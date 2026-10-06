'''
=============================================================================
ĐỀ BÀI: Bài 9 - Điều khiển Động cơ Servo qua cảm biến DHT11 (đã tinh chỉnh góc chuẩn):
- Nhiệt độ < 28°C VÀ Độ ẩm < 75% -> Quay 45° trong 1 giây rồi về 0°
- 28°C <= Nhiệt độ <= 32°C VÀ Độ ẩm >= 75% -> Quay 90° trong 1 giây rồi về 0°
- Nhiệt độ > 32°C VÀ Độ ẩm >= 75% -> Quay 135° trong 1 giây rồi về 0°

WIRING:
- DHT11 DATA: GPIO 4 | VCC: 5V | GND: GND
- Servo Tín hiệu (Cam/Vàng): GPIO 18
- Servo VCC (Đỏ): 5V | GND (Nâu/Đen): GND
=============================================================================
'''

import time
import board
import adafruit_dht
from gpiozero import AngularServo

# Khởi tạo cảm biến DHT11 ở chân GPIO 4
dht_device = adafruit_dht.DHT11(board.D4)

# Khởi tạo Động cơ Servo với dải xung chuẩn cho SG90 (0.5ms đến 2.5ms)
# Giúp khắc phục triệt để tình trạng quay bị hụt góc (gọi 90° mà chỉ chạy 45°)
servo = AngularServo(
    18, 
    min_angle=0, 
    max_angle=180, 
    min_pulse_width=0.0005,  # 0.5 ms tương ứng 0 độ
    max_pulse_width=0.0025   # 2.5 ms tương ứng 180 độ
)

def main():
    """Vòng lặp chính: Đọc DHT11, quay servo đến góc định mức trong 1s rồi về 0°."""
    print("Hệ thống Động cơ Servo & DHT11 đã sẵn sàng. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            try:
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                
                if temperature is not None and humidity is not None:
                    print(f"Nhiệt độ: {temperature:.1f}°C | Độ ẩm: {humidity:.1f}%")
                    
                    target_angle = None
                    
                    # Điều kiện 1: Nhiệt độ < 28°C VÀ Độ ẩm < 75% -> Quay 45°
                    if temperature < 28.0 and humidity < 75.0:
                        target_angle = 45
                        print("-> [Trường hợp 1] Quay chuẩn 45°")
                        
                    # Điều kiện 2: 28°C <= Nhiệt độ <= 32°C VÀ Độ ẩm >= 75% -> Quay 90°
                    elif 28.0 <= temperature <= 32.0 and humidity >= 75.0:
                        target_angle = 90
                        print("-> [Trường hợp 2] Quay chuẩn 90°")
                        
                    # Điều kiện 3: Nhiệt độ > 32°C VÀ Độ ẩm >= 75% -> Quay 135°
                    elif temperature > 32.0 and humidity >= 75.0:
                        target_angle = 135
                        print("-> [Trường hợp 3] Quay chuẩn 135°")
                    
                    # Thực hiện quay và hồi vị
                    if target_angle is not None:
                        servo.angle = target_angle
                        time.sleep(1.0)  # Giữ ở góc mục tiêu trong 1 giây
                        
                        servo.angle = 0  # Quay trở về góc 0°
                        print("-> Quay về 0°")
                        time.sleep(0.5)
                    else:
                        print("-> Ngoài vùng điều kiện: Servo đứng yên ở 0°.")
                        servo.angle = 0
                else:
                    print("Đang chờ dữ liệu từ cảm biến...")
                    
            except RuntimeError as error:
                print(f"Lỗi đọc cảm biến (bình thường): {error.args[0]}")
                
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\nĐang dừng chương trình...")
    finally:
        dht_device.exit()
        servo.detach()

if __name__ == '__main__':
    main()