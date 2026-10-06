'''
=============================================================================
ĐỀ BÀI 29: Web Server Flask tích hợp Gọi Web API Thời tiết & Giám sát Siêu âm & Động cơ Servo
1. Giao diện Web HTML thuần:
   - Có ô nhập tên thành phố và nút "Xem Thời Tiết".
   - Hiển thị thông số thời tiết từ wttr.in: Nhiệt độ, Độ ẩm, Lượng mưa, Tầm nhìn, Gió, Tình trạng.
   - Hiển thị khoảng cách thực tế từ Cảm biến Siêu âm HC-SR04 (Trig=23, Echo=24).
   - Bảng nút bấm chọn góc nhanh (0°, 45°, 90°, 135°, 180°) và thanh trượt góc điều khiển Servo SG90.

WIRING GUIDE:
- HC-SR04: Trig -> GPIO 23 | Echo -> GPIO 24 (qua mạch chia áp) | VCC -> 5V | GND -> GND
- Servo SG90: Signal (Cam/Vàng) -> GPIO 18 | VCC (Đỏ) -> 5V | GND (Nâu/Đen) -> GND
=============================================================================
'''

from flask import Flask, render_template_string, jsonify, request
import requests
from gpiozero import DistanceSensor, AngularServo

app = Flask(__name__)

# Khởi tạo cảm biến siêu âm HC-SR04
sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

# Khởi tạo Servo tại GPIO 18 với dải xung chuẩn SG90
servo = AngularServo(
    18, 
    min_angle=0, 
    max_angle=180, 
    min_pulse_width=0.0005, 
    max_pulse_width=0.0025
)

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bài 29 - Web Server API Thời tiết & Siêu âm & Động cơ Servo</title>
</head>
<body>
    <h1>HỆ THỐNG IOT: WEB API THỜI TIẾT + SIÊU ÂM + ĐỘNG CƠ SERVO</h1>
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
    <h2>2. THÔNG SỐ CẢM BIẾN SIÊU ÂM HC-SR04 (THỰC TẾ)</h2>
    <p>Khoảng cách đo được: <b id="dist_val">--</b> cm</p>
    
    <hr>
    <h2>3. BẢNG ĐIỀU KHIỂN ĐỘNG CƠ SERVO (SG90)</h2>
    <p>
        <b>Nút chọn góc nhanh:</b><br><br>
        <button onclick="setServoAngle(0)">0°</button>
        <button onclick="setServoAngle(45)">45°</button>
        <button onclick="setServoAngle(90)">90°</button>
        <button onclick="setServoAngle(135)">135°</button>
        <button onclick="setServoAngle(180)">180°</button>
    </p>
    <p>
        <b>Thanh trượt góc (0° - 180°):</b><br><br>
        <input type="range" id="servo_slider" min="0" max="180" value="90" onchange="setServoAngle(this.value)">
        <span id="slider_val">90°</span>
    </p>
    
    <p>Trạng thái Servo: <b id="servo_status">Đang sẵn sàng tại 0°</b></p>

    <script>
        // Lấy thông tin thời tiết từ API
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

        // Tự động đọc khoảng cách mỗi 1 giây
        function fetchDistance() {
            fetch('/get_distance')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('dist_val').innerText = data.distance;
                })
                .catch(err => console.error(err));
        }

        // Điều khiển góc Servo
        function setServoAngle(angle) {
            document.getElementById('servo_slider').value = angle;
            document.getElementById('slider_val').innerText = angle + '°';
            fetch('/servo/' + angle)
                .then(response => response.text())
                .then(data => {
                    document.getElementById('servo_status').innerText = data;
                })
                .catch(err => console.error(err));
        }

        // Khởi chạy
        fetchWeatherData();
        setInterval(fetchDistance, 1000);
        fetchDistance();
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

@app.route("/get_distance")
def get_distance():
    """API trả về khoảng cách đo được tính bằng cm dạng JSON."""
    distance_cm = round(sensor.distance * 100, 1)
    return jsonify({"distance": distance_cm})

@app.route("/servo/<int:angle>")
def control_servo(angle):
    """API xoay động cơ Servo đến góc chỉ định."""
    if 0 <= angle <= 180:
        servo.angle = angle
        return f"Đã xoay Servo đến góc {angle}°"
    return "Góc không hợp lệ (0 - 180)", 400

if __name__ == "__main__":
    try:
        print("Web Server đang chạy tại: http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        servo.detach()
