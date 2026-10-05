'''
=============================================================================
ĐỀ BÀI VÀ YÊU CẦU HỆ THỐNG:
1. Đọc dữ liệu trực tuyến: Gửi HTTP Request tới wttr.in API (dùng HTTP thường) 
   để lấy dữ liệu thời tiết (Nhiệt độ & Độ ẩm) theo tên thành phố nhập từ bàn phím.
2. Không cần đăng ký tài khoản: Sử dụng API mở hoàn toàn miễn phí.
3. Điều khiển thiết bị: Dùng mạch L298N kết hợp thư viện gpiozero để điều khiển 
   động cơ DC theo đúng 3 điều kiện logic (đã hiệu chỉnh theo nhiệt độ thực tế):
   - Trường hợp 1: Nhiệt độ < 18°C VÀ Độ ẩm < 75% -> Quay thuận chậm (35%).
   - Trường hợp 2: 18°C <= Nhiệt độ <= 20°C VÀ Độ ẩm >= 75% -> Quay nghịch chậm (35%).
   - Trường hợp 3: Nhiệt độ > 20°C VÀ Độ ẩm >= 75% -> Quay thuận nhanh (90%).
   - Trường hợp an toàn: Ngoài các điều kiện trên -> Dừng động cơ (Stop).

=============================================================================
SƠ ĐỒ LẮP MẠCH (WIRING GUIDE):
1. Mạch L298N & Động cơ DC:
   - Chân ENA (PWM tốc độ): Nối vào GPIO 22 (Nhớ tháo jumper màu đen trên L298N)
   - Chân IN1 (Chiều quay 1): Nối vào GPIO 17
   - Chân IN2 (Chiều quay 2): Nối vào GPIO 27
   - Động cơ DC (Motor A): Nối trực tiếp vào 2 cực ngõ ra Motor A của L298N.
   - Nguồn cấp: Cấp nguồn ngoài (pin 9V hoặc nguồn 12V) cho L298N. 
     [CỰC KỲ QUAN TRỌNG]: Phải nối chung chân GND của nguồn ngoài với chân GND của Raspberry Pi.
=============================================================================
'''

import time
import requests
from gpiozero import Motor

# Khởi tạo động cơ DC bằng thư viện gpiozero
# forward = IN1 (GPIO 17), backward = IN2 (GPIO 27), enable = ENA (GPIO 22)
motor = Motor(forward=17, backward=27, enable=22)

def get_weather_data(city_name):
    """
    Hàm gọi wttr.in qua HTTP thường (tránh triệt để lỗi SSL EOF trên Raspberry Pi).
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
    """Vòng lặp chính của chương trình"""
    print("==================================================")
    print(" HỆ THỐNG IOT: LẤY DỮ LIỆU WEB API ĐIỀU KHIỂN ĐỘNG CƠ")
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
                
                # THỰC HIỆN 3 ĐIỀU KIỆN ĐÃ ĐIỀU CHỈNH NGƯỠNG:
                
                # Điều kiện 1: Nhiệt độ < 18°C VÀ Độ ẩm < 75% -> Quay thuận chậm (35%)
                if temperature < 18.0 and humidity < 75.0:
                    motor.forward(speed=0.35)
                    print("-> [ĐIỀU KIỆN 1] Nhiệt độ < 18 & Độ ẩm < 75: Quay thuận chậm (35%)")
                    
                # Điều kiện 2: 18°C <= Nhiệt độ <= 20°C VÀ Độ ẩm >= 75% -> Quay nghịch chậm (35%)
                elif 18.0 <= temperature <= 20.0 and humidity >= 75.0:
                    motor.backward(speed=0.35)
                    print("-> [ĐIỀU KIỆN 2] 18 <= temperature <= 20 & Độ ẩm >= 75: Quay nghịch chậm (35%)")
                    
                # Điều kiện 3: Nhiệt độ > 20°C VÀ Độ ẩm >= 75% -> Quay thuận nhanh (90%)
                # (Với nhiệt độ Hà Nội hiện tại ~23°C và độ ẩm 91%, điều kiện này sẽ kích hoạt ngay lập tức!)
                elif temperature > 20.0 and humidity >= 75.0:
                    motor.forward(speed=0.90)
                    print("-> [ĐIỀU KIỆN 3] Nhiệt độ > 20 & Độ ẩm >= 75: Quay thuận nhanh (90%)")
                    
                # Trường hợp an toàn khác -> Dừng động cơ
                else:
                    motor.stop()
                    print("-> [AN TOÀN] Ngoài dải điều kiện thiết lập: Dừng động cơ (Stop)")
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