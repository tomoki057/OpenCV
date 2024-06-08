import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685の初期化
pca = PCA9685(i2c)
pca.frequency = 50  # サーボモーター用に50Hzに設定

# ローテーションサーボ用のPWM信号を計算する関数（角度をPWMのデューティサイクルに変換）
def set_rotation_servo_angle(channel, angle):
    pulse_min = 500  # 0度のときのパルス幅（0.5ms）
    pulse_max = 2500  # 180度のときのパルス幅（2.5ms）
    pulse_range = pulse_max - pulse_min
    pulse = pulse_min + (pulse_range * angle / 180)
    duty_cycle = int(pulse / 1000000 * pca.frequency * 65535)
    print(f"Setting rotation servo angle for channel {channel} to: {angle} degrees, duty cycle: {duty_cycle}")
    pca.channels[channel].duty_cycle = duty_cycle

# DCサーボ用のPWM信号を計算する関数（速度と方向をPWMのデューティサイクルに変換）
def set_dc_servo_speed(channel, speed):
    # speedは-100から100の範囲で、0が停止、負の値が逆方向
    pulse_min = 1500  # 中立のときのパルス幅（1.5ms）
    pulse_max = 500  # 逆方向の最大パルス幅（0.5ms）
    pulse_min_rev = 2500  # 正方向の最大パルス幅（2.5ms）
    if speed == 0:
        pulse = pulse_min
    elif speed > 0:
        pulse = pulse_min + ((pulse_min_rev - pulse_min) * speed / 100)
    else:
        pulse = pulse_min + ((pulse_max - pulse_min) * speed / 100)
    duty_cycle = int(pulse / 1000000 * pca.frequency * 65535)
    print(f"Setting DC servo speed for channel {channel} to: {speed}%, duty cycle: {duty_cycle}")
    pca.channels[channel].duty_cycle = duty_cycle

# DCサーボのチャンネル
dc_servo_channel = 0

# ローテーションサーボのチャンネル
rotation_servo_channel = 1

try:
    while True:
        # ローテーションサーボを0度に動かす
        set_rotation_servo_angle(rotation_servo_channel, 0)
        time.sleep(1)

        # ローテーションサーボを90度に動かす
        set_rotation_servo_angle(rotation_servo_channel, 90)
        time.sleep(1)

        # ローテーションサーボを180度に動かす
        set_rotation_servo_angle(rotation_servo_channel, 180)
        time.sleep(1)

        # DCサーボを前進させる
        set_dc_servo_speed(dc_servo_channel, 50)
        time.sleep(2)

        # DCサーボを停止させる
        set_dc_servo_speed(dc_servo_channel, 0)
        time.sleep(1)

        # DCサーボを後退させる
        set_dc_servo_speed(dc_servo_channel, -50)
        time.sleep(2)

        # DCサーボを停止させる
        set_dc_servo_speed(dc_servo_channel, 0)
        time.sleep(1)

except KeyboardInterrupt:
    # 終了時にPCA9685をシャットダウン
    pca.deinit()
    print("Program terminated and PCA9685 shutdown.")

