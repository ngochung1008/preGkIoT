'''
=============================================================================
ĐỀ BÀI 21: Web Server Flask Giám sát Cảm biến Siêu âm HC-SR04 & Điều khiển Động cơ DC
- Đọc khoảng cách thực tế từ cảm biến siêu âm HC-SR04 gửi về Web qua JSON API.
- Điều khiển Động cơ DC (Quay thuận, quay nghịch các cấp tốc độ, dừng lại).
- Thư viện: gpiozero (DistanceSensor, Motor), flask.
- Giao diện HTML thuần (không dùng CSS).

WIRING GUIDE:
- HC-SR04: Trig -> GPIO 23 | Echo -> GPIO 24 (qua mạch chia áp) | VCC -> 5V | GND -> GND
- L298N: ENA -> GPIO 12 (tháo jumper) | IN1 -> GPIO 17 | IN2 -> GPIO 27
- L298N GND -> Nối chung GND với Raspberry Pi và nguồn ngoài.
=============================================================================
'''

from flask import Flask, render_template_string, jsonify, request
from gpiozero import DistanceSensor, Motor

app = Flask(__name__)

# Khởi tạo cảm biến siêu âm HC-SR04
sensor = DistanceSensor(echo=24, trigger=23, max_distance=2.0)

# Khởi tạo động cơ DC bằng gpiozero Motor (IN1=17, IN2=27, ENA=12)
motor = Motor(forward=17, backward=27, enable=12)

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bài 21 - Cảm biến Siêu âm & Động cơ DC</title>
</head>
<body>
    <h1>GIÁM SÁT KHOẢNG CÁCH SIÊU ÂM & ĐIỀU KHIỂN ĐỘNG CƠ DC</h1>
    <hr>
    
    <h2>1. KHOẢNG CÁCH TỪ CẢM BIẾN HC-SR04</h2>
    <p>Khoảng cách đo được: <b id="dist_val">--</b> cm</p>
    
    <hr>
    <h2>2. BẢNG ĐIỀU KHIỂN ĐỘNG CƠ DC</h2>
    <p>
        <b>Điều khiển chiều quay và tốc độ:</b><br><br>
        <button onclick="controlMotor('forward', 0.35)">Quay Thuận Chậm (35%)</button>
        <button onclick="controlMotor('forward', 0.90)">Quay Thuận Nhanh (90%)</button>
        <button onclick="controlMotor('backward', 0.35)">Quay Nghịch Chậm (35%)</button>
        <button onclick="controlMotor('backward', 0.90)">Quay Nghịch Nhanh (90%)</button>
        <button onclick="controlMotor('stop', 0)">DỪNG ĐỘNG CƠ</button>
    </p>
    
    <hr>
    <h3>Trạng thái động cơ:</h3>
    <p id="motor_status">Đang dừng</p>

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

        // Gửi lệnh điều khiển động cơ DC
        function controlMotor(action, speed) {
            fetch('/motor/' + action + '?speed=' + speed)
                .then(response => response.text())
                .then(data => {
                    document.getElementById('motor_status').innerText = data;
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
