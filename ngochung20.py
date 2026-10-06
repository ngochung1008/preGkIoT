'''
=============================================================================
ĐỀ BÀI 20: Web Server Flask Giám sát Cảm biến DHT11 & Điều khiển Động cơ Servo (SG90)
- Đọc nhiệt độ và độ ẩm thực tế từ cảm biến DHT11 (GPIO 4) gửi về Web qua JSON API.
- Điều khiển Động cơ Servo SG90 (GPIO 18) xoay các góc 0°, 45°, 90°, 135°, 180° hoặc thanh trượt.
- Thư viện: gpiozero (AngularServo), adafruit_dht, flask.
- Giao diện HTML thuần (không dùng CSS).

WIRING GUIDE:
- DHT11: DATA -> GPIO 4 | VCC -> 5V | GND -> GND
- Servo SG90: Dây Tín hiệu (Cam/Vàng) -> GPIO 18 | Dây VCC (Đỏ) -> 5V | Dây GND (Nâu/Đen) -> GND
=============================================================================
'''

from flask import Flask, render_template_string, jsonify
import board
import adafruit_dht
from gpiozero import AngularServo

app = Flask(__name__)

# Khởi tạo cảm biến DHT11 tại GPIO 4
dht_device = adafruit_dht.DHT11(board.D4)

# Khởi tạo Servo tại GPIO 18 với xung chuẩn SG90
servo = AngularServo(
    18, 
    min_angle=0, 
    max_angle=180, 
    min_pulse_width=0.0005, 
    max_pulse_width=0.0025
)

# Biến lưu trữ giá trị đọc gần nhất
last_temp = 0.0
last_humi = 0.0

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bài 20 - Cảm biến DHT11 & Động cơ Servo</title>
</head>
<body>
    <h1>GIÁM SÁT DHT11 & ĐIỀU KHIỂN ĐỘNG CƠ SERVO</h1>
    <hr>
    
    <h2>1. THÔNG SỐ CẢM BIẾN DHT11</h2>
    <p>Nhiệt độ hiện tại: <b id="temp_val">--</b> °C</p>
    <p>Độ ẩm hiện tại: <b id="humi_val">--</b> %</p>
    
    <hr>
    <h2>2. BẢNG ĐIỀU KHIỂN ĐỘNG CƠ SERVO (SG90)</h2>
    <p>
        <b>Nút bấm chọn góc nhanh:</b><br><br>
        <button onclick="setServoAngle(0)">0°</button>
        <button onclick="setServoAngle(45)">45°</button>
        <button onclick="setServoAngle(90)">90°</button>
        <button onclick="setServoAngle(135)">135°</button>
        <button onclick="setServoAngle(180)">180°</button>
    </p>
    <p>
        <b>Thanh trượt chỉnh góc tự do (0° - 180°):</b><br><br>
        <input type="range" id="servo_slider" min="0" max="180" value="90" onchange="setServoAngle(this.value)">
        <span id="slider_val">90°</span>
    </p>
    
    <hr>
    <h3>Trạng thái Servo:</h3>
    <p id="servo_status">Đang sẵn sàng tại 0°</p>

    <script>
        // Cập nhật giá trị DHT11 mỗi 2 giây
        function fetchSensorData() {
            fetch('/get_sensor')
                .then(response => response.json())
                .then(data => {
                    if (data.temperature !== null) {
                        document.getElementById('temp_val').innerText = data.temperature;
                    }
                    if (data.humidity !== null) {
                        document.getElementById('humi_val').innerText = data.humidity;
                    }
                })
                .catch(err => console.error(err));
        }
        setInterval(fetchSensorData, 2000);
        fetchSensorData();

        // Gửi lệnh điều khiển góc Servo
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
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    """Trang chủ hiển thị giao diện HTML thuần."""
    return render_template_string(HTML_PAGE)

@app.route("/get_sensor")
def get_sensor():
    """API trả về dữ liệu nhiệt độ và độ ẩm dạng JSON."""
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

@app.route("/servo/<int:angle>")
def control_servo(angle):
    """API xoay động cơ Servo đến góc chỉ định."""
    if 0 <= angle <= 180:
        servo.angle = angle
        return f"Đã xoay Servo đến góc {angle}°"
    return "Góc không hợp lệ (phải từ 0 đến 180 độ)", 400

if __name__ == "__main__":
    try:
        print("Web Server đang chạy tại: http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        dht_device.exit()
        servo.detach()
