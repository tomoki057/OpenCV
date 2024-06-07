#servo_test.py
import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685の初期化
pca = PCA9685(i2c)
pca.frequency = 50  # サーボモーター用に50Hzに設定

# PWM信号を計算する関数（角度をPWMのデューティサイクルに変換）
def set_servo_angle(channel, angle):
    pulse_min = 550  # 0度のときのパルス幅（0.5ms）
    pulse_max = 2300  # 180度のときのパルス幅（2.5ms）
    pulse_range = pulse_max - pulse_min
    pulse = pulse_min + (pulse_range * angle / 180)
    duty_cycle = int(pulse / 1000000 * pca.frequency * 65535)
    print(f"Setting duty cycle for channel {channel} to: {duty_cycle}")
    pca.channels[channel].duty_cycle = duty_cycle

# サーボモーターのチャンネル設定（例えば、チャンネル0を使用）
servo_channel = 0

try:
    while True:
        # サーボを制御（例えば、0度に設定）
        set_servo_angle(servo_channel, 0)
        # 一時停止して、サーボが動作するのを確認
        time.sleep(2)

        # サーボを別の角度に設定（例えば、180度に設定）
        set_servo_angle(servo_channel, 180)
        # 一時停止して、サーボが動作するのを確認
        time.sleep(2)

except KeyboardInterrupt:
    # 終了時にPCA9685をシャットダウン
    pca.deinit()
    print("Program terminated and PCA9685 shutdown.")

