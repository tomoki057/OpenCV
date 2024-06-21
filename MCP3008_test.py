import spidev
import RPi.GPIO as GPIO
import time

# SPI設定
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# MCP3008からデータを読み取る関数
def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# GPIO設定
motor_left_forward = 17
motor_left_backward = 18
motor_right_forward = 22
motor_right_backward = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_left_forward, GPIO.OUT)
GPIO.setup(motor_left_backward, GPIO.OUT)
GPIO.setup(motor_right_forward, GPIO.OUT)
GPIO.setup(motor_right_backward, GPIO.OUT)

# モーター制御関数
def set_motor(left_speed, right_speed):
    if left_speed > 0:
        GPIO.output(motor_left_forward, GPIO.HIGH)
        GPIO.output(motor_left_backward, GPIO.LOW)
    else:
        GPIO.output(motor_left_forward, GPIO.LOW)
        GPIO.output(motor_left_backward, GPIO.HIGH)

    if right_speed > 0:
        GPIO.output(motor_right_forward, GPIO.HIGH)
        GPIO.output(motor_right_backward, GPIO.LOW)
    else:
        GPIO.output(motor_right_forward, GPIO.LOW)
        GPIO.output(motor_right_backward, GPIO.HIGH)

# PID制御パラメータ
Kp = 1.0
Ki = 0.0
Kd = 0.0

previous_error = 0
integral = 0

# ライントレースのメインループ
try:
    while True:
        sensor_values = [read_adc(i) for i in range(8)]
        print("Sensor Values: ", sensor_values)
        
        # センサー値の重心を計算
        position = sum([i * sensor_values[i] for i in range(8)]) / sum(sensor_values)
        error = position - 3.5  # 中心からの偏差
        
        # PID制御計算
        integral += error
        derivative = error - previous_error
        control_signal = Kp * error + Ki * integral + Kd * derivative
        previous_error = error
        
        # モーター制御
        base_speed = 1  # 基本速度
        left_speed = base_speed - control_signal
        right_speed = base_speed + control_signal
        set_motor(left_speed, right_speed)

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()

