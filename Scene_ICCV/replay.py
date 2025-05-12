# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 14:30:18 2024

@author: Lenovo
"""

import carla
import argparse
import numpy as np
import pygame
import time
import pandas as pd
import Set_sensor

import os



def get_main_car_id(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        return "文件夹中没有文件。"
    # 获取最新的文件
    latest_file = max(files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    main_car_id = df['main_car_id'].iloc[0]

    return main_car_id




# 输入文件夹，输出文件夹里最新创建文件的文件名
def get_latest_file(folder):
    try:
        # 获取文件夹中的所有文件
        files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if not files:
            return "文件夹中没有文件。"
        # 获取最新的文件
        latest_file = max(files, key=os.path.getctime)
        return os.path.basename(latest_file)
    except Exception as e:
        return str(e)




def main():
    # 获取LOG文件
    latest_file = get_latest_file('log_data')
    # print(f"最新的文件是：{latest_file}")

    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')

    argparser.add_argument(
        '-s', '--start',
        metavar='S',
        default=0.0,
        type=float,
        help='starting time (default: 0.0)')
    argparser.add_argument(
        '-d', '--duration',
        metavar='D',
        default=0.0,
        type=float,
        help='duration (default: 0.0)')

    argparser.add_argument(
        '-f', '--recorder-filename',
        metavar='F',
        default=fr'E:\Scene_package\Scene_TRB\TRB\log_data\{latest_file}',
        help='recorder filename (test1.log)')

    argparser.add_argument(
        '-c', '--camera',
        metavar='C',
        default=0,
        type=int,
        help='camera follows an actor (ex: 82)')

    argparser.add_argument(
        '-x', '--time-factor',
        metavar='X',
        default=0.8,
        type=float,
        help='time factor (default 1.0)')

    argparser.add_argument(
        '-i', '--ignore-hero',
        action='store_true',
        help='ignore hero vehicles')

    argparser.add_argument(
        '--move-spectator',
        action='store_true',
        help='move spectator camera')

    argparser.add_argument(
        '--spawn-sensors',
        action='store_true',
        help='spawn sensors in the replayed world')

    args = argparser.parse_args()

    try:

        client = carla.Client(args.host, args.port)
        client.set_timeout(10.0)

        # set the time factor for the replayer设置播放器的时间因子
        client.set_replayer_time_factor(args.time_factor)

        # set to ignore the hero vehicles or not设置是否忽略英雄车辆
        client.set_replayer_ignore_hero(args.ignore_hero)

        # set to ignore the spectator camera or not
        client.set_replayer_ignore_spectator(not args.move_spectator)

        # replay the session
        # client.replay_file(args.recorder_filename, args.start, args.duration, args.camera, args.spawn_sensors)
        print(client.replay_file(args.recorder_filename, args.start, args.duration, args.camera, args.spawn_sensors))

        world = client.get_world()

        # 寻找主车
        vehicles = world.get_actors().filter('vehicle.*')
        print(vehicles)

        main_car_id = get_main_car_id('carla_data')
        vehicle = vehicles.find(int(main_car_id))

        # 初始化pygame
        pygame.init()
        pygame.font.init()

        #pygame_display = pygame.display.set_mode([800, 600], pygame.HWSURFACE | pygame.DOUBLEBUF)
        # rgb_camera = world.try_spawn_actor(rgb_camera_bp, rgb_camera_tf, attach_to=ego_vehicle)

        display_manager = Set_sensor.DisplayManager(grid_size=[1, 3], window_size=[5740, 1010])

        # 前景
        Set_sensor.SensorManager(world, display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=2, y=-0.18, z=1.3), carla.Rotation(yaw=+00)),
                                 vehicle, {'fov': '160'}, display_pos=[0, 1], Sp_flag=[[0, 0], [5740, 1010]])
        # 左后视镜
        Set_sensor.SensorManager(world, display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=1.5, y=-1, z=1.1), carla.Rotation(yaw=-140)),
                                 vehicle, {}, display_pos=[0, 0], Sp_flag=[[700, 570], [670, 430]])
        # 右后视镜
        Set_sensor.SensorManager(world, display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=1.5, y=1, z=1.1), carla.Rotation(yaw=+140)),
                                 vehicle, {}, display_pos=[0, 2], Sp_flag=[[4719, 560], [670, 430]])
        # 正后视镜
        Set_sensor.SensorManager(world, display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=-2.2, y=0, z=1.35), carla.Rotation(yaw=+180)),
                                 vehicle, {'fov': '120'}, display_pos=[1, 1], Sp_flag=[[2890, 210], [650, 190]])

        # 设置刷新帧率
        clock = pygame.time.Clock()
        fps = 60

        running = True1
        while running:
            # pygame
            # pygame渲染刷新
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # end of own scripts

            # Render received data
            display_manager.render()
            clock.tick(fps)
    finally:
        # 如果display_manager还存在，就将其摧毁
        pass


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
