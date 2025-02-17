from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Graph, QueryCache, db
from app.tasks import async_k_eta_core
import hashlib
import json
import time

query_bp = Blueprint('query', __name__)

def generate_cache_key(params):
    param_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(param_str.encode()).hexdigest()

@query_bp.route('/submit', methods=['POST'])
@login_required
def submit_query():
    data = request.get_json()
    try:
        k = int(data['k'])
        eta = float(data['eta'])
        graph_id = int(data['graph_id'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid parameters'}), 400

    # 获取图数据
    graph = Graph.query.get(graph_id)
    if not graph or graph.user_id != current_user.id:
        return jsonify({'error': 'Graph not found or unauthorized'}), 404

    # 解析边数据
    edges = []
    if graph.data:
        for line in graph.data.split('\n'):
            u, v, p = line.strip().split(',')
            edges.append((u, v, float(p)))

    # 检查缓存
    cache_key = generate_cache_key({
        'k': k,
        'eta': eta,
        'graph_id': graph_id
    })
    cached = QueryCache.query.get(cache_key)
    
    if cached:
        return jsonify({
            'task_id': 'cached',
            'result': json.loads(cached.result),
            'status': 'COMPLETED'
        })

    # 提交异步任务
    task = async_k_eta_core.apply_async(args=(edges, k, eta))
    return jsonify({
        'task_id': task.id,
        'status': 'PENDING'
    }), 202

@query_bp.route('/result/<task_id>', methods=['GET'])
@login_required
def get_result(task_id):
    if task_id == 'cached':
        return jsonify({'error': 'Invalid task ID'}), 400

    task = async_k_eta_core.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        return jsonify({
            'status': 'PENDING',
            'message': 'Task is queued'
        })
    elif task.state == 'SUCCESS':
        # 缓存结果
        result = task.result
        cache_key = generate_cache_key({
            'k': task.args[0],
            'eta': task.args[1],
            'graph_id': request.args.get('graph_id')
        })
        
        if not QueryCache.query.get(cache_key):
            new_cache = QueryCache(
                id=cache_key,
                result=json.dumps(result),
                timestamp=time.time()
            )
            db.session.add(new_cache)
            db.session.commit()
        
        return jsonify({
            'status': 'COMPLETED',
            'result': result
        })
    else:
        return jsonify({
            'status': 'FAILED',
            'error': str(task.info)
        }), 500