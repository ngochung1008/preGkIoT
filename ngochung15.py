'''
=============================================================================
ĐỀ BÀI 15 VÀ YÊU CẦU HỆ THỐNG:
1. Đọc dữ liệu trực tuyến: Gửi HTTP Request tới wttr.in API (HTTP thường) 
   để lấy dữ liệu Tầm nhìn xa / Khoảng cách quan sát (Visibility - km) theo tên thành phố.
2. Không cần đăng ký tài khoản: Sử dụng API mở hoàn toàn miễn phí.
3. Điều khiển thiết bị: Dùng driver ULN2003 kết hợp thư viện RpiMotorLib 
   để điều khiển ĐỘNG CƠ BƯỚC (28BYJ-48) theo 3 điều kiện logic:
   - Trường hợp 1: Tầm nhìn / Khoảng cách < 5 km -> Quay THUẬN 90 độ.
   - Trường hợp 2: 5 km <= Tầm nhìn / Khoảng cách <= 10 km -> Quay NGHỊCH 180 độ.
   - Trường hợp 3: Tầm nhìn / Khoảng cách > 10 km -> Quay NGHỊCH 90 độ.
   - Trường hợp an toàn: Ngoài các điều kiện trên -> Động cơ đứng yên.

=============================================================================
SƠ ĐỒ LẮP MẠCH (WIRING GUIDE):
1. Mạch ULN2003 & Động cơ Bước 28BYJ-48:
   - Chân IN1: Nối vào GPIO 17
   - Chân IN2: Nối vào GPIO 18
   - Chân IN3: Nối vào GPIO 27
   - Chân IN4: Nối vào GPIO 22
   - Chân VCC (+): Nối vào chân 5V của Raspberry Pi
   - Chân GND (-): Nối vào chân GND của Raspberry Pi
   - Động cơ 28BYJ-48: Cắm jack 5 chân vào mạch ULN2003
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
    - direction: 'forward' (thuận) hoặc 'backward' (nghịch).
    """
    steps_to_take = int(degrees * (512 / 360))
    is_clockwise = True if direction == "forward" else False
    
    # stepper_motor.motor_run(gpiopins, stepdelay, steps, clockwise, verbose, steptype)
    stepper_motor.motor_run(pins, 0.002, steps_to_take, is_clockwise, False, "full")

def get_visibility_data(city_name):
    """
    Hàm gọi wttr.in qua HTTP thường để lấy Tầm nhìn xa / Khoảng cách (km) và Tốc độ gió (km/h).
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
        
        visibility_km = float(current_condition["visibility"])     # Tầm nhìn xa / Khoảng cách (km)
        wind_speed_kmph = float(current_condition["windspeedKmph"]) # Tốc độ gió (km/h)
        
        print(f"[+] Lấy dữ liệu thành công cho khu vực: {city_name}")
        return visibility_km, wind_speed_kmph
        
    except requests.exceptions.Timeout:
        print("[!] Lỗi: Hết thời gian chờ phản hồi từ máy chủ API (Timeout).")
        return None, None
    except Exception as e:
        print(f"[!] Lỗi kết nối hoặc phân tích JSON: {e}")
        return None, None

def main():
    """Vòng lặp chính: Web API Khoảng cách/Tầm nhìn -> Động cơ Bước."""
    print("==================================================")
    print(" HỆ THỐNG IOT: LẤY WEB API TẦM NHÌN/KHOẢNG CÁCH ĐIỀU KHIỂN ĐỘNG CƠ BƯỚC")
    print("==================================================")
    
    city = input("Nhập tên thành phố bạn muốn kiểm tra (Ví dụ: Da Nang, Hanoi, Tokyo, London): ").strip()
    
    if not city:
        city = "Da Nang"
        print(f"[*] Không nhập tên, hệ thống tự động chọn mặc định: {city}")

    print(f"\n[*] Đang kết nối mạng để lấy dữ liệu khoảng cách/tầm nhìn cho: {city}...")
    
    try:
        while True:
            visibility, wind_speed = get_visibility_data(city)
            
            if visibility is not None:
                print(f"--------------------------------------------------")
                print(f"📊 GIÁ TRỊ NHẬN TỪ WEB API:")
                print(f"🔭 Tầm nhìn xa (Khoảng cách) : {visibility} km")
                print(f"💨 Tốc độ gió                : {wind_speed} km/h")
                print(f"--------------------------------------------------")
                
                # THỰC HIỆN 3 ĐIỀU KIỆN ĐIỀU KHIỂN ĐỘNG CƠ BƯỚC:
                
                # Điều kiện 1: Tầm nhìn < 5 km -> Quay thuận 90 độ
                if visibility < 5.0:
                    print("-> [ĐIỀU KIỆN 1] Tầm nhìn < 5km: Quay THUẬN 90 độ")
                    rotate_angle(90, direction="forward")
                    
                # Điều kiện 2: 5 km <= Tầm nhìn <= 10 km -> Quay nghịch 180 độ
                elif 5.0 <= visibility <= 10.0:
                    print("-> [ĐIỀU KIỆN 2] 5km <= Tầm nhìn <= 10km: Quay NGHỊCH 180 độ")
                    rotate_angle(180, direction="backward")
                    
                # Điều kiện 3: Tầm nhìn > 10 km -> Quay nghịch 90 độ
                elif visibility > 10.0:
                    print("-> [ĐIỀU KIỆN 3] Tầm nhìn > 10km: Quay NGHỊCH 90 độ")
                    rotate_angle(90, direction="backward")
                    
                # Trường hợp an toàn khác -> Đứng yên
                else:
                    print("-> [AN TOÀN] Ngoài dải điều kiện: Động cơ đứng yên")
            else:
                print("[!] Chưa nhận được dữ liệu, đang thử kết nối lại sau 5 giây...")
                
            print("==================================================")
            time.sleep(30.0)
            
    except KeyboardInterrupt:
        print("\n[!] Đã ngắt chương trình. Đang dọn dẹp và thoát...")

if __name__ == '__main__':
    main()
