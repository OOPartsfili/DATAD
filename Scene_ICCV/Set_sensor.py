# -*- coding: utf-8 -*-
"""
该模块的作用是设置传感器和自定义pygame渲染图像
在55行附近需要调节前景图片路径

更新列表

重写render函数，需要自己改动png图片路径，从而稳定渲染出图片
新增获取窗口函数，为get_display
重大BUG修复，画面水平翻转，解决方法是让广角为120的摄像头都水平翻转，因此要慎用fov

"""

import glob
import os
import sys

import carla
import argparse
import random
import time
import numpy as np
import pygame


class CustomTimer:
    def __init__(self):
        try:
            self.timer = time.perf_counter
        except AttributeError:
            self.timer = time.time

    def time(self):
        return self.timer()


# 输入 grid_size逻辑格[2,3]代表2行3列, window_size窗口大小这里1280X720
class DisplayManager:
    def __init__(self, grid_size, window_size):
        pygame.init()
        pygame.font.init()
        # 显示屏设置，这里是整个屏的大小
        self.display = pygame.display.set_mode(window_size, pygame.HWSURFACE | pygame.DOUBLEBUF)

        # 逻辑格大小
        self.grid_size = grid_size

        # 窗口大小，这个也是整个屏大小
        self.window_size = window_size

        # 初始化传感器列表
        self.sensor_list = []

        # 读取前景图片
        image_path = 'asset/123.png'  # 确保这个路径指向你的PNG图片
        self.transparent_image = pygame.image.load(image_path).convert_alpha()


    # 获取显示屏
    def get_display(self):
        return self.display

    # 获取当前窗口大小
    # 输出[x,y]尺寸
    def get_window_size(self):
        return [int(self.window_size[0]), int(self.window_size[1])]

    # 实际显示大小，这里self.window_size[0]/self.grid_size[1]是算出小屏的尺寸
    # 输出小屏的尺寸[x,y]
    def get_display_size(self):
        return [int(self.window_size[0] / self.grid_size[1]), int(self.window_size[1] / self.grid_size[0])]

    # gridPos=[1, 0]，代表小屏的位置坐标
    # 输入位置坐标，输出一个小屏左上角起点坐标,如果有特殊位置就按特殊位置设置
    def get_display_offset(self, gridPos):
        dis_size = self.get_display_size()  # 这里得到的是小屏的尺寸
        x0 = int(gridPos[1] * dis_size[0])
        y0 = int(gridPos[0] * dis_size[1])

        return [x0, y0]

    # 输入一个传感器，结果是DisplayManager里增加一个传感器
    def add_sensor(self, sensor):
        self.sensor_list.append(sensor)

    # 获取传感器列表
    def get_sensor_list(self):
        return self.sensor_list


    def render(self):
        # 渲染没有打开，就返回空值,然后啥也不做
        if not self.render_enabled():
            return
        # s就是传感器
        for s in self.sensor_list:
            # 激发传感器渲染图像
            s.render()

        # 将具有透明度的图片渲染到窗口上
        self.display.blit(self.transparent_image, (400, 0))  # 你可以调整位置

        # 更新屏幕显示
        pygame.display.flip()





    #   清除传感器
    def destroy(self):
        for s in self.sensor_list:
            s.destroy()

    # 输出一个布尔值，display为none时，为False，表示别传感器渲染
    def render_enabled(self):
        return self.display != None


