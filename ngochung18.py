'''
=============================================================================
ĐỀ BÀI 18: Web Server Flask Giám sát Cảm biến DHT11 & Điều khiển Động cơ DC (L298N)
- Đọc nhiệt độ và độ ẩm thực tế từ cảm biến DHT11 (GPIO 4) gửi về Web qua JSON API.
- Điều khiển Động cơ DC (Quay thuận, quay nghịch với các cấp tốc độ, dừng lại).
- Giao diện HTML thuần (không dùng CSS).

WIRING GUIDE:
- DHT11: DATA -> GPIO 4 | VCC -> 5V | GND -> GND
- L298N: ENA -> GPIO 12 (hoặc 22, tháo jumper) | IN1 -> GPIO 17 | IN2 -> GPIO 27
- L298N GND -> Nối chung GND với Raspberry Pi và nguồn ngoài.
=============================================================================
'''

from flask import Flask, render_template_string, jsonify, request
import board
import adafruit_dht
from gpiozero import Motor

app = Flask(__name__)

# Khởi tạo cảm biến DHT11 tại GPIO 4
dht_device = adafruit_dht.DHT11(board.D4)

# Khởi tạo động cơ DC bằng gpiozero Motor (IN1=17, IN2=27, ENA=12)
motor = Motor(forward=17, backward=27, enable=12)

# Biến lưu trữ giá trị đọc gần nhất
last_temp = 0.0
last_humi = 0.0

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bài 18 - Cảm biến DHT11 & Động cơ DC</title>
</head>
<body>
    <h1>GIÁM SÁT DHT11 & ĐIỀU KHIỂN ĐỘNG CƠ DC</h1>
    <hr>
    
    <h2>1. THÔNG SỐ CẢM BIẾN DHT11</h2>
    <p>Nhiệt độ hiện tại: <b id="temp_val">--</b> °C</p>
    <p>Độ ẩm hiện tại: <b id="humi_val">--</b> %</p>
    
    <hr>
    <h2>2. BẢNG ĐIỀU KHIỂN ĐỘNG CƠ DC</h2>
    <p>
        <b>Điều khiển chiều & tốc độ:</b><br><br>
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
        pass  # DHT11 có thể gặp lỗi đọc timing định kỳ
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
