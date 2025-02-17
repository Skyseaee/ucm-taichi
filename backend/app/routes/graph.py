from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import numpy as np
from app.models import Graph, db
from app.utils.graph_parser import pipeline_read_data
import uuid
import datetime

graph_bp = Blueprint('graph', __name__)

def adjacency_to_edges(matrix):
    edges = []
    rows, cols = matrix.shape

    for u in range(rows):
        for v in range(u + 1, cols):  # 避免重复遍历
            p = matrix[u, v]
            if p > 0:  # 仅保留存在的边
                edges.append((u, v, p))
    
    return edges

def edges_to_adjacency(edges, size):
    # 初始化一个 size x size 的零矩阵
    matrix = np.zeros((size, size), dtype=float)

    # 填充边的概率值
    for u, v, p in edges:
        matrix[u, v] = p
        matrix[v, u] = p  # 确保矩阵是对称的

    return matrix


@graph_bp.route('/upload', methods=['POST'])
@login_required
def upload_graph():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        # 解析文件内容
        edges = adjacency_to_edges(pipeline_read_data(file.stream))
        
        # 保存到数据库
        new_graph = Graph(
            user_id=current_user.id,
            filename=f"{uuid.uuid4()}.graph",
            data='\n'.join([f"{u},{v},{p}" for u, v, p in edges]),
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(new_graph)
        db.session.commit()

        return jsonify({
            'message': 'Graph uploaded successfully',
            'graph_id': new_graph.id,
            'edge_count': len(edges)
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500

@graph_bp.route('/list', methods=['GET'])
@login_required
def list_graphs():
    graphs = Graph.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': g.id,
        'filename': g.filename,
        'timestamp': g.timestamp.isoformat(),
        'edge_count': len(g.data.split('\n')) if g.data else 0
    } for g in graphs])

@graph_bp.route('/<int:graph_id>', methods=['GET'])
@login_required
def get_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    if graph.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    edges = []
    if graph.data:
        edges = [line.split(',') for line in graph.data.split('\n')]
    
    return jsonify({
        'id': graph.id,
        'data': {
            'nodes': list({e[0] for e in edges} | {e[1] for e in edges}),
            'edges': edges
        }
    })

@graph_bp.route('/<int:graph_id>', methods=['DELETE'])
@login_required
def delete_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    if graph.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    db.session.delete(graph)
    db.session.commit()
    return jsonify({'message': 'Graph deleted successfully'})