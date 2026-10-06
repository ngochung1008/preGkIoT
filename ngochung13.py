'''
=============================================================================
ĐỀ BÀI 13 VÀ YÊU CẦU HỆ THỐNG:
1. Đọc dữ liệu trực tuyến: Gửi HTTP Request tới wttr.in API (HTTP thường) 
   để lấy dữ liệu thời tiết (Nhiệt độ & Độ ẩm) theo tên thành phố nhập từ bàn phím.
2. Không cần đăng ký tài khoản: Sử dụng API mở hoàn toàn miễn phí.
3. Điều khiển thiết bị: Dùng thư viện gpiozero điều khiển ĐỘNG CƠ SERVO (SG90) 
   theo 3 điều kiện logic (quay đến góc mục tiêu trong 1 giây rồi hồi vị về 0°):
   - Trường hợp 1: Nhiệt độ < 18°C VÀ Độ ẩm < 75% -> Quay 45° trong 1s rồi về 0°.
   - Trường hợp 2: 18°C <= Nhiệt độ <= 20°C VÀ Độ ẩm >= 75% -> Quay 90° trong 1s rồi về 0°.
   - Trường hợp 3: Nhiệt độ > 20°C VÀ Độ ẩm >= 75% -> Quay 135° trong 1s rồi về 0°.
   - Trường hợp an toàn: Ngoài các điều kiện trên -> Giữ servo ở 0°.

=============================================================================
SƠ ĐỒ LẮP MẠCH (WIRING GUIDE):
1. Động cơ Servo SG90:
   - Dây Tín hiệu (Màu Cam hoặc Vàng): Nối vào GPIO 18 của Raspberry Pi
   - Dây Dương nguồn VCC (Màu Đỏ): Nối vào chân 5V của Raspberry Pi
   - Dây Âm nguồn GND (Màu Nâu hoặc Đen): Nối vào chân GND của Raspberry Pi
=============================================================================
'''

import time
import requests
from gpiozero import AngularServo

# Khởi tạo Động cơ Servo ở chân GPIO 18 với dải xung chuẩn cho SG90 (0.5ms - 2.5ms)
servo = AngularServo(
    18, 
    min_angle=0, 
    max_angle=180, 
    min_pulse_width=0.0005,  # 0.5 ms tương ứng 0 độ
    max_pulse_width=0.0025   # 2.5 ms tương ứng 180 độ
)

def get_weather_data(city_name):
    """
    Hàm gọi wttr.in qua HTTP thường để lấy Nhiệt độ (°C) và Độ ẩm (%).
    """
    try:
        url = f"http://wttr.in/{city_name}?format=j1"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"[!] Lỗi HTTP từ API: {response.status_code}")
            return None, None
            
        data = response.json()
        current_condition = data["current_condition"][0]
        
        temperature = float(current_condition["temp_C"])        # Nhiệt độ (°C)
        humidity = float(current_condition["humidity"])            # Độ ẩm (%)
        
        print(f"[+] Lấy dữ liệu thành công cho khu vực: {city_name}")
        return temperature, humidity
        
    except requests.exceptions.Timeout:
        print("[!] Lỗi: Hết thời gian chờ phản hồi từ máy chủ API (Timeout).")
        return None, None
    except Exception as e:
        print(f"[!] Lỗi kết nối hoặc phân tích JSON: {e}")
        return None, None

def main():
    """Vòng lặp chính của chương trình: Web API Nhiệt/Ẩm -> Động cơ Servo."""
    print("==================================================")
    print(" HỆ THỐNG IOT: LẤY WEB API THỜI TIẾT ĐIỀU KHIỂN ĐỘNG CƠ SERVO")
    print("==================================================")
    
    city = input("Nhập tên thành phố bạn muốn kiểm tra (Ví dụ: Da Nang, Hanoi, Tokyo, London): ").strip()
    
    if not city:
        city = "Da Nang"
        print(f"[*] Không nhập tên, hệ thống tự động chọn mặc định: {city}")

    print(f"\n[*] Đang kết nối mạng để lấy dữ liệu thời tiết cho khu vực: {city}...")
    
    try:
        while True:
            temperature, humidity = get_weather_data(city)
            
            if temperature is not None and humidity is not None:
                print(f"--------------------------------------------------")
                print(f"📊 GIÁ TRỊ NHẬN TỪ WEB API:")
                print(f"🌡️  Nhiệt độ hiện tại : {temperature}°C")
                print(f"💧 Độ ẩm hiện tại    : {humidity}%")
                print(f"--------------------------------------------------")
                
                target_angle = None
                
                # THỰC HIỆN 3 ĐIỀU KIỆN ĐIỀU KHIỂN SERVO:
                
                # Điều kiện 1: Nhiệt độ < 18°C VÀ Độ ẩm < 75% -> Quay 45°
                if temperature < 18.0 and humidity < 75.0:
                    target_angle = 45
                    print("-> [ĐIỀU KIỆN 1] Nhiệt độ < 18 & Độ ẩm < 75: Quay chuẩn 45°")
                    
                # Điều kiện 2: 18°C <= Nhiệt độ <= 20°C VÀ Độ ẩm >= 75% -> Quay 90°
                elif 18.0 <= temperature <= 20.0 and humidity >= 75.0:
                    target_angle = 90
                    print("-> [ĐIỀU KIỆN 2] 18 <= Temp <= 20 & Độ ẩm >= 75: Quay chuẩn 90°")
                    
                # Điều kiện 3: Nhiệt độ > 20°C VÀ Độ ẩm >= 75% -> Quay 135°
                elif temperature > 20.0 and humidity >= 75.0:
                    target_angle = 135
                    print("-> [ĐIỀU KIỆN 3] Nhiệt độ > 20 & Độ ẩm >= 75: Quay chuẩn 135°")
                    
                # Thực hiện quay góc chỉ định, giữ 1 giây rồi hồi vị về 0°
                if target_angle is not None:
                    servo.angle = target_angle
                    time.sleep(1.0)
                    servo.angle = 0
                    print("-> Servo đã hồi vị về 0°")
                else:
                    print("-> [AN TOÀN] Ngoài dải điều kiện: Servo giữ tại 0°")
                    servo.angle = 0
            else:
                print("[!] Chưa nhận được dữ liệu, đang thử kết nối lại sau 5 giây...")
                
            print("==================================================")
            time.sleep(30.0)
            
    except KeyboardInterrupt:
        print("\n[!] Đã ngắt chương trình. Đang dọn dẹp và thoát...")
    finally:
        servo.detach()

if __name__ == '__main__':
    main()
