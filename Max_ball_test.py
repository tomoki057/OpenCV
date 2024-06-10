import cv2
import numpy as np

def main():
    # USBカメラの映像をキャプチャ
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("カメラを開けませんでした")
        return

    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f'actual frame rate: {actual_fps}')

    # 各色の範囲を定義（HSV色空間）
    color_ranges = {
        'blue': ([100, 150, 0], [140, 255, 255]),
        'yellow': ([20, 90, 105], [30, 255, 255])
    }

    while True:
        # フレームを取得
        ret, frame = cap.read()
        if not ret:
            break

        # フレームをHSV色空間に変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 最大のボールのマスクを作成
        max_ball_mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)

        for color, (lower, upper) in color_ranges.items():
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            mask = cv2.inRange(hsv, lower_bound, upper_bound)

            # 輪郭を検出
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # 輪郭の中で最大のものを選択
                max_contour = max(contours, key=cv2.contourArea)

                # 最大のボールの輪郭を追加
                cv2.drawContours(max_ball_mask, [max_contour], -1, 255, thickness=cv2.FILLED)

        # 最大のボールのマスクを元のフレームに適用
        max_ball_frame = cv2.bitwise_and(frame, frame, mask=max_ball_mask)

        # 結果を表示
        cv2.imshow('Max Ball Mask', max_ball_mask)
        cv2.imshow('Max Ball Frame', max_ball_frame)

        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # リソースを解放
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

