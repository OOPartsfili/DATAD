import json
import socket
from hipnuc_acc import *
from hipnuc_brake import *

def load_calibration(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

def map_brake(angle, min_angle, max_angle, reverse=False):
    K_brake = 1  
    if reverse:
        nor_data = (max_angle - angle) / (max_angle - min_angle)
    else:
        nor_data = (angle - min_angle) / (max_angle - min_angle)
    
    nor_data = max(0, min(nor_data * K_brake, 1))
    return nor_data

def map_acc(angle, min_angle, max_angle, reverse=False):
    K_acc = 3
    if reverse:
        nor_data = (max_angle - angle) / (max_angle - min_angle)
    else:
        nor_data = (angle - min_angle) / (max_angle - min_angle)
    
    nor_data = max(0, min(nor_data * K_acc, 1))
    return nor_data

def initial_direction(hip_module, calibration, sensor_key):
    samples = []
    for _ in range(10):
        data = hip_module.get_module_data(10)
        pitch_angle = data['euler'][0]['Pitch']
        samples.append(pitch_angle)
    avg_angle = sum(samples) / len(samples)
    min_angle = calibration[sensor_key]['min']
    max_angle = calibration[sensor_key]['max']
    return avg_angle < (min_angle + max_angle) / 2


hip_acc = hipnuc_acc(r'E:\Scene_package\Scene_AAP\sensor_script\config\config_acc.json')
hip_brake = hipnuc_brake(r'E:\Scene_package\Scene_AAP\sensor_script\config\config_brake.json')
config_file = r'E:\Scene_package\Scene_AAP\sensor\pedal_calibration.json'

calibration = load_calibration(config_file)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 12001)

try:
    acc_reverse = not initial_direction(hip_acc, calibration, 'acc')
    brake_reverse = not initial_direction(hip_brake, calibration, 'brake')
    while True:
        try:
            acc_data = hip_acc.get_module_data(10)
            acc_num = acc_data['euler'][0]['Pitch']
            mapped_acc_num = map_acc(acc_num, calibration['acc']['min'], calibration['acc']['max'], acc_reverse)

            brake_data = hip_brake.get_module_data(10)
            brake_num = brake_data['euler'][0]['Pitch']
            mapped_brake_num = map_brake(brake_num, calibration['brake']['min'], calibration['brake']['max'], brake_reverse)

            message = f"ACC: {mapped_acc_num:.3f}, BRAKE: {mapped_brake_num:.3f}"
            print(message)
            udp_socket.sendto(message.encode(), server_address)
        except Exception as e:
            print(f"Error: {e}")
            break
finally:
    hip_acc.close()
    hip_brake.close()
    udp_socket.close()
