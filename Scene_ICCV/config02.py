import carla


# 主车坐标
main_vehicle_location = carla.Location(x=-821.25, y=-305.75)

# 另一方向车坐标
right_vehicle_location = carla.Location(x=-995, y=-250)

TOR_location = carla.Location(x=-968.75, y=-301.75) # 紧急接管发起点


# 接管终点
# 十字路口终点坐标
start_location = carla.Location(x=-1021.75, y=-300, z=2)
end_location = carla.Location(x=-1021.75, y=-320, z=2)


# 数据记录信息
dict_index = {
    0: "main_car",
    1: "Car1",
    2: "Car2",
    3: "Car3",
    4: "Car4",
    5: "Car5",
}


file_name1 = 'carla_data/data02.csv'
file_name2 = 'carla_data/data02_ARHUD.csv'


