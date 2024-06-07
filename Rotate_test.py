import RPi.GPIO as GPIO
import time

# GPIOの設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

# PWMの設定
pwm = GPIO.PWM(18, 50)  # 50HzのPWM信号を生成
pwm.start(0)

def set_angle(angle):
    duty = angle / 18 + 2  # 角度に対応するデューティサイクルを計算
    GPIO.output(18, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(18, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        # サーボを0度に動かす
        set_angle(0)
        time.sleep(2)

        # サーボを90度に動かす
        set_angle(90)
        time.sleep(2)

        # サーボを180度に動かす
        set_angle(180)
        time.sleep(2)

except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()

