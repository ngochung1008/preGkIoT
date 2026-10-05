'''
=============================================================================
ĐỀ BÀI: Bài 4 - Sử dụng thư viện gpiozero với cảm biến siêu âm HC-SR04 bật/tắt đèn.
Điều kiện: Khoảng cách từ 20cm đến 30cm (0.2m - 0.3m) -> Bật LED, Ngược lại -> Tắt.
WIRING:
- LED (+): qua điện trở 220Ω -> GPIO 18
- LED (-): GND
- HC-SR04 VCC: 5V
- HC-SR04 GND: GND
- HC-SR04 Trig: GPIO 23
- HC-SR04 Echo: qua mạch phân áp -> GPIO 24
=============================================================================
'''

from gpiozero import DistanceSensor, LED
from time import sleep

# Khởi tạo cảm biến siêu âm với (echo, trigger) theo chuẩn BCM
# Lưu ý: DistanceSensor của gpiozero mặc định trả về đơn vị là Mét (m)
sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)
led = LED(18)

# Quy đổi khoảng cách từ cm sang mét cho dễ cấu hình
DIST_MIN_M = 0.20  # 20 cm
DIST_MAX_M = 0.30  # 30 cm

def main():
    """Vòng lặp chính: Đọc khoảng cách bằng gpiozero và điều khiển LED."""
    print("Đang chạy chương trình đo khoảng cách bằng thư viện gpiozero. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            # Lấy giá trị khoảng cách (đơn vị: mét)
            distance_m = sensor.distance
            distance_cm = distance_m * 100
            
            print(f"Khoảng cách: {distance_cm:.2f} cm")
            
            # Kiểm tra điều kiện trong khoảng từ 20cm đến 30cm
            if DIST_MIN_M <= distance_m <= DIST_MAX_M:
                led.on()
                print("-> Trong khoảng 20-30cm: Bật LED")
            else:
                led.off()
                print("-> Ngoài khoảng 20-30cm: Tắt LED")
                
            sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nThoát chương trình.")

if __name__ == '__main__':
    main()