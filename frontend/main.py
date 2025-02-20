# visualizer.py
import taichi as ti
import requests
import json
import os

ti.init(arch=ti.cpu)

class GraphVisualizer:
    def __init__(self):
        # 窗口和GUI初始化
        self.window = ti.ui.Window("(k, η)-core Analysis System", (1600, 900))
        self.canvas = self.window.get_canvas()
        self.gui = self.window.get_gui()
        
        # 应用状态
        self.state = {
            'logged_in': False,
            'auth_token': None,
            'graphs': [],
            'current_graph': None,
            'highlight_nodes': set(),
            'k': 2,
            'eta': 0.5
        }
        
        # UI组件
        self.ui = {
            'username': ti.ui.TextInput(label='Username'),
            'password': ti.ui.TextInput(label='Password', password=True),
            'upload_btn': ti.ui.Button("Upload"),
            'query_btn': ti.ui.Button("Run Query")
        }
        
        # 图形数据
        self.graph_data = {
            'nodes': {},
            'edges': []
        }

    def run(self):
        while self.window.running:
            self.handle_events()
            self.draw_interface()
            self.window.show()

    def handle_events(self):
        # 处理输入事件
        if self.ui['upload_btn'].clicked():
            self.handle_upload()
            
        if self.ui['query_btn'].clicked():
            self.run_query()

    def draw_interface(self):
        # 绘制侧边栏
        with self.gui.sub_window("Control Panel", 0.02, 0.02, 0.25, 0.96) as panel:
            if not self.state['logged_in']:
                self.draw_login(panel)
            else:
                self.draw_main_controls(panel)
        
        # 绘制主视图
        if self.state['current_graph']:
            self.draw_graph()

    def draw_login(self, panel):
        panel.text("Login")
        self.ui['username'].render(panel, (0.1, 0.2), (0.8, 0.1))
        self.ui['password'].render(panel, (0.1, 0.35), (0.8, 0.1))
        
        if panel.button("Login", (0.3, 0.5, 0.4, 0.1)):
            self.handle_login()

    def draw_main_controls(self, panel):
        # 文件管理
        panel.text(f"Welcome, {self.ui['username'].value}")
        if panel.button("Refresh List", (0.1, 0.1, 0.8, 0.05)):
            self.load_graphs()
            
        # 图列表
        for graph in self.state['graphs']:
            if panel.checkbox(graph['filename'], graph['id'] == self.state['current_graph']):
                self.load_graph_data(graph['id'])
                
        # 查询参数
        panel.separator()
        self.state['k'] = panel.slider_int("k Value", self.state['k'], 1, 10)
        self.state['eta'] = panel.slider_float("η Value", self.state['eta'], 0.0, 1.0)
        self.ui['query_btn'].render(panel, (0.3, 0.8, 0.4, 0.05))

    def draw_graph(self):
        # 绘制节点
        for node, pos in self.graph_data['nodes'].items():
            color = (1, 0, 0) if node in self.state['highlight_nodes'] else (0.2, 0.5, 1)
            self.canvas.circle(pos, color=color, radius=0.015)
        
        # 绘制边
        for u, v, _ in self.graph_data['edges']:
            if u in self.graph_data['nodes'] and v in self.graph_data['nodes']:
                self.canvas.line(
                    self.graph_data['nodes'][u],
                    self.graph_data['nodes'][v],
                    color=(0.8, 0.8, 0.8),
                    width=1
                )

    def handle_login(self):
        try:
            response = requests.post(
                "http://localhost:5000/api/login",
                json={
                    'username': self.ui['username'].value,
                    'password': self.ui['password'].value
                }
            )
            if response.ok:
                self.state['auth_token'] = response.json().get('token')
                self.state['logged_in'] = True
                self.load_graphs()
        except Exception as e:
            print(f"Login error: {e}")

    def load_graphs(self):
        try:
            response = requests.get(
                "http://localhost:5000/api/graphs",
                headers={'Authorization': f'Bearer {self.state["auth_token"]}'}
            )
            self.state['graphs'] = response.json()
        except Exception as e:
            print(f"Load graphs error: {e}")

    def load_graph_data(self, graph_id):
        try:
            response = requests.get(
                f"http://localhost:5000/api/graph/{graph_id}",
                headers={'Authorization': f'Bearer {self.state["auth_token"]}'}
            )
            data = response.json()
            self.graph_data['nodes'] = self.layout_nodes(data['nodes'])
            self.graph_data['edges'] = [(u, v, p) for u, v, p in data['edges']]
            self.state['current_graph'] = graph_id
        except Exception as e:
            print(f"Load graph error: {e}")

    def handle_upload(self):
        file_path = self.gui.file_dialog("Select Graph File")
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    response = requests.post(
                        "http://localhost:5000/api/upload",
                        files={'file': f},
                        headers={'Authorization': f'Bearer {self.state["auth_token"]}'}
                    )
                    if response.ok:
                        self.load_graphs()
            except Exception as e:
                print(f"Upload error: {e}")

    def run_query(self):
        try:
            response = requests.post(
                "http://localhost:5000/api/query",
                json={
                    'k': self.state['k'],
                    'eta': self.state['eta'],
                    'graph_id': self.state['current_graph']
                },
                headers={'Authorization': f'Bearer {self.state["auth_token"]}'}
            )
            if response.ok:
                self.state['highlight_nodes'] = set(response.json()['result'])
        except Exception as e:
            print(f"Query error: {e}")

    @staticmethod
    def layout_nodes(nodes):
        # 简单圆形布局
        n = len(nodes)
        return {
            node: (0.5 + 0.4 * ti.cos(2 * 3.1416 * i / n),
                   0.5 + 0.4 * ti.sin(2 * 3.1416 * i / n))
            for i, node in enumerate(nodes)
        }

if __name__ == "__main__":
    vis = GraphVisualizer()
    vis.run()