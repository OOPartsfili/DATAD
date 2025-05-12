import socket
import struct
import threading

_steering_wheel_angle = 0
angle_lock = threading.Lock() 

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
steer_local_address = ('192.168.31.107', 9763)
udp_socket.bind(steer_local_address)

def get_steering_angle():
    with angle_lock:
        return _steering_wheel_angle
    
def set_steering_angle(angle):
    with angle_lock:
        global _steering_wheel_angle
        _steering_wheel_angle = angle


def parse_euler():
    calibration_frames = 10
    calibration_values = []
    last_angle = None
    total_rotation = 0

    while True:
        format_string = '>6sIcblbbbbhh'
        segment_format = '>Iffffff'
        data, addr = udp_socket.recvfrom(4096) 
        header = struct.unpack(format_string, data[0:24])
        body = []
        for i in range(24):
            segment_body = []
            pos = []
            ori = []
            begin_flag = 24 + i * 28
            end_flag = 23 + 28 + i * 28 + 1
            segment_data = struct.unpack(segment_format, data[begin_flag:end_flag])
            id = segment_data[0]
            for j in range(1, 4):
                pos.append(segment_data[j])
            for k in range(4, 7):
                ori.append(segment_data[k])
            segment_body.append(id)
            segment_body.append(pos)
            segment_body.append(ori)
            body.append(segment_body)
        current_angle = body[23][2][2] 

        if len(calibration_values) < calibration_frames:
            calibration_values.append(current_angle)
            if len(calibration_values) == calibration_frames:
                zero_angle = sum(calibration_values) / calibration_frames
            continue  
        adjusted_angle = current_angle - zero_angle

        if last_angle is not None:
            angle_delta = adjusted_angle - last_angle
            if angle_delta > 180:
                total_rotation -= 360
            elif angle_delta < -180:
                total_rotation += 360
        last_angle = adjusted_angle

        steering_wheel_angle = total_rotation + adjusted_angle
        if steering_wheel_angle > 540:
            steering_wheel_angle -= 1080
        elif steering_wheel_angle < -540:
            steering_wheel_angle += 1080

        set_steering_angle(steering_wheel_angle) 
        # print(f"Steering Wheel Angle: {steering_wheel_angle:.2f}")
# parse_euler()
