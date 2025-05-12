from vehicle_method import *
from config01 import*
import Set_sensor
import Set_request
import Set_taskpoint
import Set_info
import time

"""
更新版本

新增车内图片、语言接管提示
q
"""

# 新的页面窗口
class Window:
    def __init__(self, vehicle, world, info):
        self.world = world
        self.vehicle = vehicle
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 5740, 1010  # 屏幕大小
        self.clock = pygame.time.Clock()
        self.fps = 60  # 帧率
        self.info = info
        self.Process_flag = True

        self.Process = threading.Thread(target=self.show_screen)
        self.Process.start()

    def show_screen(self):  # 显示窗口
        # 创建窗口
        self.display_manager = Set_sensor.DisplayManager(grid_size=[1, 3],
                                                         window_size=[self.SCREEN_WIDTH, self.SCREEN_HEIGHT])

        # 前景
        Set_sensor.SensorManager(world, self.display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=2, y=-0.18, z=1.3), carla.Rotation(yaw=+00)),
                                 self.vehicle, {'fov': '160'}, display_pos=[0, 1], Sp_flag=[[0, 0], [5740, 1010]])
        # 左后视镜
        Set_sensor.SensorManager(world, self.display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=1.5, y=-1, z=1.1), carla.Rotation(yaw=-140)),
                                 self.vehicle, {}, display_pos=[0, 0], Sp_flag=[[700, 430], [670, 390]])
        # 右后视镜
        Set_sensor.SensorManager(world, self.display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=1.5, y=1, z=1.1), carla.Rotation(yaw=+140)),
                                 self.vehicle, {}, display_pos=[0, 2], Sp_flag=[[4719, 420], [670, 385]])
        # 正后视镜
        Set_sensor.SensorManager(world, self.display_manager, 'RGBCamera',
                                 carla.Transform(carla.Location(x=-2.2, y=0, z=1.35), carla.Rotation(yaw=+180)),
                                 self.vehicle, {'fov': '120'}, display_pos=[1, 1], Sp_flag=[[2890, 210], [650, 190]])

        while self.Process_flag:
            # screen.fill((0, 0, 0))  # 使用黑色清除屏幕
            self.display_manager.render()

            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # 窗口关闭
                    # self.info.save_info()
                    # client.stop_recorder()
                    # print('stop recorder')
                    pygame.quit()
                    self.Process_flag = False
                    os._exit(0)


if __name__ == '__main__':
    destroy_all_vehicles_traffics()

    threading.Thread(target=pedal_receiver).start()
    threading.Thread(target=parse_euler, daemon=True).start()

    # 主车生成
    main_vehicle = create_actor(main_vehicle_location)
    # 主车前半段自动驾驶控制
    vehicle_control = Vehicle_Control(main_vehicle)  # 主车控制
    vehicle_control.autopilot_speed_limit = 30
    vehicle_control.follow_lane()


    # 标志位，用于表示是否按下了'e'键
    e_key_pressed = False


    def listen_for_e_key():
        global e_key_pressed, info
        while 1:
            steerCmd, acc, brake = get_sensor_data()
            print(brake)
            if brake > 0.5:
                e_key_pressed = True
                info.Handchange_flag = 1
                vehicle_control.autopilot_flag = False
                print("切换成功！")
                break
            time.sleep(0.005)  # 防止CPU占用过高


    listener_thread = threading.Thread(target=listen_for_e_key)
    listener_thread.start()

    # 信息收集
    info = Set_info.Info(dict_index, Set_info.dict_0, file_name1)
    # info.car_list = [main_vehicle] + vice_vehicles1 + [vice_vehicles2[0]] + [V_Car5] + vice_vehicles2[1:] + [V_Car9]

    # 主车窗口
    Window(main_vehicle, world, info)

