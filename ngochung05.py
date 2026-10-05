'''
=============================================================================
ĐỀ BÀI: Bài 5 - Điều khiển động cơ DC qua cảm biến DHT11 (dùng thư viện gpiozero):
- Nhiệt độ < 28°C VÀ Độ ẩm < 75% -> Quay thuận chậm (speed = 0.35)
- 28°C <= Nhiệt độ <= 32°C VÀ Độ ẩm >= 75% -> Quay nghịch chậm (speed = -0.35)
- Nhiệt độ > 32°C VÀ Độ ẩm >= 75% -> Quay thuận nhanh (speed = 0.90)
- Các trường hợp khác -> Dừng động cơ (Stop)

WIRING:
- DHT11 DATA: GPIO 4 | VCC: 5V | GND: GND
- L298N ENA: GPIO 12 (PWM)
- L298N IN1: GPIO 17
- L298N IN2: GPIO 27
- L298N GND: Chung GND với Raspberry Pi và nguồn motor ngoài.
(Nhớ tháo jumper chân ENA của L298N để cắm vào GPIO 12).
=============================================================================
'''

import time
import board
import adafruit_dht
from gpiozero import Motor

# Khởi tạo cảm biến DHT11 ở chân GPIO 4
dht_device = adafruit_dht.DHT11(board.D4)

# Khởi tạo động cơ DC bằng thư viện gpiozero Motor
# forward=(IN1_PIN), backward=(IN2_PIN), enable=(ENA_PIN) với giá trị PWM
motor = Motor(forward=17, backward=27, enable=12)

def main():
    """Vòng lặp chính đọc cảm biến và điều khiển động cơ DC bằng gpiozero."""
    print("Hệ thống điều khiển động cơ (gpiozero) & DHT11 đã sẵn sàng. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            try:
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                
                if temperature is not None and humidity is not None:
                    print(f"Nhiệt độ: {temperature:.1f}°C | Độ ẩm: {humidity:.1f}%")
                    
                    # Trường hợp 1: Nhiệt độ < 28°C VÀ Độ ẩm < 75% -> Quay thuận chậm (0.35)
                    if temperature < 28.0 and humidity < 75.0:
                        motor.forward(speed=0.35)
                        print("-> [Trường hợp 1] Nhiệt độ < 28 & Độ ẩm < 75: Quay thuận chậm (35%)")
                        
                    # Trường hợp 2: 28°C <= Nhiệt độ <= 32°C VÀ Độ ẩm >= 75% -> Quay nghịch chậm (0.35)
                    elif 28.0 <= temperature <= 32.0 and humidity >= 75.0:
                        motor.backward(speed=0.35)
                        print("-> [Trường hợp 2] 28 <= Nhiệt độ <= 32 & Độ ẩm >= 75: Quay nghịch chậm (35%)")
                        
                    # Trường hợp 3: Nhiệt độ > 32°C VÀ Độ ẩm >= 75% -> Quay thuận nhanh (0.90)
                    elif temperature > 32.0 and humidity >= 75.0:
                        motor.forward(speed=0.90)
                        print("-> [Trường hợp 3] Nhiệt độ > 32 & Độ ẩm >= 75: Quay thuận nhanh (90%)")
                        
                    # Các trường hợp ngoài vùng điều kiện -> Dừng động cơ
                    else:
                        motor.stop()
                        print("-> [An toàn] Ngoài điều kiện thiết lập: Dừng động cơ")
                else:
                    print("Đang chờ dữ liệu từ cảm biến...")
                    
            except RuntimeError as error:
                print(f"Lỗi đọc cảm biến (bình thường): {error.args[0]}")
                
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\nĐang dừng động cơ và thoát chương trình...")
    finally:
        motor.stop()
        dht_device.exit()

if __name__ == '__main__':
    main()