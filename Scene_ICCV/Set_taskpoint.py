"""
这个模块的作用是设计接管游戏任务的起点和终点，方便之后接管过程的统一
就是画箭头，箭头参数在下面函数里有，这个箭头自己会消除的
"""


import carla


def draw_arrow_example(world,start_location,end_location,life_time = 180):

    debug = world.debug


    # 设置箭头参数
    thickness = 0.3
    arrow_size = 0.3
    arrow_color = carla.Color(255, 0, 0, 0)  # 红色
    life_time = 180.0  # 秒钟
    persistent_lines = False  # 非永久线条

    # 绘制箭头
    debug.draw_arrow(start_location, end_location, thickness, arrow_size, arrow_color, life_time, persistent_lines)

