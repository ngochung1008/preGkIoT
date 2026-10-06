'''
=============================================================================
ĐỀ BÀI 23: Web Server Flask Giám sát Cảm biến Siêu âm HC-SR04 & Điều khiển Động cơ Servo (SG90)
- Đọc khoảng cách thực tế từ cảm biến siêu âm HC-SR04 gửi về Web qua JSON API.
- Điều khiển Động cơ Servo SG90 xoay các góc 0°, 45°, 90°, 135°, 180° hoặc thanh trượt.
- Thư viện: gpiozero (DistanceSensor, AngularServo), flask.
- Giao diện HTML thuần (không dùng CSS).

WIRING GUIDE:
- HC-SR04: Trig -> GPIO 23 | Echo -> GPIO 24 (qua mạch chia áp) | VCC -> 5V | GND -> GND
- Servo SG90: Signal (Cam/Vàng) -> GPIO 18 | VCC (Đỏ) -> 5V | GND (Nâu/Đen) -> GND
=============================================================================
'''

from flask import Flask, render_template_string, jsonify
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
    <title>Bài 23 - Cảm biến Siêu âm & Động cơ Servo</title>
</head>
<body>
    <h1>GIÁM SÁT KHOẢNG CÁCH SIÊU ÂM & ĐIỀU KHIỂN ĐỘNG CƠ SERVO</h1>
    <hr>
    
    <h2>1. KHOẢNG CÁCH TỪ CẢM BIẾN HC-SR04</h2>
    <p>Khoảng cách đo được: <b id="dist_val">--</b> cm</p>
    
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
        // Cập nhật khoảng cách mỗi 1 giây
        function fetchDistance() {
            fetch('/get_distance')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('dist_val').innerText = data.distance;
                })
                .catch(err => console.error(err));
        }
        setInterval(fetchDistance, 1000);
        fetchDistance();

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
    return "Góc không hợp lệ (phải từ 0 đến 180 độ)", 400

if __name__ == "__main__":
    try:
        print("Web Server đang chạy tại: http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        servo.detach()
