from flask import Flask, jsonify, render_template
from gpiozero import AngularServo, DistanceSensor
# Sử dụng pin_factory='lgpio' ngầm định hoặc mặc định của hệ thống
from time import sleep

app = Flask(__name__)

# Khởi tạo cảm biến siêu âm (Trig=23, Echo=24)
sensor = DistanceSensor(echo=24, trigger=23)

# Khởi tạo Servo ở chân GPIO 18 với góc từ 0 đến 180 độ
servo = AngularServo(18, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0024)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/get_distance")
def get_distance():
  # Đo khoảng cách và đổi sang centimet
  distance_cm = round(sensor.distance * 100, 1)
  return jsonify({"distance": distance_cm})

@app.route("/servo/<int:angle>")
def control_servo(angle):
  if 0 <= angle <= 180:
    servo.angle = angle
    return f"Đã xoay Servo đến góc {angle}°"
  return "Góc không hợp lệ (0-180)"

if __name__ == "__main__":
  # Tắt debug=True để tránh lỗi tranh chấp chân GPIO (GPIO busy)
  app.run(host="0.0.0.0", port=5000, debug=False)