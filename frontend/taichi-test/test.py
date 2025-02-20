from colorsys import hls_to_rgb
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
node_size = 12  # 增大节点尺寸
line_width = 2

# 将节点位置转换为 numpy 数组
node_positions = np.array([
    (0.5 + radius * math.cos(2 * math.pi * i / nodes),
     0.5 + radius * math.sin(2 * math.pi * i / nodes))
    for i in range(nodes)
], dtype=np.float32)

gui = ti.GUI("Uncertain Graph", res=(800, 800), background_color=0xFFFFFF)

def get_edge_color(alpha):
    # 使用HSL颜色空间实现渐变（从红色到绿色）
    hue = (1 - alpha) * 0.3  # 控制色相范围（0.0红色 -> 0.3绿色）
    lightness = 0.4  # 控制明度
    saturation = 0.9  # 控制饱和度
    
    # 转换HSL到RGB
    r, g, b = hls_to_rgb(hue, lightness, saturation)
    
    # 转换为0-255整数值
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    
    # 保持透明度与概率相关
    a = int(alpha * 255)
    
    # 组合成Taichi颜色格式（0xRRGGBBAA）
    return (r << 24) | (g << 16) | (b << 8) | a

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
    
    # 绘制边
    for edge in edges:
        color = get_edge_color(edge["alpha"])
        gui.line(
            edge["start"], 
            edge["end"],
            color=color,
            radius=line_width
        )
    
    # 绘制节点
    gui.circles(node_positions, color=0xCC6600, radius=node_size)
    
    # 添加节点索引号
    for i, pos in enumerate(node_positions):
        gui.text(
            content=f"{i+1}",                # 显示索引数字
            pos=pos - np.array([0.02, 0]), # 微调文字位置（向右偏移）
            font_size=20,                  # 字体大小
            color=0x333                 # 白色文字
        )
    
    gui.show()