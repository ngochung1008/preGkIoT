'''
=============================================================================
ĐỀ BÀI: Điều khiển động cơ bước (28BYJ-48) qua DHT11 dùng thư viện RpiMotorLib:
- Nhiệt độ < 28°C VÀ Độ ẩm < 75% -> Quay thuận 90 độ
- 28°C <= Nhiệt độ <= 32°C VÀ Độ ẩm >= 75% -> Quay nghịch 180 độ
- Nhiệt độ > 32°C VÀ Độ ẩm >= 75% -> Quay nghịch 90 độ

WIRING:
- DHT11 DATA: GPIO 4 | VCC: 5V | GND: GND
- ULN2003 IN1 -> GPIO 17, IN2 -> GPIO 18, IN3 -> GPIO 27, IN4 -> GPIO 22
- ULN2003 VCC: 5V | GND: GND
=============================================================================
'''

import time
import board
import adafruit_dht
from RpiMotorLib import RpiMotorLib

# Khởi tạo cảm biến DHT11 ở chân GPIO 4
dht_device = adafruit_dht.DHT11(board.D4)

# Khai báo danh sách các chân GPIO nối với driver ULN2003 theo thứ tự (IN1, IN2, IN3, IN4)
pins = [17, 18, 27, 22]

# Khởi tạo đối tượng động cơ bước 28BYJ-48 bằng thư viện RpiMotorLib
# Tên đối tượng tùy ý, kiểu truyền vào là "28BYJ"
stepper_motor = RpiMotorLib.BYJMotor("MyStepper", "28BYJ")

def rotate_angle(degrees, direction="forward"):
    """Hàm quay động cơ theo góc độ và hướng sử dụng thư viện."""
    # 28BYJ-48 ở chế độ full-step có 512 bước cho một vòng (360 độ).
    # Tính số bước tương ứng với góc quay (ví dụ: 90 độ = 128 bước, 180 độ = 256 bước)
    steps_to_take = int(degrees * (512 / 360))
    
    # Thiết lập chiều quay cho thư viện ('True' là thuận, 'False' là nghịch)
    is_clockwise = True if direction == "forward" else False
    
    # Gọi hàm motor_run của thư viện với: 
    # (danh sách chân, tốc độ bước/delay, số bước, chiều quay, kiểu chạy, kiểu ngắt điện cuối)
    stepper_motor.motor_run(pins, 0.002, steps_to_take, is_clockwise, False, "full")

def main():
    """Vòng lặp chính đọc cảm biến và điều khiển động cơ bước bằng thư viện."""
    print("Hệ thống Động cơ bước (RpiMotorLib) & DHT11 đã sẵn sàng. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            try:
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                
                if temperature is not None and humidity is not None:
                    print(f"Nhiệt độ: {temperature:.1f}°C | Độ ẩm: {humidity:.1f}%")
                    
                    # Điều kiện 1: Nhiệt độ < 28°C VÀ Độ ẩm < 75% -> Quay thuận 90 độ
                    if temperature < 28.0 and humidity < 75.0:
                        print("-> [Trường hợp 1] Quay THUẬN 90 độ")
                        rotate_angle(90, direction="forward")
                        
                    # Điều kiện 2: 28°C <= Nhiệt độ <= 32°C VÀ Độ ẩm >= 75% -> Quay nghịch 180 độ
                    elif 28.0 <= temperature <= 32.0 and humidity >= 75.0:
                        print("-> [Trường hợp 2] Quay NGHỊCH 180 độ")
                        rotate_angle(180, direction="backward")
                        
                    # Điều kiện 3: Nhiệt độ > 32°C VÀ Độ ẩm >= 75% -> Quay nghịch 90 độ
                    elif temperature > 32.0 and humidity >= 75.0:
                        print("-> [Trường hợp 3] Quay NGHỊCH 90 độ")
                        rotate_angle(90, direction="backward")
                        
                    else:
                        print("-> Ngoài vùng điều kiện: Động cơ đứng yên.")
                else:
                    print("Đang chờ dữ liệu từ cảm biến...")
                    
            except RuntimeError as error:
                print(f"Lỗi đọc cảm biến (bình thường): {error.args[0]}")
                
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    finally:
        dht_device.exit()

if __name__ == '__main__':
    main()