'''
=============================================================================
ĐỀ BÀI 12 VÀ YÊU CẦU HỆ THỐNG:
1. Đọc dữ liệu trực tuyến: Gửi HTTP Request tới wttr.in API (HTTP thường) 
   để lấy dữ liệu thời tiết (Nhiệt độ & Độ ẩm) theo tên thành phố nhập từ bàn phím.
2. Không cần đăng ký tài khoản: Sử dụng API mở hoàn toàn miễn phí.
3. Điều khiển thiết bị: Dùng mạch điều khiển ULN2003 kết hợp thư viện RpiMotorLib 
   để điều khiển ĐỘNG CƠ BƯỚC (28BYJ-48) theo 3 điều kiện logic:
   - Trường hợp 1: Nhiệt độ < 18°C VÀ Độ ẩm < 75% -> Quay THUẬN 90 độ.
   - Trường hợp 2: 18°C <= Nhiệt độ <= 20°C VÀ Độ ẩm >= 75% -> Quay NGHỊCH 180 độ.
   - Trường hợp 3: Nhiệt độ > 20°C VÀ Độ ẩm >= 75% -> Quay NGHỊCH 90 độ.
   - Trường hợp an toàn: Ngoài các điều kiện trên -> Đứng yên.

=============================================================================
SƠ ĐỒ LẮP MẠCH (WIRING GUIDE):
1. Mạch ULN2003 & Động cơ Bước 28BYJ-48:
   - Chân IN1: Nối vào GPIO 17
   - Chân IN2: Nối vào GPIO 18
   - Chân IN3: Nối vào GPIO 27
   - Chân IN4: Nối vào GPIO 22
   - Chân VCC (+): Nối vào chân 5V của Raspberry Pi (hoặc nguồn ngoài 5V)
   - Chân GND (-): Nối vào chân GND của Raspberry Pi
   - Động cơ 28BYJ-48: Cắm trực tiếp jack 5 chân vào mạch ULN2003
=============================================================================
'''

import time
import requests
from RpiMotorLib import RpiMotorLib

# Khai báo danh sách các chân GPIO nối với driver ULN2003 theo thứ tự (IN1, IN2, IN3, IN4)
pins = [17, 18, 27, 22]

# Khởi tạo đối tượng động cơ bước 28BYJ-48 bằng thư viện RpiMotorLib
stepper_motor = RpiMotorLib.BYJMotor("MyStepper", "28BYJ")

def rotate_angle(degrees, direction="forward"):
    """
    Hàm quay động cơ bước theo góc độ và hướng sử dụng thư viện RpiMotorLib.
    - 28BYJ-48 ở chế độ full-step có 512 bước cho 1 vòng 360 độ.
    - direction: 'forward' (thuận - kim đồng hồ) hoặc 'backward' (nghịch - ngược kim đồng hồ).
    """
    steps_to_take = int(degrees * (512 / 360))
    is_clockwise = True if direction == "forward" else False
    
    # stepper_motor.motor_run(gpiopins, stepdelay, steps, clockwise, verbose, steptype)
    stepper_motor.motor_run(pins, 0.002, steps_to_take, is_clockwise, False, "full")

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
    """Vòng lặp chính của chương trình: Web API Nhiệt/Ẩm -> Động cơ Bước."""
    print("==================================================")
    print(" HỆ THỐNG IOT: LẤY WEB API THỜI TIẾT ĐIỀU KHIỂN ĐỘNG CƠ BƯỚC")
    print("==================================================")
    
    city = input("Nhập tên thành phố bạn muốn kiểm tra (Ví dụ: Hanoi, Da Nang, Tokyo, London): ").strip()
    
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
                
                # THỰC HIỆN 3 ĐIỀU KIỆN ĐIỀU KHIỂN ĐỘNG CƠ BƯỚC:
                
                # Điều kiện 1: Nhiệt độ < 18°C VÀ Độ ẩm < 75% -> Quay thuận 90 độ
                if temperature < 18.0 and humidity < 75.0:
                    print("-> [ĐIỀU KIỆN 1] Nhiệt độ < 18 & Độ ẩm < 75: Quay THUẬN 90 độ")
                    rotate_angle(90, direction="forward")
                    
                # Điều kiện 2: 18°C <= Nhiệt độ <= 20°C VÀ Độ ẩm >= 75% -> Quay nghịch 180 độ
                elif 18.0 <= temperature <= 20.0 and humidity >= 75.0:
                    print("-> [ĐIỀU KIỆN 2] 18 <= Temp <= 20 & Độ ẩm >= 75: Quay NGHỊCH 180 độ")
                    rotate_angle(180, direction="backward")
                    
                # Điều kiện 3: Nhiệt độ > 20°C VÀ Độ ẩm >= 75% -> Quay nghịch 90 độ
                elif temperature > 20.0 and humidity >= 75.0:
                    print("-> [ĐIỀU KIỆN 3] Nhiệt độ > 20 & Độ ẩm >= 75: Quay NGHỊCH 90 độ")
                    rotate_angle(90, direction="backward")
                    
                # Trường hợp an toàn khác -> Đứng yên
                else:
                    print("-> [AN TOÀN] Ngoài dải điều kiện thiết lập: Động cơ đứng yên")
            else:
                print("[!] Chưa nhận được dữ liệu, đang thử kết nối lại sau 5 giây...")
                
            print("==================================================")
            time.sleep(30.0)
            
    except KeyboardInterrupt:
        print("\n[!] Đã ngắt chương trình. Đang dọn dẹp và thoát...")

if __name__ == '__main__':
    main()
