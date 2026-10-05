'''
=============================================================================
ĐỀ BÀI: Bài 1 - Sử dụng Raspberry Pi bật tắt đèn thông qua button (2 chân).
WIRING:
- LED (+): qua điện trở 220Ω -> GPIO 18
- LED (-): GND
- Button chân 1: GPIO 23
- Button chân 2: GND (dùng pull-up nội bộ)
=============================================================================
'''

import RPi.GPIO as GPIO
import time

LED_PIN = 18
BUTTON_PIN = 23

def setup_hardware():
    """Cấu hình chân GPIO cho LED (Output) và Button (Input pull-up)."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)
    
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    """Vòng lặp chính: Đọc nút nhấn để bật/tắt LED (toggle)."""
    setup_hardware()
    
    led_state = False
    prev_state = GPIO.input(BUTTON_PIN)
    
    print("Chương trình đang chạy. Nhấn Ctrl+C để thoát.")
    
    try:
        while True:
            curr_state = GPIO.input(BUTTON_PIN)
            
            # Phát hiện sự kiện nhấn nút (chuyển từ HIGH sang LOW)
            if prev_state == GPIO.HIGH and curr_state == GPIO.LOW:
                led_state = not led_state
                GPIO.output(LED_PIN, GPIO.HIGH if led_state else GPIO.LOW)
                print(f"LED: {'ON' if led_state else 'OFF'}")
                time.sleep(0.2)  # Chống dội phím (debounce)
                
            prev_state = curr_state
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()