# 传感器控制器
# 输入世界、显示器、显示器位置、以及一个sensor生成的基本信息
class SensorManager:
    def __init__(self, world, display_man, sensor_type, transform, attached, sensor_options, display_pos, Sp_flag):
        # 代表是否为特殊位置的旗子，如果为[],则不是，如果为[[300,400],[500,600]]，则代表有特殊位置
        # 先是插入位置，再是屏幕大小
        self.Sp_flag = Sp_flag

        self.surface = None
        self.world = world
        self.display_man = display_man
        self.display_pos = display_pos

        self.sensor = self.init_sensor(sensor_type, transform, attached, sensor_options)
        self.sensor_options = sensor_options
        self.timer = CustomTimer()

        self.display_man.add_sensor(self)

    def init_sensor(self, sensor_type, transform, attached, sensor_options):
        if sensor_type == 'RGBCamera':
            camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
            Sp_flag = self.Sp_flag

            if Sp_flag == []:
                disp_size = self.display_man.get_display_size()
            # 如果为[[x,y],[w,h]]，则代表有特殊位置
            else:
                disp_size = Sp_flag[1]
            # 取出蓝图后，调整蓝图里的参数（小屏大小）
            camera_bp.set_attribute('image_size_x', str(disp_size[0]))
            camera_bp.set_attribute('image_size_y', str(disp_size[1]))


            for key in sensor_options:
                camera_bp.set_attribute(key, sensor_options[key])

            camera = self.world.spawn_actor(camera_bp, transform, attach_to=attached)
            camera.listen(self.save_rgb_image)

            return camera

        if sensor_type == 'SS':
            camera_bp = self.world.get_blueprint_library().find('sensor.camera.semantic_segmentation')
            Sp_flag = self.Sp_flag
            if Sp_flag == []:
                disp_size = self.display_man.get_display_size()
            # 如果为[[x,y],[w,h]]，则代表有特殊位置
            else:
                disp_size = Sp_flag[1]
            camera_bp.set_attribute('image_size_x', str(disp_size[0]))
            camera_bp.set_attribute('image_size_y', str(disp_size[1]))

            for key in sensor_options:
                camera_bp.set_attribute(key, sensor_options[key])

            camera = self.world.spawn_actor(camera_bp, transform, attach_to=attached)
            camera.listen(self.save_SS_image)
            return camera

        if sensor_type == 'IS':
            camera_bp = self.world.get_blueprint_library().find('sensor.camera.instance_segmentation')
            Sp_flag = self.Sp_flag
            if Sp_flag == []:
                disp_size = self.display_man.get_display_size()
            # 如果为[[x,y],[w,h]]，则代表有特殊位置
            else:
                disp_size = Sp_flag[1]
            camera_bp.set_attribute('image_size_x', str(disp_size[0]))
            camera_bp.set_attribute('image_size_y', str(disp_size[1]))

            for key in sensor_options:
                camera_bp.set_attribute(key, sensor_options[key])

            camera = self.world.spawn_actor(camera_bp, transform, attach_to=attached)
            camera.listen(self.save_IS_image)
            return camera


        else:
            return None

    def get_sensor(self):
        return self.sensor

    # 保存RGB图像
    def save_rgb_image(self, image):
        image.convert(carla.ColorConverter.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        # 如果视场角度为120度，对图像进行水平翻转
        try:
            if self.sensor_options['fov'] == '120':
                array = np.fliplr(array)
        except KeyError:
            pass
        # 根据渲染是否启用，将图像数据转换为 Pygame 的 Surface 对象，
        # 以便后续的渲染和显示操作。这样可以将图像数据在 Pygame 窗口中显示出来
        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

    def save_SS_image(self, image):
        image.convert(carla.ColorConverter.CityScapesPalette)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        # 根据渲染是否启用，将图像数据转换为 Pygame 的 Surface 对象，
        # 以便后续的渲染和显示操作。这样可以将图像数据在 Pygame 窗口中显示出来
        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

    def save_IS_image(self, image):
        image.convert(carla.ColorConverter.Raw)
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        # 根据渲染是否启用，将图像数据转换为 Pygame 的 Surface 对象，
        # 以便后续的渲染和显示操作。这样可以将图像数据在 Pygame 窗口中显示出来
        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

    # 渲染到pygame上
    def render(self):
        if self.surface is not None:
            if self.Sp_flag == []:
                offset = self.display_man.get_display_offset(self.display_pos)
            else:
                offset = self.Sp_flag[0]
            self.display_man.display.blit(self.surface, offset)

    def destroy(self):
        self.sensor.destroy()


def run_simulation(args, client):
    """This function performed one test run using the args parameters
    and connecting to the carla client passed.
    """
    # 初始化场景
    display_manager = None
    vehicle = None
    vehicle_list = []
    timer = CustomTimer()

    try:
        # 获取世界对象和基本设置
        world = client.get_world()
        original_settings = world.get_settings()

        if args.sync:  # 如果有输入的参数
            # 创建一个与Carla服务器交互的TrafficManager对象，并将其连接到本地主机的8000端口。
            traffic_manager = client.get_trafficmanager(8000)
            settings = world.get_settings()
            # 在异步模式下，模拟器的不同组件可以并行执行，每个组件根据其自己的时间步长进行更新。
            # 您可能需要将模拟器设置为同步模式，以便所有组件在每个时间步骤中以固定的顺序和时间间隔进行更新。
            traffic_manager.set_synchronous_mode(True)
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05
            world.apply_settings(settings)

        # 实例化我们安装传感器的车辆
        bp = world.get_blueprint_library().filter('model3')[0]

        # 随机选一个出生点来生成车辆
        vehicle = world.spawn_actor(bp, random.choice(world.get_map().get_spawn_points()))
        # 加入车库
        vehicle_list.append(vehicle)
        # 之前那辆车开启自动驾驶
        vehicle.set_autopilot(True)

        # 显示管理器在一个窗口中组织所有传感器及其显示
        # 它可以很容易地配置网格和总窗口大小
        display_manager = DisplayManager(grid_size=[1, 3], window_size=[args.width, args.height])

        clock = pygame.time.Clock()


        # 前景
        SensorManager(world, display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=2, y=-0.18, z=1.3), carla.Rotation(yaw=+00)),
                                 vehicle, {'fov': '135'}, display_pos=[0, 1], Sp_flag=[[0, 0], [5740, 1010]])
        # 左后视镜
        SensorManager(world, display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=1.5, y=-1, z=1.1), carla.Rotation(yaw=-140)),
                                 vehicle, {}, display_pos=[0, 0], Sp_flag=[[700, 570], [670, 430]])
        # 右后视镜
        SensorManager(world, display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=1.5, y=1, z=1.1), carla.Rotation(yaw=+140)),
                                 vehicle, {}, display_pos=[0, 2], Sp_flag=[[4719, 560], [670, 430]])
        # 正后视镜
        SensorManager(world, display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=-2.2, y=0, z=1.35), carla.Rotation(yaw=+180)),
                                 vehicle, {'fov': '120'}, display_pos=[1, 1], Sp_flag=[[2890, 210], [650, 190]])

        # client.start_recorder('BIG_TRY.log')
        # print(display_manager.get_sensor_list())

        # 仿真循环
        call_exit = False
        time_init_sim = timer.time()
        while True:
            # Carla Tick
            if args.sync:
                world.tick()
            else:
                world.wait_for_tick()
            # Render received data
            display_manager.render()
            clock.tick(60)
            # 这里给出了几种退出的方法（但是没有用）
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    call_exit = True
            if call_exit:
                break

    finally:
        # 如果display_manager还存在，就将其摧毁
        if display_manager:
            display_manager.destroy()
        # 摧毁所有对象Actor
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicle_list])
        # 还原世界设置
        world.apply_settings(original_settings)

        # print("Stop recording")
        # client.stop_recorder()


def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Sensor tutorial')
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
        '--sync',
        action='store_true',
        help='Synchronous mode execution')
    argparser.add_argument(
        '--async',
        dest='sync',
        action='store_false',
        help='Asynchronous mode execution')
    argparser.set_defaults(sync=True)
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='5740x1010',
        help='window resolution (default: 3600x1200)')

    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]

    try:
        client = carla.Client(args.host, args.port)
        # 设置超时时间
        client.set_timeout(5.0)

        run_simulation(args, client)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':
    main()
