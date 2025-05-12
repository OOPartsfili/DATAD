import socket
import json
import csv
import os
import time

# 配置接收数据的 IP 和端口
RECEIVER_IP = "0.0.0.0"
RECEIVER_PORT = 1999

# 配置保存 CSV 文件的路径
time_now = str(int(time.time()))
CSV_FILE_PATH = 'received_data' + '_' + time_now + '.csv'

def main():
    # 创建 UDP 套接字
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((RECEIVER_IP, RECEIVER_PORT))
        print(f"Listening on {RECEIVER_IP}:{RECEIVER_PORT}")

        # 打开 CSV 文件以写入模式
        with open(CSV_FILE_PATH, mode='w', newline='') as csv_file:
            fieldnames = None
            csv_writer = None

            while True:
                # 接收数据
                data, addr = sock.recvfrom(10024)
                decoded_data = data.decode('utf-8')
                json_data = json.loads(decoded_data)

                # 获取当前13位时间戳
                current_time = int(time.time() * 1000)

                # 确定 CSV 文件的列名
                if fieldnames is None:
                    fieldnames = list(json_data.keys()) + ['StorageTime']
                    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    csv_writer.writeheader()

                # 写入当前时间戳到数据
                json_data['StorageTime'] = current_time

                # 写入 CSV 文件
                csv_writer.writerow(json_data)
                print(f"Received and wrote data: {json_data}")

if __name__ == "__main__":
    main()
