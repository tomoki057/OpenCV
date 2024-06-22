import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685の初期化
pca = PCA9685(i2c)
pca.frequency = 50  # サーボモーター用に50Hzに設定

def set_servo_angle(channel, angle):
    pulse_min = 550  # 0度のときのパルス幅（0.55ms）
    pulse_max = 2500  # 180度のときのパルス幅（2.5ms）
    pulse_range = pulse_max - pulse_min
    pulse = pulse_min + (pulse_range * angle / 180)
    duty_cycle = int(pulse / 1000000 * pca.frequency * 65535)
    pca.channels[channel].duty_cycle = duty_cycle

# サーボのチャンネル(青)
servo_channel_Blue = 2

# サーボのチャンネル(黄)
servo_channel_Yellow = 3

# サーボのチャンネル(赤)
servo_channel_Red = 4

try:
    while True:
        # 0 -> 60 slow rotate (blue tank)
        for angle in range(0, 60, 1):  # 1度ずつ増加
            set_servo_angle(servo_channel_Blue, angle)
            time.sleep(0.05)

        # 60 -> 0 slow rotate (blue tank)
        for angle in range(60, 0, -1):  # 1度ずつ減少
            set_servo_angle(servo_channel_Blue, angle)
            time.sleep(0.05)

        # 0 -> 60 slow rotate (yellow tank)
        for angle in range(125, 90, -1):  # 1度ずつ増加
            set_servo_angle(servo_channel_Yellow, angle)
            time.sleep(0.05)

        # 60 -> 0 slow rotate (yellow tank)
        for angle in range(90, 125, 1):  # 1度ずつ減少
            set_servo_angle(servo_channel_Yellow, angle)
            time.sleep(0.05)

        # 0 -> 60 slow rotate (red tank)
        for angle in range(180, 120, -1):  # 1度ずつ増加
            set_servo_angle(servo_channel_Red, angle)
            time.sleep(0.05)

        # 60 -> 0 slow rotate (red tank)
        for angle in range(120, 180, 1):  # 1度ずつ減少
            set_servo_angle(servo_channel_Red, angle)
            time.sleep(0.05)

except KeyboardInterrupt:
    # 終了時にPCA9685をシャットダウン
    pca.deinit()
    print("Program terminated and PCA9685 shutdown.")

