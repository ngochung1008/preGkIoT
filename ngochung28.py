'''
=============================================================================
ĐỀ BÀI 28: Web Server Flask tích hợp Gọi Web API Thời tiết & Giám sát Siêu âm & Động cơ Bước
1. Giao diện Web HTML thuần:
   - Có ô nhập tên thành phố và nút "Xem Thời Tiết".
   - Hiển thị thông số thời tiết từ wttr.in: Nhiệt độ, Độ ẩm, Lượng mưa, Tầm nhìn, Gió, Tình trạng.
   - Hiển thị khoảng cách thực tế từ Cảm biến Siêu âm HC-SR04 (Trig=23, Echo=24).
   - Bảng nút bấm điều khiển Động cơ Bước 28BYJ-48 (Thuận/Nghịch theo góc 90°, 180°, 360°).

WIRING GUIDE:
- HC-SR04: Trig -> GPIO 23 | Echo -> GPIO 24 (qua mạch chia áp) | VCC -> 5V | GND -> GND
- ULN2003: IN1 -> GPIO 17 | IN2 -> GPIO 18 | IN3 -> GPIO 27 | IN4 -> GPIO 22
- ULN2003: VCC -> 5V | GND -> GND
=============================================================================
'''

from flask import Flask, render_template_string, jsonify, request
import requests
from gpiozero import DistanceSensor
from RpiMotorLib import RpiMotorLib

app = Flask(__name__)

# Khởi tạo cảm biến siêu âm HC-SR04
sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

# Cấu hình chân ULN2003 và Động cơ Bước
pins = [17, 18, 27, 22]
stepper_motor = RpiMotorLib.BYJMotor("MyStepper", "28BYJ")

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bài 28 - Web Server API Thời tiết & Siêu âm & Động cơ Bước</title>
</head>
<body>
    <h1>HỆ THỐNG IOT: WEB API THỜI TIẾT + SIÊU ÂM + ĐỘNG CƠ BƯỚC</h1>
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
    <h2>3. BẢNG ĐIỀU KHIỂN ĐỘNG CƠ BƯỚC (28BYJ-48)</h2>
    <p>
        <b>Quay theo chiều kim đồng hồ (Thuận):</b><br><br>
        <button onclick="controlStepper('forward', 90)">Quay Thuận 90°</button>
        <button onclick="controlStepper('forward', 180)">Quay Thuận 180°</button>
        <button onclick="controlStepper('forward', 360)">Quay Thuận 360° (1 Vòng)</button>
    </p>
    <p>
        <b>Quay ngược chiều kim đồng hồ (Nghịch):</b><br><br>
        <button onclick="controlStepper('backward', 90)">Quay Nghịch 90°</button>
        <button onclick="controlStepper('backward', 180)">Quay Nghịch 180°</button>
        <button onclick="controlStepper('backward', 360)">Quay Nghịch 360° (1 Vòng)</button>
    </p>
    
    <p>Trạng thái động cơ bước: <b id="stepper_status">Đang sẵn sàng</b></p>

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

        // Điều khiển động cơ bước
        function controlStepper(direction, angle) {
            document.getElementById('stepper_status').innerText = 'Đang quay ' + direction + ' ' + angle + '°...';
            fetch('/stepper/' + direction + '/' + angle)
                .then(response => response.text())
                .then(data => {
                    document.getElementById('stepper_status').innerText = data;
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

@app.route("/stepper/<direction>/<int:angle>")
def control_stepper(direction, angle):
    """API điều khiển động cơ bước quay theo hướng và góc."""
    steps = int(angle * (512 / 360))
    is_clockwise = True if direction == "forward" else False
    
    stepper_motor.motor_run(pins, 0.002, steps, is_clockwise, False, "full")
    dir_text = "THUẬN" if is_clockwise else "NGHỊCH"
    return f"Đã hoàn thành quay {dir_text} {angle}° ({steps} bước)."

if __name__ == "__main__":
    print("Web Server đang chạy tại: http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
