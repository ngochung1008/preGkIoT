'''
=============================================================================
ĐỀ BÀI 14 VÀ YÊU CẦU HỆ THỐNG:
1. Đọc dữ liệu trực tuyến: Gửi HTTP Request tới wttr.in API (HTTP thường) 
   để lấy dữ liệu Tầm nhìn xa / Khoảng cách quan sát (Visibility - km) theo tên thành phố.
   (Dữ liệu tương đương chỉ số khoảng cách từ cảm biến siêu âm trong hệ thống IoT).
2. Không cần đăng ký tài khoản: Sử dụng API mở hoàn toàn miễn phí.
3. Điều khiển thiết bị: Dùng mạch L298N kết hợp thư viện gpiozero để điều khiển 
   ĐỘNG CƠ DC theo 3 điều kiện logic:
   - Trường hợp 1: Tầm nhìn / Khoảng cách < 5 km -> Quay thuận chậm (35%).
   - Trường hợp 2: 5 km <= Tầm nhìn / Khoảng cách <= 10 km -> Quay nghịch chậm (35%).
   - Trường hợp 3: Tầm nhìn / Khoảng cách > 10 km -> Quay thuận nhanh (90%).
   - Trường hợp an toàn: Ngoài các điều kiện trên -> Dừng động cơ (Stop).

=============================================================================
SƠ ĐỒ LẮP MẠCH (WIRING GUIDE):
1. Mạch L298N & Động cơ DC:
   - Chân ENA (PWM tốc độ): Nối vào GPIO 22 (hoặc GPIO 12, nhớ tháo jumper trên L298N)
   - Chân IN1 (Chiều quay 1): Nối vào GPIO 17
   - Chân IN2 (Chiều quay 2): Nối vào GPIO 27
   - Động cơ DC (Motor A): Nối trực tiếp vào 2 cực ngõ ra Motor A của L298N.
   - Nguồn cấp: Cấp nguồn ngoài cho L298N và [CỰC KỲ QUAN TRỌNG] nối chung GND với Raspberry Pi.
=============================================================================
'''

import time
import requests
from gpiozero import Motor

# Khởi tạo động cơ DC bằng thư viện gpiozero
# forward = IN1 (GPIO 17), backward = IN2 (GPIO 27), enable = ENA (GPIO 22)
motor = Motor(forward=17, backward=27, enable=22)

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
    """Vòng lặp chính của chương trình: Web API Khoảng cách/Tầm nhìn -> Động cơ DC."""
    print("==================================================")
    print(" HỆ THỐNG IOT: LẤY WEB API TẦM NHÌN/KHOẢNG CÁCH ĐIỀU KHIỂN ĐỘNG CƠ DC")
    print("==================================================")
    
    city = input("Nhập tên thành phố bạn muốn kiểm tra (Ví dụ: Hanoi, Da Nang, Tokyo, London): ").strip()
    
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
                
                # THỰC HIỆN 3 ĐIỀU KIỆN ĐIỀU KHIỂN ĐỘNG CƠ DC:
                
                # Điều kiện 1: Tầm nhìn < 5 km -> Quay thuận chậm (35%)
                if visibility < 5.0:
                    motor.forward(speed=0.35)
                    print("-> [ĐIỀU KIỆN 1] Tầm nhìn < 5km (Gần/Sương mù): Quay thuận chậm (35%)")
                    
                # Điều kiện 2: 5 km <= Tầm nhìn <= 10 km -> Quay nghịch chậm (35%)
                elif 5.0 <= visibility <= 10.0:
                    motor.backward(speed=0.35)
                    print("-> [ĐIỀU KIỆN 2] 5km <= Tầm nhìn <= 10km (Trung bình): Quay nghịch chậm (35%)")
                    
                # Điều kiện 3: Tầm nhìn > 10 km -> Quay thuận nhanh (90%)
                elif visibility > 10.0:
                    motor.forward(speed=0.90)
                    print("-> [ĐIỀU KIỆN 3] Tầm nhìn > 10km (Xa/Thoáng): Quay thuận nhanh (90%)")
                    
                # Trường hợp an toàn khác -> Dừng động cơ
                else:
                    motor.stop()
                    print("-> [AN TOÀN] Ngoài dải điều kiện: Dừng động cơ (Stop)")
            else:
                print("[!] Chưa nhận được dữ liệu, đang thử kết nối lại sau 5 giây...")
                motor.stop()
                
            print("==================================================")
            time.sleep(30.0)
            
    except KeyboardInterrupt:
        print("\n[!] Đã ngắt chương trình. Đang dọn dẹp và thoát...")
    finally:
        motor.stop()

if __name__ == '__main__':
    main()
