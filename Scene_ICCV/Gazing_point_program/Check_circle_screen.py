"""
这个脚本用来实时检测驾驶员注视点的精度

"""

import socket
import json
import csv
import os
import pandas as pd
import pygame
import sys


# 定义处理函数
def process_point(data):
    # 提取ObjectPoint的x、y坐标
    object_point = data['ObjectPoint']
    x, y = object_point['x'], object_point['y']

    # 根据ObjectName进行调整
    x_int = int(x * 5740)
    y_int = 1010 - int(y * 1010)
    # 返回结果
    return [x_int,y_int]



# 配置接收数据的 IP 和端口
RECEIVER_IP = "0.0.0.0"
RECEIVER_PORT = 1999

# 配置保存 CSV 文件的路径
CSV_FILE_PATH = r'received_data.csv'

def main():
    # 创建 UDP 套接字
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((RECEIVER_IP, RECEIVER_PORT))
        print(f"Listening on {RECEIVER_IP}:{RECEIVER_PORT}")

        # 初始化Pygame
        pygame.init()

        running = True

        # 设置窗口尺寸
        window_width = 5760
        window_height = 1010
        window_size = (window_width, window_height)
        window = pygame.display.set_mode(window_size)
        pygame.display.set_caption("动态显示点")

        # 颜色定义
        white = (255, 255, 255)
        black = (0, 0, 0)

        # 点列表
        points = []

        # 限制点的数量为15
        max_points = 15

        # 函数：添加新的点
        def add_point(x, y):
            # 检查坐标是否超出窗口尺寸
            if x < 0:
                x = 0
            elif x > window_width:
                x = window_width
            if y < 0:
                y = 0
            elif y > window_height:
                y = window_height

            # 添加新点到列表
            points.append((x, y))

            # 保证列表中最多有15个点
            if len(points) > max_points:
                points.pop(0)

        while running:
            # 接收数据
            data, addr = sock.recvfrom(10024)
            decoded_data = data.decode('utf-8')
            json_data = json.loads(decoded_data)
            try:
                input_data = json_data['FilteredClosestWorldIntersection']
            except KeyError:
                input_data = {'WorldPoint': {'x': 0, 'y': 0, 'z': 0},'ObjectPoint': {'x': 0, 'y': 0, 'z': 0},'ObjectName': 'ScreenMiddle'}

            output_coordinates = process_point(input_data)
            print(output_coordinates)

            # 主循环

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # 示例输入坐标
                # 你可以将下面的坐标换成你的动态输入
            add_point(output_coordinates[0],output_coordinates[1])  # 示例：添加一个点 (900, 900)

            # 绘制点
            for point in points:
                pygame.draw.circle(window, white, point, 50)

                # 更新显示
            pygame.display.flip()

                # 模拟延迟，便于观察效果
            pygame.time.wait(10)

            # 退出Pygame
        pygame.quit()
        sys.exit()




if __name__ == "__main__":
    main()
