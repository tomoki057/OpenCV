import time
import board
import busio
import RPi.GPIO as GPIO
from adafruit_pca9685 import PCA9685

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685の初期化
pca = PCA9685(i2c)
pca.frequency = 50  # サーボモーター用に50Hzに設定

# PWM信号を計算する関数（角度をPWMのデューティサイクルに変換）
def set_servo_angle(channel, angle):
    duty = angle / 18 + 2  # 角度に対応するデューティサイクルを計算
    GPIO.output(18, True)
    pca.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(18, False)
    pca.ChangeDutyCycle(0)

# サーボモーターのチャンネル設定（例えば、チャンネル0を使用）
servo_channel = 1

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
    # 終了時にPCA9685をシャットダウン
    pca.deinit()
    print("Program terminated and PCA9685 shutdown.")

    GPIO.cleanup()
