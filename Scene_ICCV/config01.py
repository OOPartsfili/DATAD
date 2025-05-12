import carla

# 位置信息
main_vehicle_location = carla.Location(x=-700, y=-291.25)  # 主车位置

# 事故位置
accident_location  = carla.Location(x=-500, y=-289)

# 接管起点
TOR_location = carla.Location(x=-530, y=-292.202942)

# 接管终点(箭头的起点和终点)
start_location = carla.Location(x=-367, y=-295, z=2 )
end_location = carla.Location(x=-367, y=-283, z=2 )


# 数据记录信息
dict_index = {
    0: "main_car",
    1: "Car1",
    2: "Car2",
    3: "Car3",
    4: "Car4",
    5: "Car5",
}


file_name1 = 'carla_data/data01.csv'
file_name2 = 'carla_data/data01_ARHUD.csv'