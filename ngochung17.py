'''
=============================================================================
ĐỀ BÀI 17: Web Server Flask điều khiển Bật / Tắt đèn LED trên Raspberry Pi 4
- Sử dụng Flask framework tạo Web Server chạy trên cổng 5000.
- Giao diện HTML thuần (không dùng CSS) với các nút bấm điều khiển LED.
- Sử dụng fetch() JavaScript để gửi lệnh không tải lại trang.

WIRING GUIDE:
- LED (+): nối qua điện trở 220Ω -> GPIO 18
- LED (-): GND
=============================================================================
'''

from flask import Flask, render_template_string, jsonify
from gpiozero import LED

app = Flask(__name__)

# Khởi tạo LED ở chân GPIO 18
led = LED(18)

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Bài 17 - Điều khiển LED qua Web Server</title>
</head>
<body>
    <h1>HỆ THỐNG ĐIỀU KHIỂN ĐÈN LED (WEB SERVER FLASK)</h1>
    <hr>
    
    <h2>Bảng điều khiển:</h2>
    <button onclick="controlLed('on')">BẬT ĐÈN</button>
    <button onclick="controlLed('off')">TẮT ĐÈN</button>
    <button onclick="controlLed('toggle')">ĐẢO TRẠNG THÁI</button>
    
    <hr>
    <h3>Trạng thái hiện tại:</h3>
    <p id="status_text">Đang lấy dữ liệu...</p>

    <script>
        function controlLed(action) {
            fetch('/led/' + action)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status_text').innerText = 'Đèn LED: ' + data.status;
                })
                .catch(err => console.error(err));
        }

        function updateStatus() {
            fetch('/get_led_status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status_text').innerText = 'Đèn LED: ' + data.status;
                })
                .catch(err => console.error(err));
        }

        // Tự động cập nhật trạng thái mỗi 1 giây
        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    """Trang chủ hiển thị giao diện HTML thuần."""
    return render_template_string(HTML_PAGE)

@app.route("/led/<action>")
def control_led(action):
    """API điều khiển trạng thái LED."""
    if action == "on":
        led.on()
    elif action == "off":
        led.off()
    elif action == "toggle":
        led.toggle()
    else:
        return jsonify({"status": "Lệnh không hợp lệ", "is_lit": led.is_lit}), 400
        
    status_str = "BẬT (ON)" if led.is_lit else "TẮT (OFF)"
    return jsonify({"status": status_str, "is_lit": led.is_lit})

@app.route("/get_led_status")
def get_led_status():
    """API lấy trạng thái hiện tại của LED."""
    status_str = "BẬT (ON)" if led.is_lit else "TẮT (OFF)"
    return jsonify({"status": status_str, "is_lit": led.is_lit})

if __name__ == "__main__":
    print("Web Server đang chạy tại: http://0.0.0.0:5000")
    print("Nhấn Ctrl+C để dừng server.")
    app.run(host="0.0.0.0", port=5000, debug=False)
