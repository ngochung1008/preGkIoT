'''
=============================================================================
ĐỀ BÀI 19: Web Server Flask Giám sát Cảm biến DHT11 & Điều khiển Động cơ Bước (28BYJ-48)
- Đọc nhiệt độ và độ ẩm thực tế từ cảm biến DHT11 (GPIO 4) gửi về Web qua JSON API.
- Điều khiển Động cơ Bước 28BYJ-48 (Quay thuận, quay nghịch theo góc: 90°, 180°, 360°).
- Thư viện: RpiMotorLib, adafruit_dht, flask.
- Giao diện HTML thuần (không dùng CSS).

WIRING GUIDE:
- DHT11: DATA -> GPIO 4 | VCC -> 5V | GND -> GND
- ULN2003: IN1 -> GPIO 17 | IN2 -> GPIO 18 | IN3 -> GPIO 27 | IN4 -> GPIO 22
- ULN2003: VCC -> 5V | GND -> GND
=============================================================================
'''

from flask import Flask, render_template_string, jsonify
import board
import adafruit_dht
from RpiMotorLib import RpiMotorLib

app = Flask(__name__)

# Khởi tạo cảm biến DHT11 tại GPIO 4
dht_device = adafruit_dht.DHT11(board.D4)

# Cấu hình chân ULN2003 và Động cơ Bước
pins = [17, 18, 27, 22]
stepper_motor = RpiMotorLib.BYJMotor("MyStepper", "28BYJ")

# Biến lưu trữ giá trị đọc gần nhất
last_temp = 0.0
last_humi = 0.0

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bài 19 - Cảm biến DHT11 & Động cơ Bước</title>
</head>
<body>
    <h1>GIÁM SÁT DHT11 & ĐIỀU KHIỂN ĐỘNG CƠ BƯỚC</h1>
    <hr>
    
    <h2>1. THÔNG SỐ CẢM BIẾN DHT11</h2>
    <p>Nhiệt độ hiện tại: <b id="temp_val">--</b> °C</p>
    <p>Độ ẩm hiện tại: <b id="humi_val">--</b> %</p>
    
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

@app.route("/stepper/<direction>/<int:angle>")
def control_stepper(direction, angle):
    """API điều khiển động cơ bước quay theo hướng và góc."""
    # 28BYJ-48 có 512 bước / vòng 360 độ ở chế độ full-step
    steps = int(angle * (512 / 360))
    is_clockwise = True if direction == "forward" else False
    
    stepper_motor.motor_run(pins, 0.002, steps, is_clockwise, False, "full")
    dir_text = "THUẬN" if is_clockwise else "NGHỊCH"
    return f"Đã hoàn thành quay {dir_text} {angle}° ({steps} bước)."

if __name__ == "__main__":
    try:
        print("Web Server đang chạy tại: http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        dht_device.exit()
