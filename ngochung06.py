'''
=============================================================================
ĐỀ BÀI: Bài 6 - Điều khiển động cơ DC qua cảm biến siêu âm (HC-SR04) dùng thư viện gpiozero:
- Khoảng cách < 20cm -> Quay thuận chậm (speed = 0.35)
- 20cm <= Khoảng cách <= 40cm -> Quay nghịch chậm (speed = 0.35)
- Khoảng cách > 40cm -> Quay thuận nhanh (speed = 0.90)

WIRING:
- HC-SR04 Trig: GPIO 23 | Echo: GPIO 24 (qua mạch chia áp) | VCC: 5V | GND: GND
- L298N ENA: GPIO 12 (PWM) - Nhớ tháo jumper chân ENA của L298N
- L298N IN1: GPIO 17
- L298N IN2: GPIO 27
- L298N GND: Chung GND với Raspberry Pi và nguồn motor ngoài.
=============================================================================
'''

from gpiozero import DistanceSensor, Motor
from time import sleep

# Khởi tạo cảm biến siêu âm với (echo, trigger) theo chuẩn BCM
# DistanceSensor mặc định trả về đơn vị là Mét (m)
sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

# Khởi tạo động cơ DC bằng lớp Motor của gpiozero:
# forward=(IN1), backward=(IN2), enable=(ENA - chân PWM)
motor = Motor(forward=17, backward=27, enable=12)

def main():
    """Vòng lặp chính đọc khoảng cách siêu âm và điều khiển động cơ bằng gpiozero."""
    print("Hệ thống điều khiển động cơ bằng siêu âm (gpiozero) đã sẵn sàng. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            # Đọc khoảng cách và quy đổi ra centimet (cm)
            distance_m = sensor.distance
            distance_cm = distance_m * 100
            
            print(f"Khoảng cách đo được: {distance_cm:.2f} cm")
            
            # Trường hợp 1: Khoảng cách < 20cm -> Quay thuận chậm (35%)
            if distance_cm < 20.0:
                motor.forward(speed=0.35)
                print("-> [Trường hợp 1] Khoảng cách < 20cm: Quay thuận chậm (35%)")
                
            # Trường hợp 2: Khoảng cách từ 20cm đến 40cm -> Quay nghịch chậm (35%)
            elif 20.0 <= distance_cm <= 40.0:
                motor.backward(speed=0.35)
                print("-> [Trường hợp 2] 20cm <= Khoảng cách <= 40cm: Quay nghịch chậm (35%)")
                
            # Trường hợp 3: Khoảng cách > 40cm -> Quay thuận nhanh (90%)
            else:
                motor.forward(speed=0.90)
                print("-> [Trường hợp 3] Khoảng cách > 40cm: Quay thuận nhanh (90%)")
                
            sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nĐang dừng động cơ và thoát chương trình...")
    finally:
        motor.stop()

if __name__ == '__main__':
    main()