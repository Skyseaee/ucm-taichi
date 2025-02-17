import taichi as ti
import requests
import hashlib
import json

ti.init(arch=ti.opengl)

class GraphVisualizer:
    def __init__(self):
        self.window = ti.ui.Window("(k, η)-core Visualization", (1280, 720))
        self.canvas = self.window.get_canvas()
        self.node_positions = {}
        self.highlight_nodes = set()
        
    def layout_nodes(self, nodes):
        """简单圆形布局"""
        n = len(nodes)
        for i, node in enumerate(nodes):
            angle = 2 * 3.1415926 * i / n
            self.node_positions[node] = (0.5 + 0.4 * ti.cos(angle), 
                                       0.5 + 0.4 * ti.sin(angle))
            
    def draw_graph(self, edges, highlight):
        """绘制图形"""
        self.canvas.set_background_color((1, 1, 1))
        
        # 绘制边
        for u, v, _ in edges:
            if u in self.node_positions and v in self.node_positions:
                u_pos = self.node_positions[u]
                v_pos = self.node_positions[v]
                self.canvas.line(u_pos, v_pos, color=(0.7, 0.7, 0.7), width=1)
        
        # 绘制节点
        for node, pos in self.node_positions.items():
            color = (1, 0, 0) if node in highlight else (0, 0.5, 1)
            self.canvas.circle(pos, color=color, radius=0.02)

def main():
    vis = GraphVisualizer()
    
    # 从后端获取图数据
    response = requests.get("http://localhost:5000/api/graph/1")
    graph_data = json.loads(response.json()['data'])
    
    # 解析数据
    nodes = set()
    edges = []
    for line in graph_data.strip().split('\n'):
        u, v, p = map(float, line.split(','))
        nodes.update([int(u), int(v)])
        edges.append((int(u), int(v), p))
    
    vis.layout_nodes(nodes)
    
    # 主循环
    while vis.window.running:
        # 处理输入
        if vis.window.get_event(ti.ui.PRESS):
            if vis.window.event.key == ti.ui.ENTER:
                # 执行查询
                k = 2  # 从GUI获取实际值
                eta = 0.5
                response = requests.post(
                    "http://localhost:5000/api/query",
                    json={"k": k, "eta": eta, "graph_id": 1}
                )
                vis.highlight_nodes = set(json.loads(response.json()['result']))
        
        # 绘制图形
        vis.draw_graph(edges, vis.highlight_nodes)
        vis.window.show()

if __name__ == "__main__":
    main()