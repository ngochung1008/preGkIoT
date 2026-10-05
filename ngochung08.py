'''
=============================================================================
ĐỀ BÀI: Điều khiển động cơ bước (28BYJ-48) qua cảm biến siêu âm (HC-SR04) 
dùng thư viện gpiozero (cho cảm biến) và RpiMotorLib (cho động cơ):
- Khoảng cách < 20cm -> Quay thuận 90 độ
- 20cm <= Khoảng cách <= 40cm -> Quay nghịch 180 độ
- Khoảng cách > 40cm -> Quay nghịch 90 độ

WIRING:
- HC-SR04 Trig: GPIO 23 | Echo: GPIO 24 (qua mạch chia áp) | VCC: 5V | GND: GND
- ULN2003 IN1 -> GPIO 17, IN2 -> GPIO 18, IN3 -> GPIO 27, IN4 -> GPIO 22
- ULN2003 VCC: 5V | GND: GND
=============================================================================
'''

import time
from gpiozero import DistanceSensor
from RpiMotorLib import RpiMotorLib

# Khởi tạo cảm biến siêu âm bằng thư viện gpiozero (echo, trigger)
# Mặc định trả về giá trị Mét, nhân 100 để quy đổi ra cm
sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

# Khai báo danh sách các chân GPIO nối với driver ULN2003 theo thứ tự (IN1, IN2, IN3, IN4)
pins = [17, 18, 27, 22]

# Khởi tạo đối tượng động cơ bước 28BYJ-48 bằng thư viện RpiMotorLib
stepper_motor = RpiMotorLib.BYJMotor("MyStepper", "28BYJ")

def rotate_angle(degrees, direction="forward"):
    """Hàm quay động cơ theo góc độ và hướng sử dụng thư viện RpiMotorLib."""
    steps_to_take = int(degrees * (512 / 360))
    is_clockwise = True if direction == "forward" else False
    
    # Gọi hàm motor_run của thư viện
    stepper_motor.motor_run(pins, 0.002, steps_to_take, is_clockwise, False, "full")

def main():
    """Vòng lặp chính đọc khoảng cách siêu âm bằng gpiozero và điều khiển động cơ bước."""
    print("Hệ thống Động cơ bước & Siêu âm (dùng thư viện) đã sẵn sàng. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            # Đọc khoảng cách bằng 1 dòng lệnh duy nhất của thư viện gpiozero (đổi sang cm)
            dist = sensor.distance * 100
            print(f"Khoảng cách đo được: {dist:.2f} cm")
            
            # Trường hợp 1: Khoảng cách < 20cm -> Quay thuận 90 độ
            if dist < 20.0:
                print("-> [Trường hợp 1] Khoảng cách < 20cm: Quay THUẬN 90 độ")
                rotate_angle(90, direction="forward")
                
            # Trường hợp 2: Khoảng cách từ 20cm đến 40cm -> Quay nghịch 180 độ
            elif 20.0 <= dist <= 40.0:
                print("-> [Trường hợp 2] Khoảng cách 20-40cm: Quay NGHỊCH 180 độ")
                rotate_angle(180, direction="backward")
                
            # Trường hợp 3: Khoảng cách > 40cm -> Quay nghịch 90 độ
            else:
                print("-> [Trường hợp 3] Khoảng cách > 40cm: Quay NGHỊCH 90 độ")
                rotate_angle(90, direction="backward")
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nĐang dừng chương trình...")

if __name__ == '__main__':
    main()