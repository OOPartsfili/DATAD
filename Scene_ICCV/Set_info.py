from vehicle_method import *
import threading
import csv
import time

# dict_0 是CSV文件的关键
dict_0 = {"time": [],
        "steering": [],
        "accelerator": [],
        "brake": [],
        # "main_car_dev":[],
        'TOR_flag':[], #0为未接管、1为发出接管
        'Handchange_flag':[],
        "Collision_flag":[] #0为未碰撞，其他数为碰撞物ID
          }

def get_vehicle_yaw(vehicle):
    # 获取车辆的变换信息
    vehicle_transform = vehicle.get_transform()
    # 获取车辆的方向（四元数表示）
    rotation = vehicle_transform.rotation
    # 将四元数转换为欧拉角（弧度）
    pitch, yaw, roll = rotation.pitch, rotation.yaw, rotation.roll
    # 将偏航角限制在0到2*pi之间
    yaw = math.radians(yaw)
    return yaw

def get_lane_deviation(vehicle):
    # 获取车辆的位置
    vehicle_location = vehicle.get_location()
    # 获取最近的道路点
    waypoint = world.get_map().get_waypoint(vehicle_location)
    # 获取车道中心线的位置
    lane_center = waypoint.transform.location
    # 计算车辆和车道中心线之间的距离
    deviation = vehicle_location.distance(lane_center)
    return deviation

class Info:
    def __init__(self, dict_index, dict_0, file_name, fps=60):
        self.car_list = []
        self.flag = True
        self.dict_index = dict_index
        self.dict_0 = dict_0
        self.fps = fps
        self.file_name = file_name
        self.TOR_flag = 0   # 专门获取TOR发出时间的
        self.Handchange_flag = 0 # 驾驶员切换到手动驾驶的旗帜
        self.Collision_flag = 0 #专门获取碰撞对象

    # 获取数据
    def get_info(self):
        # 一旦开始运行，就以特定频率记录car_list中所有车辆的数据
        def getinfo():
            # 只要self.flag为True ，就进行CSV数据记录
            while self.flag:
                self.dict_0["time"].append(round(time.time(),3))  # 添加时间戳
                steering, accelerator ,brake= get_sensor_data() #获取方向盘，油门，踏板
                self.dict_0["steering"].append(steering)
                self.dict_0["accelerator"].append(accelerator)
                self.dict_0["brake"].append(brake)

                # 主车专属变量 默认car_list[0]为主车
                # ttc_list = [ttc(self.car_list[0], v) for v in self.car_list[1:]]
                # self.dict_0["main_car_TTC"].append(min(ttc_list))
                # self.dict_0["main_car_dev"].append(get_lane_deviation(self.car_list[0]))
                self.dict_0["TOR_flag"].append(self.TOR_flag)
                self.dict_0["Collision_flag"].append(self.Collision_flag)
                self.dict_0["Handchange_flag"].append(self.Handchange_flag)

                # car_list是所有车的位置信息
                for index, car in enumerate(self.car_list):
                    if self.dict_0.get(f"{self.dict_index[index]}_id") is None:
                        self.dict_0[f"{self.dict_index[index]}_id"] = [car.id]
                        location = car.get_location()
                        self.dict_0[f"{self.dict_index[index]}_x"] = [location.x]
                        self.dict_0[f"{self.dict_index[index]}_y"] = [location.y]
                        self.dict_0[f"{self.dict_index[index]}_z"] = [location.z]
                        self.dict_0[f"{self.dict_index[index]}_speed(km/h)"] = [get_speed(car)]
                        self.dict_0[f"{self.dict_index[index]}_accx"] = [car.get_acceleration().x] # 加速度
                        self.dict_0[f"{self.dict_index[index]}_accy"] = [car.get_acceleration().y]  # 加速度
                        transform = car.get_transform()
                        self.dict_0[f"{self.dict_index[index]}_pitch"] = [transform.rotation.pitch]
                        self.dict_0[f"{self.dict_index[index]}_yaw"] = [transform.rotation.yaw]
                        self.dict_0[f"{self.dict_index[index]}_roll"] = [transform.rotation.roll]

                    else:
                        self.dict_0[f"{self.dict_index[index]}_id"].append(car.id)
                        location = car.get_location()
                        self.dict_0[f"{self.dict_index[index]}_x"].append(location.x)
                        self.dict_0[f"{self.dict_index[index]}_y"].append(location.y)
                        self.dict_0[f"{self.dict_index[index]}_z"].append(location.z)
                        self.dict_0[f"{self.dict_index[index]}_speed(km/h)"].append(get_speed(car))
                        self.dict_0[f"{self.dict_index[index]}_accx"].append(car.get_acceleration().x) # 加速度
                        self.dict_0[f"{self.dict_index[index]}_accy"].append(car.get_acceleration().y)  # 加速度
                        transform = car.get_transform()
                        self.dict_0[f"{self.dict_index[index]}_pitch"].append(transform.rotation.pitch)
                        self.dict_0[f"{self.dict_index[index]}_yaw"].append(transform.rotation.yaw)
                        self.dict_0[f"{self.dict_index[index]}_roll"].append(transform.rotation.roll)
                # 这里可以调节频率(艺术)
                time.sleep(round(1/(self.fps+70),12))


        threading.Thread(target=getinfo).start()

    # 保存数据
    def save_info(self):
        self.flag = False
        # 找出最长的列表长度
        max_length = max(len(values) for values in self.dict_0.values())
        # 在每个列表的前面添加 None
        for key in self.dict_0:
            self.dict_0[key] = [None] * (max_length - len(self.dict_0[key])) + self.dict_0[key]

        # 将数据写入CSV文件
        with open(self.file_name, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.dict_0.keys())  # 写入列名
            writer.writerows(zip(*self.dict_0.values()))  # 写入数据
