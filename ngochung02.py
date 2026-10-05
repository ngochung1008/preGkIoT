'''
=============================================================================
ĐỀ BÀI: Bài 2 - Nhấn 1 lần bật đèn, nhấn 2 lần liên tiếp (double-click) thì tắt đèn.
(Đang tắt nhấn 2 lần liên tiếp sẽ giữ nguyên tắt, không bị chớp sáng).
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
    """Vòng lặp chính: Xử lý nhấn 1 lần (BẬT) và nhấn 2 lần liên tiếp (TẮT không chớp)."""
    setup_hardware()
    
    led_state = False
    prev_button_state = GPIO.input(BUTTON_PIN)
    
    click_count = 0
    last_click_time = 0
    DOUBLE_CLICK_TIME = 0.35  # Ngưỡng thời gian nhận diện 2 lần nhấn (giây)
    waiting_for_double = False
    
    print("Chương trình đang chạy. Nhấn 1 lần: BẬT | Nhấn 2 lần liên tiếp: TẮT.")
    
    try:
        while True:
            curr_button_state = GPIO.input(BUTTON_PIN)
            current_time = time.time()
            
            # Phát hiện sự kiện nhấn nút (chuyển từ HIGH sang LOW)
            if prev_button_state == GPIO.HIGH and curr_button_state == GPIO.LOW:
                if current_time - last_click_time > DOUBLE_CLICK_TIME:
                    click_count = 0
                
                click_count += 1
                last_click_time = current_time
                
                if click_count == 1:
                    waiting_for_double = True
                elif click_count == 2:
                    # Nhấn 2 lần liên tiếp -> Tắt đèn ngay lập tức, hủy chờ đơn
                    waiting_for_double = False
                    led_state = False
                    GPIO.output(LED_PIN, GPIO.LOW)
                    print("Nhấn 2 lần liên tiếp -> LED: OFF (Giữ nguyên tắt)")
                    click_count = 0
                
                time.sleep(0.2)  # Chống dội phím (debounce)
            
            # Kiểm tra nếu hết thời gian chờ nhấn lần 2 mà chỉ có 1 lần nhấn
            if waiting_for_double and (current_time - last_click_time > DOUBLE_CLICK_TIME):
                waiting_for_double = False
                led_state = True
                GPIO.output(LED_PIN, GPIO.HIGH)
                print("Nhấn 1 lần -> LED: ON")
                click_count = 0
                
            prev_button_state = curr_button_state
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nThoát chương trình.")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()