#3colors_test.py
import cv2
import numpy as np

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

    while True:
        # フレームを取得
        ret, frame = cap.read()
        if not ret:
            break

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

                    # 円を描画
                    if radius > 10:
                        circularity = 4 * np.pi * (area / (cv2.arcLength(contour, True) ** 2))
                        if 0.7 < circularity < 1.3:  # 円形に近いかどうか
                            if color == 'blue':
                                cv2.circle(frame, center, radius, (255, 0, 0), 2)
                            elif color == 'red':
                                cv2.circle(frame, center, radius, (0, 0, 255), 2)
                            elif color == 'yellow':
                                cv2.circle(frame, center, radius, (0, 255, 255), 2)

        # 結果を表示
        cv2.imshow('Frame', frame)

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # リソースを解放
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
