import taichi as ti
import math
import numpy as np

ti.init(arch=ti.opengl)

# 原始图数据保持不变
graph = [
    [.0, .5, .2, .0, .0, .0, .0, .0, .0, .0],
    [.5, .0, .8, .2, .6, .0, .0, .0, .0, .0],
    [.2, .8, .0, .5, .8, .0, .0, .0, .0, .0],
    [.0, .2, .5, .0, .4, .0, .0, .0, .0, .0],
    [.0, .6, .8, .4, .0, .2, .0, .0, .0, .0],
    [.0, .0, .0, .0, .2, .0, .5, .0, .0, .0],
    [.0, .0, .0, .0, .0, .5, .0, .8, .5, .8],
    [.0, .0, .0, .0, .0, .0, .8, .0, .0, .0],
    [.0, .0, .0, .0, .0, .0, .5, .0, .0, .8],
    [.0, .0, .0, .0, .0, .0, .8, .0, .8, .0],
]

nodes = len(graph)
radius = 0.4
node_size = 8
line_width = 2

# 将节点位置转换为 numpy 数组
node_positions = np.array([
    (0.5 + radius * math.cos(2 * math.pi * i / nodes),
     0.5 + radius * math.sin(2 * math.pi * i / nodes))
    for i in range(nodes)
], dtype=np.float32)

gui = ti.GUI("Uncertain Graph", res=(800, 800), background_color=0x000000)

# 预计算所有边数据
edges = []
for i in range(nodes):
    for j in range(i+1, nodes):
        if graph[i][j] > 0:
            edges.append({
                "start": node_positions[i],
                "end": node_positions[j],
                "alpha": graph[i][j]
            })

while gui.running:
    gui.clear()
    
    # 批量绘制边（使用RGBA十六进制格式）
    for edge in edges:
        color = 0xFFFFFF + (int(edge["alpha"] * 255) << 24)
        gui.line(
            edge["start"], 
            edge["end"],
            color=color,
            radius=line_width
        )
    
    # 绘制节点（使用预计算的位置）
    gui.circles(node_positions, color=0xFFA500, radius=node_size)
    
    gui.show()