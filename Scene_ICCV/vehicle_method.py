import carla

from disposition import *

from sensor.steering_angle import parse_euler, get_steering_angle
from sensor.pedal import get_data,pedal_receiver

# 添加一个全局变量来存储上一次的传感器数据
last_sensor_data = {
    'steer': 0,
    'throttle': 0,
    'brake': 0
}


def get_sensor_data():
    K1 = 0.25
    steer = get_steering_angle() / 450
    steerCmd = K1 * math.tan(1.1 * steer)
    acc,brake = get_data()
    brake *= 2
    if brake > 1:
        brake = 1
    if acc > 0.2:
        brake =0
    return  steerCmd, acc, brake



# 主车控制
class Vehicle_Control:
    def __init__(self, vehicle):
        self.vehicle = vehicle  # 车子对象
        self.autopilot_flag = True  # 是否自动驾驶，默认沿着当前道路，没有路了就停止，为False可用方向盘驾驶
        self.lose_control = False  # 这个是有控制权，为True是失去所有控制
        self.autopilot_speed_limit = 100  # 自动驾驶速度限制
        self.labour_speed_limit = 140  # 人工驾驶速度限制
        self.driver_status = "自动驾驶"
        self.instantaneous_speed = True

    def follow_lane(self):
        pid = VehiclePIDController(self.vehicle, args_lateral=args_lateral_dict, args_longitudinal=args_long_dict)

        def control():
            # break_frame = 0 #踩刹车的累计帧

            while True:
                if self.lose_control:  # 判断有没有失去控制
                    self.driver_status = "没有控制"
                    pass
                elif self.autopilot_flag:
                    self.driver_status = "自动驾驶"
                    self.autopilot_flag = not keyboard.is_pressed("q")
                    # 自动驾驶车辆，瞬时速度
                    if self.instantaneous_speed:
                        if get_speed(self.vehicle) < self.autopilot_speed_limit:
                            set_speed(self.vehicle, self.autopilot_speed_limit)

                    waypoint = env_map.get_waypoint(self.vehicle.get_location()).next(max(1, int(get_speed(self.vehicle) / 6)))
                    if waypoint:
                        waypoint = waypoint[0]
                    else:
                        print(f"前方没有路了,当前车子坐标{self.vehicle.get_location()},车子对象为{self.vehicle}")
                        set_speed(self.vehicle, 0)
                        return

                    result = pid.run_step(self.autopilot_speed_limit, waypoint)
                    self.vehicle.apply_control(result)
                else:
                    self.driver_status = "人工驾驶"
                    self.autopilot_flag = keyboard.is_pressed("e")
                    # 人工控制车辆
                    steer, throttle,brake  = get_sensor_data()
                    # steer, brake, throttle = get_steering_wheel_info()
                    print(steer, throttle, brake)

                    # if brake >0.4:
                    #     break_frame += 1
                    # if break_frame >60:
                    #     velocity = carla.Vector3D(self.vehicle.get_velocity().x/5, self.vehicle.get_velocity().y/5, 0)  # 10 m/s 的速度，方向为X轴正方向
                    #     self.vehicle.set_target_velocity(velocity)
                    #     sleep(0.1)
                    #
                    #     velocity = carla.Vector3D(self.vehicle.get_velocity().x / 10,
                    #                               self.vehicle.get_velocity().y / 10, 0)  # 10 m/s 的速度，方向为X轴正方
                    #     self.vehicle.set_target_velocity(velocity)
                    #     sleep(0.05)
                    #     velocity = carla.Vector3D(0,0,0)  # 10 m/s 的速度，方向为X轴正方向
                    #     self.vehicle.set_target_velocity(velocity)
                    #
                    #     break_frame = 0

                    if get_speed(self.vehicle) > self.labour_speed_limit:  # 设置最高速度
                        throttle = 0.5
                    result = carla.VehicleControl(steer=round(steer, 3), throttle=round(throttle, 3), brake=round(brake, 3))

                    self.vehicle.apply_control(result)
                sleep(0.01)

        threading.Thread(target=control).start()

    def right_left_lane(self, direction=None, min_direction=10, method="pid", line_number=1, draw=False):
        """
        左转或右转
        :param direction: 左转还是右转,接收"left"和"right"
        :param min_direction: 最小变道距离
        :param method: 变道所使用的方法，默认用pid，还有agent
        :return:
        """
        self.lose_control = True
        # 判断有没有可变道路,得到direction方向值
        if not direction:  # 如果没有传左/右变道
            # 先判断左右是否有道路
            direction = str(env_map.get_waypoint(self.vehicle.get_location()).lane_change).lower()
            if not direction:  # 如果没有可变道路，找前方看有没有可以变道
                direction = str(env_map.get_waypoint(self.vehicle.get_location()).next(max(get_speed(self.vehicle), 5))[0].lane_change).lower()
                if not direction:
                    print("没有可变道路！！！！！！！！")
                    return
                elif direction == "both":
                    direction = random.choice(["right", "left"])
            elif direction == "both":
                direction = random.choice(["right", "left"])

        # PID
        pid = VehiclePIDController(self.vehicle, args_lateral=args_lateral_dict, args_longitudinal=args_long_dict)
        # 获取当前速度
        speed = get_speed(self.vehicle)
        # 设置速度防止车子在已有速度上突然减速
        set_speed(self.vehicle, speed)
        # 变道距离,根据速度实现
        distance = max(speed, min_direction)

        while True:  # 获取到变道后的终点坐标
            location = self.vehicle.get_location()
            if direction == "right":
                for i in range(line_number):
                    location = env_map.get_waypoint(location).get_right_lane().transform.location
            else:
                for i in range(line_number):
                    location = env_map.get_waypoint(location).get_left_lane().transform.location
            waypoint = env_map.get_waypoint(location)
            if not waypoint:
                sleep(0.01)
                continue
            waypoint = waypoint.next(distance + 5 * line_number)[0]
            break

        end_location = waypoint.transform.location
        if method == "agent":
            self.autopilot_agent(end_location)
            return
        if draw:
            draw_line(locations=[self.vehicle.get_location(), end_location], life_time=(15 - get_speed(self.vehicle)) / 10)  # 划线
        while True:
            if self.vehicle.get_location().distance(end_location) < 0.5:
                now_time = time.time()
                while time.time() - now_time < 1:  # 变道完成后再执行一秒往前开
                    waypoint = env_map.get_waypoint(self.vehicle.get_location()).next(int(get_speed(self.vehicle)))
                    if waypoint:
                        waypoint = waypoint[0]
                    else:
                        print("变道完前方没路了")
                    result = pid.run_step(self.autopilot_speed_limit, waypoint)
                    self.vehicle.apply_control(result)
                    sleep(0.01)
                print("变道完毕")
                self.lose_control = False
                return
            set_speed(self.vehicle, self.autopilot_speed_limit)
            result = pid.run_step(self.autopilot_speed_limit, waypoint)
            self.vehicle.apply_control(result)
            sleep(0.01)

    def autopilot_agent(self, end_location, ignore_traffic_light=True, mode="aggressive", distance=4.5, draw=False, lift_time=10):
        """
        自动驾驶车辆到终点坐标
        :param end_location: 终点坐标
        :param ignore_traffic_light: 是否忽略交通规则
        :param mode: 模式，有三种，速度不一样  cautious(最慢)，normal(正常),aggressive(稍快)
        :param distance: 每个waypoint之间的距离
        :param draw: 是否绘制线路
        :param lift_time: 路线存活时间
        """
        self.lose_control = True
        agent = BehaviorAgent(self.vehicle, ignore_traffic_light=ignore_traffic_light, behavior=mode)
        agent.speed_limit = self.autopilot_speed_limit
        agent._sampling_resolution = distance

        agent.set_destination(self.vehicle.get_location(), end_location, clean=True)

        while True:
            agent.update_information(self.vehicle)
            if len(agent._local_planner.waypoints_queue) < 2:
                self.lose_control = False
                print('======== Success, Arrivied at Target Point!')
                return True
            control = agent.run_step(debug=draw)
            self.vehicle.apply_control(control)
            sleep(0.01)

    def autopilot_pid(self, end_location, draw=False):
        """
        自动驾驶到终点
        :param end_location: 终点坐标
        :return:
        """
        self.lose_control = True
        # PID
        pid = VehiclePIDController(self.vehicle, args_lateral=args_lateral_dict, args_longitudinal=args_long_dict)
        while True:
            # 设置车子速度，防止他在原有基础速度上突然减速
            speed = get_speed(self.vehicle)
            set_speed(self.vehicle, speed)
            # 计算每个waypoint的距离，如果速度越快，相应waypoint距离增加，防止掉头
            sampling_resolution = max(int(get_speed(self.vehicle) // 10), 1)
            # 创建路由对象，方便获取路径
            dao = GlobalRoutePlannerDAO(env_map, sampling_resolution=4.5)
            grp = GlobalRoutePlanner(dao)
            grp.setup()
            # 获取前往终点的路径信息
            path = grp.trace_route(self.vehicle.get_location(), end_location)
            # 如果没有了，就认为到达目的地
            if len(path) < sampling_resolution + 2:
                self.lose_control = False
                print("======== Success, Arrivied at Target Point!")
                return
            # 省略前几个waypoint，防止速度过快往回跑
            waypoint = path[sampling_resolution + 1][0]
            if draw:
                draw_line(locations=[self.vehicle.get_location(), waypoint.transform.location], life_time=0.1)  # 划线
            result = pid.run_step(self.autopilot_speed_limit, waypoint)
            self.vehicle.apply_control(result)
            sleep(0.01)


class Window:
    def __init__(self, vehicle, sensor_type='sensor.camera.rgb'):
        """
        创建车子的pygame窗口显示
        :param vehicle: 车子对象
        """
        self.vehicle = vehicle
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1600, 1000  # 屏幕大小
        self.screen = None  # 初始化屏幕窗口
        pygame.init()  # 初始化pygame

        # 初始化窗口设置
        self.clock = pygame.time.Clock()
        self.size = 18  # 字体大小
        self.fps = 60  # 帧率
        self.font = pygame.font.Font(r"TTF\宋体.ttf", self.size)  # 初始化字体对象

        # 初始化传感器
        self.blueprint_camera = blueprint_library.find(sensor_type)  # 选择一个传感器蓝图
        self.blueprint_camera.set_attribute('image_size_x', f'{self.SCREEN_WIDTH}')  # 传感器获得的图片高度
        self.blueprint_camera.set_attribute('image_size_y', f'{self.SCREEN_HEIGHT}')  # 传感器获得的图片宽度
        self.blueprint_camera.set_attribute('fov', '110')  # 水平方向上能看到的视角度数
        spawn_point = carla.Transform(carla.Location(x=-5, y=0, z=3),
                                      carla.Rotation(pitch=0, yaw=0, roll=0))  # 传感器相对车子的位置设置
        self.sensor = world.spawn_actor(self.blueprint_camera, spawn_point, attach_to=self.vehicle)  # 添加传感器

        threading.Thread(target=self.show_screen).start()

    def show_screen(self):  # 显示窗口
        # 初始化窗口
        pygame.display.set_caption("pygame模拟场景")

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF, 32)
        self.sensor.listen(lambda image: self.process_img(image))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # 窗口关闭
                    pygame.quit()
                    os._exit(0)
            self.clock.tick(self.fps)

    # 加载图片
    def process_img(self, image):
        i = np.array(image.raw_data)
        i2 = i.reshape((self.SCREEN_HEIGHT, self.SCREEN_WIDTH, 4))
        i3 = i2[:, :, :3]
        i3 = np.rot90(i3, k=1, axes=(0, 1))
        i3 = i3[..., ::-1]
        img_surface = pygame.surfarray.make_surface(np.flip(i3, axis=0))
        self.screen.blit(img_surface, (0, 0))  # 绘制图片

        # 添加文字信息
        self.draw_text(f"速度：{round(get_speed(self.vehicle), 2)}km/h", 20, (0, 0))
        # 刷新屏幕
        pygame.display.flip()

    def draw_text(self, word, length, position, color=(255, 0, 0)):
        text = self.font.render(word.ljust(length), True, color)
        text_rect = text.get_rect()
        text_rect.topleft = position
        self.screen.blit(text, text_rect)


# 副车控制器
class Vice_Control:
    def __init__(self, vices):
        self.vices = vices  # 主车

        self.thread_car_number = 10  # 一个线程控制的车辆数
        self.thread_number = 1  # 这个是线程数
        self.whichOne = 0  # 用于记录遍历副车的索引
        self.speed_limit = 50  # 副车的速度限制

    def follow_road(self):
        def control():
            with ThreadPoolExecutor(max_workers=self.thread_number) as executor:
                while True:
                    if not self.vices:  # 如果没有车流
                        sleep(0.01)
                        continue
                    else:
                        if self.whichOne + self.thread_car_number > len(self.vices):
                            executor.submit(self.control_car, self.vices[self.whichOne:])
                            self.whichOne = 0
                        else:
                            executor.submit(self.control_car, self.vices[self.whichOne: self.whichOne + self.thread_car_number])
                            self.whichOne += self.thread_car_number
                    sleep(0.01)

        threading.Thread(target=control).start()

    def control_car(self, cars):
        for car in cars:
            pid = VehiclePIDController(car, args_lateral=args_lateral_dict, args_longitudinal=args_long_dict)
            # 获取前方道路
            waypoint = env_map.get_waypoint(car.get_location()).next(max(1, int(get_speed(car) / 6)))
            if waypoint:
                waypoint = waypoint[0]
            else:
                print(f"前方没有路了,当前车子坐标{car.get_location()},车子对象为{car}")
                car.destory()
            result = pid.run_step(self.speed_limit, waypoint)
            if get_speed(car) < self.speed_limit - 10:
                set_speed(car, self.speed_limit)
            car.apply_control(result)

    def lose_vice(self, car):
        for i in self.vices:
            if i.id == car.id:
                self.vices.remove(car)
                break


class Ramp_Vice_Control:
    def __init__(self, vice_car):
        self.vice_car = vice_car
        self.speed_limit = 50
        self.flag = True

    def follow_road(self):
        pid = VehiclePIDController(self.vice_car, args_lateral=args_lateral_dict, args_longitudinal=args_long_dict)

        def follow():
            while True:
                if not self.flag:
                    sleep(0.01)
                    continue
                waypoint = env_map.get_waypoint(self.vice_car.get_location()).next(max(1, int(get_speed(self.vice_car) / 6)))
                if waypoint:
                    waypoint = waypoint[0]
                else:
                    print(f"前方没有路了,当前车子坐标{self.vice_car.get_location()},车子对象为{self.vice_car}")
                    set_speed(self.vice_car, 0)
                    return
                set_speed(self.vice_car, self.speed_limit)
                result = pid.run_step(self.speed_limit, waypoint)
                self.vice_car.apply_control(result)
                sleep(0.01)

        threading.Thread(target=follow).start()

    def right_left_lane(self, direction=None, min_direction=10, method="pid", line_number=1, draw=False):
        """
        左转或右转
        :param direction: 左转还是右转,接收"left"和"right"
        :param min_direction: 最小变道距离
        :param method: 变道所使用的方法，默认用pid，还有agent
        :return:
        """
        self.flag = False
        # 判断有没有可变道路,得到direction方向值
        if not direction:  # 如果没有传左/右变道
            # 先判断左右是否有道路
            direction = str(env_map.get_waypoint(self.vice_car.get_location()).lane_change).lower()
            if not direction:  # 如果没有可变道路，找前方看有没有可以变道
                direction = str(env_map.get_waypoint(self.vice_car.get_location()).next(max(get_speed(self.vice_car), 5))[0].lane_change).lower()
                if not direction:
                    print("没有可变道路！！！！！！！！")
                    return
                elif direction == "both":
                    direction = random.choice(["right", "left"])
            elif direction == "both":
                direction = random.choice(["right", "left"])

        # PID
        pid = VehiclePIDController(self.vice_car, args_lateral=args_lateral_dict, args_longitudinal=args_long_dict)
        # 获取当前速度
        speed = get_speed(self.vice_car)
        # 设置速度防止车子在已有速度上突然减速
        set_speed(self.vice_car, speed)
        # 变道距离,根据速度实现
        distance = max(speed, min_direction)

        while True:  # 获取到变道后的终点坐标
            location = self.vice_car.get_location()
            if direction == "right":
                for i in range(line_number):
                    location = env_map.get_waypoint(location).get_right_lane().transform.location
            else:
                for i in range(line_number):
                    location = env_map.get_waypoint(location).get_left_lane().transform.location
            waypoint = env_map.get_waypoint(location)
            if not waypoint:
                sleep(0.01)
                continue
            waypoint = waypoint.next(distance + 5 * line_number)[0]
            break

        end_location = waypoint.transform.location
        if draw:
            draw_line(locations=[self.vice_car.get_location(), end_location], life_time=(15 - get_speed(self.vice_car)) / 10)  # 划线
        while True:
            if self.vice_car.get_location().distance(end_location) < 0.5:
                now_time = time.time()
                while time.time() - now_time < 1:  # 变道完成后再执行一秒往前开
                    waypoint = env_map.get_waypoint(self.vice_car.get_location()).next(int(get_speed(self.vice_car)))
                    if waypoint:
                        waypoint = waypoint[0]
                    else:
                        print("变道完前方没路了")
                    result = pid.run_step(self.speed_limit, waypoint)
                    self.vice_car.apply_control(result)
                    sleep(0.01)
                print("变道完毕")
                self.flag = True
                return
            set_speed(self.vice_car, self.speed_limit)
            result = pid.run_step(self.speed_limit, waypoint)
            self.vice_car.apply_control(result)
            sleep(0.01)


def pedestrian_control(people, speed=8, yaw=0, target_location=None):
    def con():
        people_control = carla.WalkerControl(speed=speed / 3.6)
        people_rotation = carla.Rotation(0, yaw, 0)
        people_control.direction = people_rotation.get_forward_vector()
        people.apply_control(people_control)

        if target_location:
            while True:
                if people.get_location().distance(target_location) < 2:
                    control = carla.WalkerControl()
                    control.direction.x = 0
                    control.direction.z = 0
                    control.direction.y = 0
                    people.apply_control(control)
                    break
                sleep(0.01)

    threading.Thread(target=con).start()


def create_actor(locations, model="vehicle.mini.cooper_s_2021", height=0.1):
    def create(location):
        transform = env_map.get_waypoint(location).transform
        transform.location.z += height
        blueprint = random.choice(blueprint_library.filter(model))
        actor = world.try_spawn_actor(blueprint, transform)
        if not actor:
            return actor
        while actor.get_location().x == 0 and actor.get_location().y == 0:
            sleep(0.001)
        return actor

    if isinstance(locations, list):
        actors = []
        for location in locations:
            actors.append(create(location))
        return actors
    else:
        return create(locations)


# 控制车辆刹车
def brake_throttle_retard(vehicle, acceleration, target_speed):
    """
    加减速
    :param vehicle: 目标车辆
    :param acceleration: 加速度
    :param target_speed: 目标速度
    :return:
    """
    pid = VehiclePIDController(vehicle, args_lateral=args_lateral_dict, args_longitudinal=args_long_dict)
    t = time.time()
    speed = get_speed(vehicle)
    while abs(get_speed(vehicle) - target_speed) > 1:
        # 获取前方道路
        waypoint = env_map.get_waypoint(vehicle.get_location()).next(max(1, int(get_speed(vehicle) / 6)))
        if waypoint:
            waypoint = waypoint[0]
        else:
            print(f"前方没有路了,当前车子坐标{vehicle.get_location()},车子对象为{vehicle}")
            return
        result = pid.run_step(target_speed, waypoint)
        result.brake = 0
        result.throttle = 0
        vehicle.apply_control(result)  # 这个只控制方向盘

        sp = (max(0, speed + acceleration * (time.time() - t) * 3.6))
        set_speed(vehicle, sp)
        sleep(0.01)
    for _ in range(10):
        set_speed(vehicle, target_speed)
        sleep(0.1)


def load_map(xodr_path):
    """
    导入地图
    :param xodr_path :  xodr文件路径
    """
    with open(xodr_path, encoding="utf-8") as f:
        data = f.read()
        vertex_distance = 1
        max_road_length = 500
        wall_height = 0.5
        extra_width = 1
        client.generate_opendrive_world(data,
                                        carla.OpendriveGenerationParameters(vertex_distance=vertex_distance,
                                                                            max_road_length=max_road_length,
                                                                            wall_height=wall_height,
                                                                            additional_width=extra_width,
                                                                            smooth_junctions=True, enable_mesh_visibility=True))


# 获取当前车道的车辆，返回升序车辆列表
def get_now_road_car(vehicle, next_vehicle=False, previous_vehicle=False):
    """
    返回当前车道的车辆
    :param vehicle: 车子对象
    :param next_vehicle: 前方车辆，默认获取，置为True,只获取前车
    :param previous_vehicle: 后方车辆，默认获取，置为True,只获取后车
    :return:  返回升序车辆列表，元组中第二个参数为True表示前方，False为后方
    """

    def distance_between_vehicles(vehicle, vehicle2):
        return vehicle.get_location().distance(vehicle2.get_location())

    def is_vehicle_in_front(target_vehicle, reference_vehicle):
        """
        返回是在车子前方还是后方
        :param target_vehicle: 目标车
        :param reference_vehicle: 主车，这个是主车
        :return: 一个车辆列表，每个索引值是一个元组，包含车辆对象，前车or后车，距离
        """
        target_location = target_vehicle.get_location()
        target_forward = target_vehicle.get_transform().get_forward_vector()

        reference_location = reference_vehicle.get_location()

        # 计算从参考车辆指向目标车辆的向量
        vector_to_target = carla.Location(target_location.x - reference_location.x,
                                          target_location.y - reference_location.y,
                                          target_location.z - reference_location.z)

        # 计算向量夹角（使用点积）
        dot_product = target_forward.x * vector_to_target.x + target_forward.y * vector_to_target.y
        magnitude_product = math.sqrt(target_forward.x ** 2 + target_forward.y ** 2) * math.sqrt(
            vector_to_target.x ** 2 + vector_to_target.y ** 2)
        angle = math.acos(dot_product / magnitude_product) * (180 / math.pi)

        # 一般情况下，如果夹角小于90度，则目标车辆在主车辆的前方
        return angle < 90

    # 获取所有车辆对象
    vice_cars = list(world.get_actors().filter("vehicle.*"))
    vice_cars = [v for v in vice_cars if v.id != vehicle.id]  # 排除自车
    vice_cars = [v for v in vice_cars if env_map.get_waypoint(v.get_location()).lane_id == env_map.get_waypoint(vehicle.get_location()).lane_id]  # 只要当前车道车辆
    if not vice_cars:
        return None  # 该车道没有车

    distance_list = [(v, is_vehicle_in_front(v, vehicle), distance_between_vehicles(vehicle, v)) for v in vice_cars]
    sorted_list = sorted(distance_list, key=lambda x: x[2])

    # 筛选
    if next_vehicle:
        return [tup for tup in sorted_list if tup[1] is True]
    if previous_vehicle:
        return [tup for tup in sorted_list if tup[1] is False]
    return sorted_list


def timed_function(interval, stop_event):
    """
    在函数上加上一下内容就可以实现定时器
    stop_event = threading.Event()  # 用于停止定时器，执行stop_event.set()就可以停止该定时器
    @timed_function(interval=0.01, stop_event=stop_event)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 定义定时器回调函数
            def timer_callback():
                func(*args, **kwargs)
                # 递归调用定时器，实现周期性执行
                if not stop_event.is_set():
                    threading.Timer(interval, timer_callback).start()

            # 启动定时器
            threading.Timer(interval, timer_callback).start()

        return wrapper

    return decorator


def set_towards(vehicle):
    """
    单独设置车子的朝向
    :param vehicle: 车子对象
    :return:
    """
    transform = vehicle.get_transform()
    vehicle.set_transform(transform)  # 这个需要的是transform对象


def get_vehicle_steer(vehicle):
    """
    获取carla中车子方向盘值
    :param vehicle: 车子对象
    :return:
    """
    return vehicle.get_control().steer


def get_vehicle_length(vehicle):
    """
    获取车子的长度
    :param vehicle: 车子对象
    :return: 返回车子的长宽高
    """
    car_length = vehicle.bounding_box.extent
    return car_length.x * 2, car_length.y * 2, car_length.z * 2


def draw_line(location1=None, location2=None, locations=None, thickness=0.1, life_time=10.0, color=carla.Color(255, 0, 0)):
    """
    用直线连接两个点或者多个点
    :param location1: carla坐标点1
    :param location2: carla坐标点2
    :param locations: 坐标点列表，如果传入坐标点列表，前面两个点失效,carla坐标点列表
    :param thickness: 亮度
    :param life_time: 存活时间
    :param color: 颜色
    :return: 没有返回，绘制出连线点
    """
    if locations:
        for index, location in enumerate(locations[1:]):
            world.debug.draw_line(locations[index], location, thickness=thickness, color=color, life_time=life_time)
        return
    world.debug.draw_line(location1, location2, thickness=thickness, color=color, life_time=life_time)


def set_speed(vehicle, speed_kmh):
    """
    强制设置车子速度
    :param vehicle: 车子对象
    :param speed_kmh: 车子速度
    :return:
    """
    speed = speed_kmh / 3.6
    # 获取车辆的当前速度方向
    forward_vector = vehicle.get_transform().rotation.get_forward_vector()
    # 设置车子速度
    vehicle.set_target_velocity(carla.Vector3D(forward_vector.x * speed, forward_vector.y * speed, forward_vector.z * speed))


def draw_arrow(locations, distance=10, height=1):
    """
    绘制起点专用的，绘制世界中箭头，一直存在的
    :param locations: carla.Location列表
    :param distance: 箭头绘制的距离
    :param height: 绘制的高度
    """
    debug = world.debug
    for location in locations:
        arrow_location = location + carla.Location(z=height)  # 假设箭头位置略高于地面
        target_location = env_map.get_waypoint(arrow_location).next(distance)[0].transform.location
        target_location.z += height
        # 绘制箭头
        debug.draw_arrow(arrow_location, target_location, thickness=0.3, arrow_size=0.5, color=carla.Color(255, 0, 0))

#
# def get_steering_wheel_info():
#     """
#     return: 方向盘、刹车、油门
#     """
#     # 这里0,2,3根据实际情况的方向盘参数
#     return joystick.get_axis(0), (-joystick.get_axis(2) + 1) / 2 , (-joystick.get_axis(1) + 1)/2

def get_steering_wheel_info():
    keys = pygame.key.get_pressed()
    throttle, brake, steer = (0, 0, 0)

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        throttle = 1.0
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        brake = 1.0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        steer = -0.5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        steer = 0.5
    return steer, brake, throttle


def destroy_all_vehicles_traffics(vehicle_flag=True, traffic_flag=True, people_flag=True, sensor_flag=True):
    """
    销毁世界中的所有车辆，交通标志，行人和传感器
    :param vehicle_flag: 是否销毁车辆，默认销毁
    :param traffic_flag: 是否销毁交通标志，默认销毁
    :param people_flag: 是否销毁行人，默认销毁
    :param sensor_flag: 是否销毁传感器，默认销毁
    :return:
    """
    actors = []
    if vehicle_flag:
        actors += list(world.get_actors().filter('*vehicle*'))
    if traffic_flag:
        actors += list(world.get_actors().filter("*prop*"))
    if people_flag:
        actors += list(world.get_actors().filter("*walker*"))
    if sensor_flag:
        actors += list(world.get_actors().filter("*sensor*"))

    # 销毁每个物体
    for actor in actors:
        actor.destroy()



