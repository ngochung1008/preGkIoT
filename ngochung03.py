'''
=============================================================================
ĐỀ BÀI: Bài 3 - Sử dụng cảm biến nhiệt độ - độ ẩm (DHT11) bật/tắt đèn.
Điều kiện: Nhiệt độ > 30.0°C VÀ Độ ẩm > 70.0% -> Bật LED, Ngược lại -> Tắt.
WIRING:
- LED (+): qua điện trở 220Ω -> GPIO 18
- LED (-): GND
- DHT11 VCC: 5V
- DHT11 GND: GND
- DHT11 DATA: GPIO 4
=============================================================================
'''

import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

# Khởi tạo cảm biến DHT11 ở chân GPIO 4 (board.D4 tương ứng với GPIO 4)
dht_device = adafruit_dht.DHT11(board.D4)

LED_PIN = 18
TEMP_THRESHOLD = 30.0  # Ngưỡng nhiệt độ (°C)
HUMI_THRESHOLD = 70.0  # Ngưỡng độ ẩm (%)

def setup_hardware():
    """Cấu hình chân GPIO cho LED (Output)."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)

def main():
    """Vòng lặp chính: Đọc dữ liệu từ DHT11 và điều khiển LED theo điều kiện."""
    setup_hardware()
    
    print(f"Điều kiện bật LED: Nhiệt độ > {TEMP_THRESHOLD}°C VÀ Độ ẩm > {HUMI_THRESHOLD}%")
    print("Đang đọc dữ liệu từ cảm biến. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            try:
                # Đọc giá trị nhiệt độ và độ ẩm từ cảm biến
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                
                if temperature is not None and humidity is not None:
                    print(f"Nhiệt độ: {temperature:.1f}°C | Độ ẩm: {humidity:.1f}%")
                    
                    # Kiểm tra điều kiện đồng thời cả nhiệt độ và độ ẩm
                    if temperature > TEMP_THRESHOLD and humidity > HUMI_THRESHOLD:
                        GPIO.output(LED_PIN, GPIO.HIGH)
                        print("-> Đạt điều kiện: Bật LED (Nóng & Ẩm cao!)")
                    else:
                        GPIO.output(LED_PIN, GPIO.LOW)
                        print("-> Không đạt điều kiện: Tắt LED")
                else:
                    print("Đang chờ dữ liệu từ cảm biến...")
                    
            except RuntimeError as error:
                # DHT11 hay báo lỗi timing (bình thường), catch lại để đọc tiếp ở chu kỳ sau
                print(f"Lỗi đọc cảm biến (bình thường): {error.args[0]}")
                
            # DHT11 yêu cầu thời gian nghỉ tối thiểu 2 giây giữa mỗi lần đọc
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    finally:
        dht_device.exit()
        GPIO.cleanup()

if __name__ == '__main__':
    main()