import cv2
import numpy as np
import time
import RPi.GPIO as GPIO
import board
import busio
from adafruit_pca9685 import PCA9685

# GPIOピンの設定
A1_PIN = 14  # モーター1の入力Aピン
B1_PIN = 15  # モーター1の入力Bピン
A2_PIN = 23  # モーター2の入力Aピン
B2_PIN = 24  # モーター2の入力Bピン

# GPIOの設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(A1_PIN, GPIO.OUT)
GPIO.setup(B1_PIN, GPIO.OUT)
GPIO.setup(A2_PIN, GPIO.OUT)
GPIO.setup(B2_PIN, GPIO.OUT)

# PWMの設定
FREQUENCY = 1000  # PWMの周波数（Hz）
pwm_a1 = GPIO.PWM(A1_PIN, FREQUENCY)
pwm_b1 = GPIO.PWM(B1_PIN, FREQUENCY)
pwm_a2 = GPIO.PWM(A2_PIN, FREQUENCY)
pwm_b2 = GPIO.PWM(B2_PIN, FREQUENCY)

# PWMの開始（デューティサイクル0%）
pwm_a1.start(0)
pwm_b1.start(0)
pwm_a2.start(0)
pwm_b2.start(0)

# I2Cバスの初期化
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685の初期化
pca = PCA9685(i2c)
pca.frequency = 50  # サーボモーター用に50Hzに設定

# サーボモータを動かす関数
def move_servo(channel, pulse):
    pca.channels[channel].duty_cycle = pulse

# サーボモータのチャンネルとパルス幅のマッピング
PCAchannel = 2

servo_mapping = {
    'blue': (PCAchannel, 2000),   # 例: 青いボール用のサーボモータ
    'red': (PCAchannel, 4000),    # 例: 赤いボール用のサーボモータ
    'yellow': (PCAchannel, 6000)  # 例: 黄色いボール用のサーボモータ
}

# 0番と1番のサーボモータのパルス幅（逆方向）
servo_pulses = {
    0: 10000,  # 0番サーボモータの逆方向パルス幅
    1: 10000   # 1番サーボモータの逆方向パルス幅
}

# サーボモータを停止するパルス幅（中央位置、角度ゼロ）
servo_stop_pulse = 0

def main():
    # USBカメラの映像をキャプチャ
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("カメラを開けませんでした")
        return

    # 各色の範囲を定義（HSV色空間）
    color_ranges = {
        'blue': ([100, 150, 0], [140, 255, 255]),
        'yellow': ([20, 100, 100], [30, 255, 255])
    }

    previous_max_color = None

    while True:
        # フレームを取得
        ret, frame = cap.read()
        if not ret:
            break

        # frame resize(320*240)
        frame = cv2.resize(frame, (320, 240))

        # フレームをHSV色空間に変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 赤色のマスクを作成（赤色は二つの範囲に分ける）
        red_lower1 = np.array([0, 120, 70])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([170, 120, 70])
        red_upper2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = mask1 | mask2

        # 他の色のマスクを作成
        masks = {'red': red_mask}
        for color, (lower, upper) in color_ranges.items():
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            masks[color] = cv2.inRange(hsv, lower_bound, upper_bound)

        detected_balls = []  # ボール情報を保存するリスト

        for color, mask in masks.items():
            # 輪郭を検出
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                # 輪郭の面積を計算
                area = cv2.contourArea(contour)
                if area > 500:
                    # 外接円を計算
                    ((x, y), radius) = cv2.minEnclosingCircle(contour)
                    center = (int(x), int(y))
                    radius = int(radius)

                    # 円形状かどうかをチェック
                    if radius > 10:
                        circularity = 4 * np.pi * (area / (cv2.arcLength(contour, True) ** 2))
                        if 0.7 < circularity < 1.3:  # 円形に近いかどうか
                            detected_balls.append((color, radius, center))  # 色、半径、中心座標を保存

        # ボールを半径でソート（大きい順）
        detected_balls.sort(key=lambda x: x[1], reverse=True)

        # ボールが検出されているか確認
        if detected_balls:
            move_servo(0, servo_pulses[0])
            move_servo(1, servo_pulses[1])

            max_color, _, (x, y) = detected_balls[0]
            if max_color != previous_max_color:
                move_servo_based_on_color(max_color)
                previous_max_color = max_color
                time.sleep(1)  # サーボが安定するまで待機

            # カメラの中央にボールを保持するためのモーター制御
            frame_center_x = frame.shape[1] // 2
            error_x = x - frame_center_x

            # 閾値を設定してモーターを制御
            if abs(error_x) > 20:
                if error_x > 0:
                    # ボールが右側にある場合、左に動かす
                    move_motor_left(0.5)  # 速度0.5で左に動かす
                else:
                    # ボールが左側にある場合、右に動かす
                    move_motor_right(0.5)  # 速度0.5で右に動かす
            else:
                # ボールが中央付近にある場合、モーターを停止
                stop_motors()
        else:
            # ボールが検出されていない場合、モーターを停止させる
            move_servo(0, servo_stop_pulse)
            move_servo(1, servo_stop_pulse)
            stop_motors()

        # ソートされたボールに順位を表示
        for i, (color, radius, center) in enumerate(detected_balls):
            if color == 'blue':
                cv2.circle(frame, center, radius, (255, 0, 0), 2)
            elif color == 'red':
                cv2.circle(frame, center, radius, (0, 0, 255), 2)
            elif color == 'yellow':
                cv2.circle(frame, center, radius, (0, 255, 255), 2)
            cv2.putText(frame, f'{i+1}', (center[0] - 10, center[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # 結果を表示
        cv2.imshow('Frame', frame)

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # リソースを解放
    cap.release()
    cv2.destroyAllWindows()

def move_motor_left(speed):
    """モーターを左に動かす"""
    forward_motor1(speed)
    reverse_motor2(speed)

def move_motor_right(speed):
    """モーターを右に動かす"""
    reverse_motor1(speed)
    forward_motor2(speed)

def stop_motors():
    """モーターを停止"""
    stop_motor1()
    stop_motor2()

def forward_motor1(speed):
    """モーター1を前進"""
    pwm_a1.ChangeDutyCycle(0)
    pwm_b1.ChangeDutyCycle(speed * 100)

def reverse_motor1(speed):
    """モーター1を後退"""
    pwm_a1.ChangeDutyCycle(speed * 100)
    pwm_b1.ChangeDutyCycle(0)

def stop_motor1():
    """モーター1を停止"""
    pwm_a1.ChangeDutyCycle(0)
    pwm_b1.ChangeDutyCycle(0)

def forward_motor2(speed):
    """モーター2を前進"""
    pwm_a2.ChangeDutyCycle(0)
    pwm_b2.ChangeDutyCycle(speed * 100)

def reverse_motor2(speed):
    """モーター2を後退"""
    pwm_a2.ChangeDutyCycle(speed * 100)
    pwm_b2.ChangeDutyCycle(0)

def stop_motor2():
    """モーター2を停止"""
    pwm_a2.ChangeDutyCycle(0)
    pwm_b2.ChangeDutyCycle(0)

# ボールの色に応じてサーボモータを動かす関数
def move_servo_based_on_color(color):
    if color in servo_mapping:
        channel, pulse = servo_mapping[color]
        move_servo(channel, pulse)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        pwm_a1.stop()
        pwm_b1.stop()
        pwm_a2.stop()
        pwm_b2.stop()
        GPIO.cleanup()

