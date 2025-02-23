from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import Graph, QueryCache, db
import hashlib
import json
import time
import uuid
import threading

query_bp = Blueprint('query', __name__)

# 存储任务状态和结果的全局字典
tasks = {}
tasks_lock = threading.Lock()

def generate_cache_key(params):
    param_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(param_str.encode()).hexdigest()

def background_task(task_id, edges, k, eta, graph_id):
    """后台任务处理函数"""
    try:
        # 执行核心计算（假设 async_k_eta_core 是同步函数）
        result = async_k_eta_core(edges, k, eta)
        
        # 生成缓存键
        cache_key = generate_cache_key({
            'k': k,
            'eta': eta,
            'graph_id': graph_id
        })

        # 在应用上下文中操作数据库
        with current_app.app_context():
            # 检查缓存是否存在
            if not QueryCache.query.get(cache_key):
                new_cache = QueryCache(
                    id=cache_key,
                    result=json.dumps(result),
                    timestamp=int(time.time())
                )
                db.session.add(new_cache)
                db.session.commit()

        # 更新任务状态
        with tasks_lock:
            tasks[task_id]['status'] = 'SUCCESS'
            tasks[task_id]['result'] = result

    except Exception as e:
        # 更新任务异常状态
        with tasks_lock:
            tasks[task_id]['status'] = 'FAILED'
            tasks[task_id]['error'] = str(e)

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

    # 验证图数据权限
    graph = Graph.query.get(graph_id)
    if not graph or graph.user_id != current_user.id:
        return jsonify({'error': 'Graph not found or unauthorized'}), 404

    # 解析边数据
    edges = []
    if graph.data:
        for line in graph.data.split('\n'):
            parts = line.strip().split(',')
            if len(parts) == 3:
                u, v, p = parts
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

    # 生成唯一任务ID
    task_id = str(uuid.uuid4())

    # 记录初始任务状态
    with tasks_lock:
        tasks[task_id] = {
            'status': 'PENDING',
            'graph_id': graph_id,
            'k': k,
            'eta': eta,
            'edges': edges
        }

    # 启动后台线程
    thread = threading.Thread(
        target=background_task,
        args=(task_id, edges, k, eta, graph_id)
    )
    thread.start()

    return jsonify({
        'task_id': task_id,
        'status': 'PENDING'
    }), 202

@query_bp.route('/result/<task_id>', methods=['GET'])
@login_required
def get_result(task_id):
    if task_id == 'cached':
        return jsonify({'error': 'Invalid task ID'}), 400

    # 获取任务信息
    with tasks_lock:
        task_info = tasks.get(task_id)

    if not task_info:
        return jsonify({'error': 'Task not found'}), 404

    # 验证图数据权限
    graph = Graph.query.get(task_info['graph_id'])
    if not graph or graph.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # 返回不同状态的结果
    if task_info['status'] == 'SUCCESS':
        return jsonify({
            'status': 'COMPLETED',
            'result': task_info['result']
        })
    elif task_info['status'] == 'FAILED':
        return jsonify({
            'status': 'FAILED',
            'error': task_info.get('error', 'Unknown error')
        }), 500
    else:
        return jsonify({
            'status': 'PENDING',
            'message': 'Task is processing'
        })