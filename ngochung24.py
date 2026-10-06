'''
=============================================================================
ĐỀ BÀI 24: Web Server Flask tích hợp Gọi Web API Thời tiết & Giám sát DHT11 & Điều khiển Động cơ DC
1. Giao diện Web HTML thuần:
   - Có ô nhập tên thành phố (mặc định: Da Nang) và nút "Lấy dữ liệu thời tiết".
   - Hiển thị đầy đủ thông số thời tiết từ API wttr.in: Nhiệt độ, Độ ẩm, Lượng mưa (mm), Tầm nhìn (km), Tốc độ gió (km/h), Mô tả.
   - Hiển thị dữ liệu thực tế từ Cảm biến DHT11 (GPIO 4).
   - Bảng nút bấm điều khiển Động cơ DC qua mạch L298N (Thuận, Nghịch, Dừng, Tốc độ).

WIRING GUIDE:
- DHT11: DATA -> GPIO 4 | VCC -> 5V | GND -> GND
- L298N: ENA -> GPIO 12 (tháo jumper) | IN1 -> GPIO 17 | IN2 -> GPIO 27
- L298N GND -> Nối chung GND với Raspberry Pi và nguồn motor ngoài.
=============================================================================
'''

from flask import Flask, render_template_string, jsonify, request
import requests
import board
import adafruit_dht
from gpiozero import Motor

app = Flask(__name__)

# Khởi tạo cảm biến DHT11 tại GPIO 4
dht_device = adafruit_dht.DHT11(board.D4)

# Khởi tạo động cơ DC bằng gpiozero Motor (IN1=17, IN2=27, ENA=12)
motor = Motor(forward=17, backward=27, enable=12)

# Biến lưu trữ giá trị đọc DHT11 gần nhất
last_temp = 0.0
last_humi = 0.0

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bài 24 - Web Server API Thời tiết & DHT11 & Động cơ DC</title>
</head>
<body>
    <h1>HỆ THỐNG IOT: WEB API THỜI TIẾT + DHT11 + ĐỘNG CƠ DC</h1>
    <hr>
    
    <h2>1. THÔNG TIN THỜI TIẾT TỪ WEB API (WTTR.IN)</h2>
    <label for="city_input">Nhập tên thành phố: </label>
    <input type="text" id="city_input" value="Da Nang">
    <button onclick="fetchWeatherData()">Xem Thời Tiết</button>
    
    <p>Thành phố: <b id="api_city">Da Nang</b></p>
    <p>Tình trạng: <b id="api_desc">Đang tải...</b></p>
    <p>Nhiệt độ ngoài trời: <b id="api_temp">--</b> °C</p>
    <p>Độ ẩm ngoài trời: <b id="api_humi">--</b> %</p>
    <p>Lượng mưa: <b id="api_precip">--</b> mm</p>
    <p>Tầm nhìn xa: <b id="api_visibility">--</b> km</p>
    <p>Tốc độ gió: <b id="api_wind">--</b> km/h</p>
    
    <hr>
    <h2>2. THÔNG SỐ CẢM BIẾN PHẦN CỨNG DHT11 (TẠI PHÒNG)</h2>
    <p>Nhiệt độ cảm biến: <b id="sensor_temp">--</b> °C</p>
    <p>Độ ẩm cảm biến: <b id="sensor_humi">--</b> %</p>
    
    <hr>
    <h2>3. BẢNG ĐIỀU KHIỂN ĐỘNG CƠ DC</h2>
    <button onclick="controlMotor('forward', 0.35)">Quay Thuận Chậm (35%)</button>
    <button onclick="controlMotor('forward', 0.90)">Quay Thuận Nhanh (90%)</button>
    <button onclick="controlMotor('backward', 0.35)">Quay Nghịch Chậm (35%)</button>
    <button onclick="controlMotor('backward', 0.90)">Quay Nghịch Nhanh (90%)</button>
    <button onclick="controlMotor('stop', 0)">DỪNG ĐỘNG CƠ</button>
    
    <p>Trạng thái động cơ: <b id="motor_status">Đang dừng</b></p>

    <script>
        // Hàm lấy dữ liệu Web API thời tiết theo thành phố
        function fetchWeatherData() {
            var city = document.getElementById('city_input').value.trim();
            if (!city) city = 'Da Nang';
            
            fetch('/api/weather?city=' + encodeURIComponent(city))
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('api_city').innerText = data.city;
                        document.getElementById('api_desc').innerText = data.desc;
                        document.getElementById('api_temp').innerText = data.temp;
                        document.getElementById('api_humi').innerText = data.humidity;
                        document.getElementById('api_precip').innerText = data.precip_mm;
                        document.getElementById('api_visibility').innerText = data.visibility;
                        document.getElementById('api_wind').innerText = data.wind_kmph;
                    } else {
                        document.getElementById('api_desc').innerText = 'Lỗi: ' + data.error;
                    }
                })
                .catch(err => console.error(err));
        }

        // Tự động đọc dữ liệu cảm biến DHT11 mỗi 2 giây
        function fetchSensorData() {
            fetch('/get_sensor')
                .then(response => response.json())
                .then(data => {
                    if (data.temperature !== null) {
                        document.getElementById('sensor_temp').innerText = data.temperature;
                    }
                    if (data.humidity !== null) {
                        document.getElementById('sensor_humi').innerText = data.humidity;
                    }
                })
                .catch(err => console.error(err));
        }

        // Điều khiển động cơ DC
        function controlMotor(action, speed) {
            fetch('/motor/' + action + '?speed=' + speed)
                .then(response => response.text())
                .then(data => {
                    document.getElementById('motor_status').innerText = data;
                })
                .catch(err => console.error(err));
        }

        // Khởi chạy khi load trang
        fetchWeatherData();
        setInterval(fetchSensorData, 2000);
        fetchSensorData();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    """Trang chủ hiển thị giao diện HTML thuần."""
    return render_template_string(HTML_PAGE)

