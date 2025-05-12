import socket
import threading

_data = {
    'acc': 0,
    'brake': 0
}

pedal_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
local_address = ('127.0.0.1', 12001)  
pedal_udp_socket.bind(local_address)

def get_data():
    return _data['acc'],_data['brake']

def update_data(acc, brake):
    _data['acc'] = acc
    _data['brake'] = brake

def pedal_receiver():
    try:
        while True:
            message, _ = pedal_udp_socket.recvfrom(1024)  
            decoded_message = message.decode()
            parts = decoded_message.split(', ')
            acc = float(parts[0].split(': ')[1])
            brake = float(parts[1].split(': ')[1])
            update_data(acc, brake)
            # print(acc,brake)
    except Exception as e:
        print(f"Receiver error: {e}")
    finally:
        pedal_udp_socket.close()


# recv_thread = threading.Thread(target=pedal_receiver)
# recv_thread.start()
