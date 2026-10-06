'''
=============================================================================
ĐỀ BÀI 16 VÀ YÊU CẦU HỆ THỐNG:
1. Đọc dữ liệu trực tuyến: Gửi HTTP Request tới wttr.in API (HTTP thường) 
   để lấy dữ liệu Tầm nhìn xa / Khoảng cách quan sát (Visibility - km) theo tên thành phố.
2. Không cần đăng ký tài khoản: Sử dụng API mở hoàn toàn miễn phí.
3. Điều khiển thiết bị: Dùng thư viện gpiozero điều khiển ĐỘNG CƠ SERVO (SG90) 
   theo 3 điều kiện logic (quay đến góc mục tiêu trong 1 giây rồi hồi vị về 0°):
   - Trường hợp 1: Tầm nhìn / Khoảng cách < 5 km -> Quay 45° trong 1s rồi về 0°.
   - Trường hợp 2: 5 km <= Tầm nhìn / Khoảng cách <= 10 km -> Quay 90° trong 1s rồi về 0°.
   - Trường hợp 3: Tầm nhìn / Khoảng cách > 10 km -> Quay 135° trong 1s rồi về 0°.
   - Trường hợp an toàn: Ngoài các điều kiện trên -> Giữ servo ở 0°.

=============================================================================
SƠ ĐỒ LẮP MẠCH (WIRING GUIDE):
1. Động cơ Servo SG90:
   - Dây Tín hiệu (Cam/Vàng): Nối vào GPIO 18
   - Dây VCC (Đỏ): Nối vào chân 5V của Raspberry Pi
   - Dây GND (Nâu/Đen): Nối vào chân GND của Raspberry Pi
=============================================================================
'''

import time
import requests
from gpiozero import AngularServo

# Khởi tạo Động cơ Servo ở chân GPIO 18 với dải xung chuẩn cho SG90
servo = AngularServo(
    18, 
    min_angle=0, 
    max_angle=180, 
    min_pulse_width=0.0005,  # 0.5 ms tương ứng 0 độ
    max_pulse_width=0.0025   # 2.5 ms tương ứng 180 độ
)

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
    """Vòng lặp chính: Web API Khoảng cách/Tầm nhìn -> Động cơ Servo."""
    print("==================================================")
    print(" HỆ THỐNG IOT: LẤY WEB API TẦM NHÌN/KHOẢNG CÁCH ĐIỀU KHIỂN ĐỘNG CƠ SERVO")
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
                
                target_angle = None
                
                # THỰC HIỆN 3 ĐIỀU KIỆN ĐIỀU KHIỂN SERVO:
                
                # Điều kiện 1: Tầm nhìn < 5 km -> Quay 45°
                if visibility < 5.0:
                    target_angle = 45
                    print("-> [ĐIỀU KIỆN 1] Tầm nhìn < 5km: Quay chuẩn 45°")
                    
                # Điều kiện 2: 5 km <= Tầm nhìn <= 10 km -> Quay 90°
                elif 5.0 <= visibility <= 10.0:
                    target_angle = 90
                    print("-> [ĐIỀU KIỆN 2] 5km <= Tầm nhìn <= 10km: Quay chuẩn 90°")
                    
                # Điều kiện 3: Tầm nhìn > 10 km -> Quay 135°
                elif visibility > 10.0:
                    target_angle = 135
                    print("-> [ĐIỀU KIỆN 3] Tầm nhìn > 10km: Quay chuẩn 135°")
                    
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
