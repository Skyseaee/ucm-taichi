import os
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import numpy as np
from app.models import Graph, db
from app.utils.graph_parser import pipeline_read_data
import uuid
import datetime

graph_bp = Blueprint('graph', __name__)

# 确保上传目录存在
def get_upload_folder():
    """
    返回存放图数据的上传目录，并确保该目录存在
    """
    # 使用 current_app 获取当前应用实例的 instance_path
    upload_folder = os.path.join(current_app.instance_path, 'graphs')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder

def save_graph_file(data_stream, filename):
    """将图数据保存到文件"""
    filepath = os.path.join(get_upload_folder(), filename)
    # 先解析验证数据
    matrix = pipeline_read_data(data_stream)
    edges = adjacency_to_edges(matrix)
    # 保存到文件
    with open(filepath, 'w') as f:
        for u, v, p in edges:
            f.write(f"{u},{v},{p}\n")
    return len(edges)

def load_graph_file(filename):
    """从文件加载图数据"""
    filepath = os.path.join(get_upload_folder(), filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return [line.strip().split(',') for line in f.readlines()]

def delete_graph_file(filename):
    """删除图文件"""
    filepath = os.path.join(get_upload_folder(), filename)
    if os.path.exists(filepath):
        os.remove(filepath)

def adjacency_to_edges(matrix):
    edges = []
    rows, cols = matrix.shape
    for u in range(rows):
        for v in range(u + 1, cols):
            p = matrix[u, v]
            if p > 0:
                edges.append((u, v, p))
    return edges

def edges_to_adjacency(edges, size):
    matrix = np.zeros((size, size), dtype=float)
    for u, v, p in edges:
        matrix[u, v] = p
        matrix[v, u] = p
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
        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}.graph"
        # 保存文件并获取边数
        edge_count = save_graph_file(file.stream, filename)
        
        # 保存到数据库
        new_graph = Graph(
            user_id=current_user.id,
            filename=filename,
            data=filename,  # 现在存储文件名
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(new_graph)
        db.session.commit()

        return jsonify({
            'message': 'Graph uploaded successfully',
            'graph_id': new_graph.id,
            'edge_count': edge_count
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        # app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@graph_bp.route('/list', methods=['GET'])
@login_required
def list_graphs():
    graphs = Graph.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': g.id,
        'filename': g.filename,
        'timestamp': g.timestamp.isoformat(),
        'edge_count': len(load_graph_file(g.data))  # 从文件获取边数
    } for g in graphs])

@graph_bp.route('/<int:graph_id>', methods=['GET'])
@login_required
def get_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    if graph.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    edges = load_graph_file(graph.data)
    nodes = set()
    for e in edges:
        nodes.update(e[:2])
    
    return jsonify({
        'id': graph.id,
        'data': {
            'nodes': sorted(nodes, key=int),
            'edges': edges
        }
    })

@graph_bp.route('/<int:graph_id>', methods=['DELETE'])
@login_required
def delete_graph(graph_id):
    graph = Graph.query.get_or_404(graph_id)
    if graph.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        # 先删除文件
        delete_graph_file(graph.data)
        # 再删除数据库记录
        db.session.delete(graph)
        db.session.commit()
        return jsonify({'message': 'Graph deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete error: {str(e)}")
        return jsonify({'error': 'Failed to delete graph'}), 500