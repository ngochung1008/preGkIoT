'''
=============================================================================
ĐỀ BÀI 22: Web Server Flask Giám sát Cảm biến Siêu âm HC-SR04 & Điều khiển Động cơ Bước
- Đọc khoảng cách thực tế từ cảm biến siêu âm HC-SR04 gửi về Web qua JSON API.
- Điều khiển Động cơ Bước 28BYJ-48 (Quay thuận, nghịch theo góc 90°, 180°, 360°).
- Thư viện: gpiozero (DistanceSensor), RpiMotorLib, flask.
- Giao diện HTML thuần (không dùng CSS).

WIRING GUIDE:
- HC-SR04: Trig -> GPIO 23 | Echo -> GPIO 24 (qua mạch chia áp) | VCC -> 5V | GND -> GND
- ULN2003: IN1 -> GPIO 17 | IN2 -> GPIO 18 | IN3 -> GPIO 27 | IN4 -> GPIO 22
- ULN2003: VCC -> 5V | GND -> GND
=============================================================================
'''

from flask import Flask, render_template_string, jsonify
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
    <title>Bài 22 - Cảm biến Siêu âm & Động cơ Bước</title>
</head>
<body>
    <h1>GIÁM SÁT KHOẢNG CÁCH SIÊU ÂM & ĐIỀU KHIỂN ĐỘNG CƠ BƯỚC</h1>
    <hr>
    
    <h2>1. KHOẢNG CÁCH TỪ CẢM BIẾN HC-SR04</h2>
    <p>Khoảng cách đo được: <b id="dist_val">--</b> cm</p>
    
    <hr>
    <h2>2. BẢNG ĐIỀU KHIỂN ĐỘNG CƠ BƯỚC (28BYJ-48)</h2>
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
    
    <hr>
    <h3>Trạng thái động cơ bước:</h3>
    <p id="stepper_status">Đang sẵn sàng</p>

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

        // Gửi lệnh điều khiển động cơ bước
        function controlStepper(direction, angle) {
            document.getElementById('stepper_status').innerText = 'Đang quay ' + direction + ' ' + angle + '°...';
            fetch('/stepper/' + direction + '/' + angle)
                .then(response => response.text())
                .then(data => {
                    document.getElementById('stepper_status').innerText = data;
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
