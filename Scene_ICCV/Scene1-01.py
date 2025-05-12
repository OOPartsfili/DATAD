from vehicle_method import *
from config01 import*
import Set_sensor
import Set_request
import Set_taskpoint
import Set_info
import time

"""


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
                    self.info.save_info()
                    client.stop_recorder()
                    print('stop recorder')
                    pygame.quit()
                    self.Process_flag = False
                    os._exit(0)


if __name__ == '__main__':
    destroy_all_vehicles_traffics()
    log_filename = 'Scene_1_01'
    carla_data_filename = 'carla_data/Scene_1_01'

    threading.Thread(target=pedal_receiver).start()
    threading.Thread(target=parse_euler, daemon=True).start()

    # 主车、路障车坐标在config中

    # 获取副车的位置
    Car1 = env_map.get_waypoint(main_vehicle_location).get_left_lane().next(3)[0].transform.location
    Car2 = env_map.get_waypoint(main_vehicle_location).get_left_lane().next(25)[0].transform.location
    Car3 = env_map.get_waypoint(main_vehicle_location).next(30)[0].transform.location
    Car4 = env_map.get_waypoint(main_vehicle_location).get_right_lane().next(5)[0].transform.location
    Car5 = env_map.get_waypoint(main_vehicle_location).get_right_lane().next(30)[0].transform.location

    # 生成副车
    V_Car1 = create_actor(Car1, model="vehicle.audi.tt")
    V_Car2 = create_actor(Car2, model="vehicle.audi.tt")
    V_Car3 = create_actor(Car3, model="vehicle.audi.tt")
    V_Car4 = create_actor(Car4, model="vehicle.audi.tt")
    V_Car5 = create_actor(Car5, model="vehicle.kawasaki.ninja")

    # 主车生成
    main_vehicle = create_actor(main_vehicle_location)

    time_now = str(int(time.time()))
    file_name1 = carla_data_filename + '_' + time_now + '.csv'

    # 信息收集
    info = Set_info.Info(dict_index,Set_info.dict_0,file_name1)
    info.car_list =  [main_vehicle,V_Car1,V_Car2,V_Car3,V_Car4,V_Car5]
    info.get_info()

    # 主车窗口
    Window(main_vehicle, world, info)
    # 配置碰撞传感器
    collision_sensor = world.spawn_actor(blueprint_library.find('sensor.other.collision'),
                                         carla.Transform(carla.Location(x=1.0, z=2.5)), attach_to=main_vehicle)
    def on_collision(event):
        other_actor = event.other_actor
        if 'vehicle' in other_actor.type_id:
            info.Collision_flag = other_actor.id
    collision_sensor.listen(on_collision)  # 监听碰撞事件


    # 主车初始化控制
    vehicle_control = Vehicle_Control(main_vehicle)
    vehicle_control.autopilot_speed_limit = 50.01
    vehicle_control.follow_lane()

    # 副车初始化控制
    vice_control1 = Ramp_Vice_Control(V_Car1)
    vice_control1.speed_limit = 50
    vice_control1.follow_road()

    vice_control2 = Ramp_Vice_Control(V_Car2)
    vice_control2.speed_limit = 50
    vice_control2.follow_road()

    vice_control3 = Ramp_Vice_Control(V_Car3)
    vice_control3.speed_limit = 50
    vice_control3.follow_road()

    vice_control4 = Ramp_Vice_Control(V_Car4)
    vice_control4.speed_limit = 50
    vice_control4.follow_road()

    vice_control5 = Ramp_Vice_Control(V_Car5)
    vice_control5.speed_limit = 50
    vice_control5.follow_road()


    # 标志位，用于表示是否按下了'e'键
    e_key_pressed = False
    # 键盘事件监听函数
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


    # 主车行驶300米后突发事故
    while main_vehicle.get_location().distance(TOR_location) > 50:
        sleep(0.01)






    # 进入接管状态
    while main_vehicle.get_location().x < TOR_location.x:
        sleep(0.01)



    Set_request.Video_requset()

    client.start_recorder(fr"E:\Scene_package\Scene_AAP\log_data\{log_filename}_{time_now}.log")
    info.TOR_flag = 1

    print('start_recorder')
    print("请接管")





    # 4、5车加速
    vice_control5.speed_limit = 53
    vice_control4.speed_limit = 51



    vice_control1 .speed_limit = 55
    vice_control1 .right_left_lane(direction="right", line_number=1)
    vice_control1 .speed_limit = 47


    # 绘制接管用箭头
    # Set_taskpoint.draw_arrow_example(world, start_location, end_location)

    while main_vehicle.get_location().x < start_location.x:
        sleep(0.01)

    pygame.event.post(pygame.event.Event(pygame.QUIT))

    # while True:
    #     sleep(1)
