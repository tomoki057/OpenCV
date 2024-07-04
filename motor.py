import RPi.GPIO as GPIO
import time

# GPIOピンの設定
A_PIN = 14  # 入力AのGPIOピン番号
B_PIN = 15  # 入力BのGPIOピン番号

# GPIOの設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(A_PIN, GPIO.OUT)
GPIO.setup(B_PIN, GPIO.OUT)

# PWMの設定
FREQUENCY = 1000  # PWMの周波数（Hz）
pwm_a = GPIO.PWM(A_PIN, FREQUENCY)
pwm_b = GPIO.PWM(B_PIN, FREQUENCY)

# PWMの開始
pwm_a.start(0)
pwm_b.start(0)

def motor_control(a, b):
    """モータードライバの入力を制御"""
    GPIO.output(A_PIN, a)
    GPIO.output(B_PIN, b)

def stop():
    motor_control(GPIO.HIGH, GPIO.HIGH)

def forward(speed):
    pwm_a.ChangeDutyCycle(0)
    pwm_b.ChangeDutyCycle(speed * 100)

def reverse(speed):
    pwm_a.ChangeDutyCycle(speed * 100)
    pwm_b.ChangeDutyCycle(0)

def short_brake():
    motor_control(GPIO.LOW, GPIO.LOW)

def sm_speed_control(speed):
    """SM方式の速度制御"""
    if speed < 0:
        speed = 0
    elif speed > 1:
        speed = 1

    forward_duration = speed
    stop_duration = 1.0 - speed

    forward(speed)
    time.sleep(forward_duration)
    short_brake()
    time.sleep(stop_duration)

try:
    speed = float(input("速度を0.0から1.0の範囲で入力してください: "))
    while True:
        sm_speed_control(speed)
except KeyboardInterrupt:
    pass
finally:
    pwm_a.stop()
    pwm_b.stop()
    GPIO.cleanup()