@app.route("/api/weather")
def api_weather():
    """API gọi wttr.in lấy thông tin thời tiết thành phố."""
    city = request.args.get('city', 'Da Nang')
    try:
        url = f"http://wttr.in/{city}?format=j1"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            curr = data["current_condition"][0]
            desc = curr.get("weatherDesc", [{}])[0].get("value", "Bình thường")
            return jsonify({
                "success": True,
                "city": city,
                "temp": curr.get("temp_C", "--"),
                "humidity": curr.get("humidity", "--"),
                "precip_mm": curr.get("precipMM", "--"),
                "visibility": curr.get("visibility", "--"),
                "wind_kmph": curr.get("windspeedKmph", "--"),
                "desc": desc
            })
        else:
            return jsonify({"success": False, "error": f"HTTP {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/get_sensor")
def get_sensor():
    """API trả về dữ liệu nhiệt độ và độ ẩm từ DHT11."""
    global last_temp, last_humi
    try:
        t = dht_device.temperature
        h = dht_device.humidity
        if t is not None:
            last_temp = t
        if h is not None:
            last_humi = h
    except Exception:
        pass
    return jsonify({"temperature": last_temp, "humidity": last_humi})

@app.route("/motor/<action>")
def control_motor(action):
    """API điều khiển động cơ DC."""
    speed = float(request.args.get('speed', 0.5))
    if action == "forward":
        motor.forward(speed=speed)
        return f"Động cơ đang quay THUẬN với tốc độ {int(speed * 100)}%"
    elif action == "backward":
        motor.backward(speed=speed)
        return f"Động cơ đang quay NGHỊCH với tốc độ {int(speed * 100)}%"
    elif action == "stop":
        motor.stop()
        return "Động cơ đã DỪNG."
    return "Lệnh không hợp lệ"

if __name__ == "__main__":
    try:
        print("Web Server đang chạy tại: http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        motor.stop()
        dht_device.exit()
