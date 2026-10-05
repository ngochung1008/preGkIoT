'''
=============================================================================
ĐỀ BÀI: Điều khiển Động cơ Servo qua cảm biến siêu âm (HC-SR04) dùng gpiozero:
- Khoảng cách < 20cm -> Servo quay 45° trong 1 giây rồi về 0°
- 20cm <= Khoảng cách <= 40cm -> Servo quay 90° trong 1 giây rồi về 0°
- Khoảng cách > 40cm -> Servo quay 135° trong 1 giây rồi về 0°

WIRING:
- HC-SR04 Trig: GPIO 23 | Echo: GPIO 24 (qua mạch chia áp) | VCC: 5V | GND: GND
- Servo Tín hiệu (Cam/Vàng): GPIO 18 | VCC: 5V | GND: GND
=============================================================================
'''

import time
from gpiozero import DistanceSensor, AngularServo

# Khởi tạo cảm biến siêu âm (echo=24, trigger=23) bằng gpiozero
# (Đơn vị mặc định là Mét, ta nhân 100 để quy đổi ra cm)
sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

# Khởi tạo Động cơ Servo ở chân GPIO 18 với dải xung chuẩn cho SG90
servo = AngularServo(
    18, 
    min_angle=0, 
    max_angle=180, 
    min_pulse_width=0.0005,  # 0.5 ms tương ứng 0 độ
    max_pulse_width=0.0025   # 2.5 ms tương ứng 180 độ
)

def main():
    """Vòng lặp chính: Đọc khoảng cách siêu âm, điều khiển servo quay góc 45/90/135° trong 1s rồi về 0°."""
    print("Hệ thống Động cơ Servo & Cảm biến siêu âm (gpiozero) đã sẵn sàng. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            # Lấy giá trị khoảng cách và đổi ra cm
            dist = sensor.distance * 100
            print(f"Khoảng cách đo được: {dist:.2f} cm")
            
            target_angle = None
            
            # Trường hợp 1: Khoảng cách < 20cm -> Quay 45°
            if dist < 20.0:
                target_angle = 45
                print("-> [Trường hợp 1] Khoảng cách < 20cm: Quay chuẩn 45°")
                
            # Trường hợp 2: Khoảng cách từ 20cm đến 40cm -> Quay 90°
            elif 20.0 <= dist <= 40.0:
                target_angle = 90
                print("-> [Trường hợp 2] Khoảng cách 20-40cm: Quay chuẩn 90°")
                
            # Trường hợp 3: Khoảng cách > 40cm -> Quay 135°
            else:
                target_angle = 135
                print("-> [Trường hợp 3] Khoảng cách > 40cm: Quay chuẩn 135°")
            
            # Thực hiện quay góc mục tiêu, giữ 1 giây rồi hồi vị về 0°
            if target_angle is not None:
                servo.angle = target_angle
                time.sleep(1.0)  # Giữ ở góc mục tiêu trong 1 giây
                
                servo.angle = 0  # Quay trở về góc 0°
                print("-> Quay về 0°")
                
            time.sleep(0.5)  # Nghỉ ngắn trước vòng lặp tiếp theo
            
    except KeyboardInterrupt:
        print("\nĐang dừng chương trình...")
    finally:
        servo.detach()

if __name__ == '__main__':
    main()