from flask import Flask, render_template
from gpiozero import LED

app = Flask(__name__)

# Khởi tạo LED ở chân GPIO 17 (Chân vật lý 11)
led = LED(17)


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/led/<action>")
def control_led(action):
  if action == "on":
    led.on()
    return "Đang Bật"
  elif action == "off":
    led.off()
    return "Đang Tắt"
  return "Lệnh không hợp lệ"


if __name__ == "__main__":
  # Cho phép truy cập từ các thiết bị khác trong cùng mạng nội bộ
  app.run(host="0.0.0.0", port=5000, debug=False)