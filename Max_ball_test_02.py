import cv2
import numpy as np
import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Initialize the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the PCA9685 module
pca = PCA9685(i2c)
pca.frequency = 50  # Set frequency to 50Hz for servo motors

# Function to move the servo motor
def move_servo(channel, pulse):
    pca.channels[channel].duty_cycle = pulse

# Mapping of servo motor channels and pulse widths to each color
servo_mapping = {
    'blue': (0, 2000),   # Example: Servo motor for blue ball
    'red': (0, 4000),    # Example: Servo motor for red ball
    'yellow': (0, 6000)  # Example: Servo motor for yellow ball
}

def main():
    # Capture video from USB camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Unable to open camera")
        return

    # Define color ranges in HSV color space
    color_ranges = {
        'blue': ([100, 150, 0], [140, 255, 255]),
        'yellow': ([20, 100, 100], [30, 255, 255])
    }

    while True:
        # Get a frame
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame to 320x240
        frame = cv2.resize(frame, (320, 240))

        # Convert frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a mask for red color (red has two ranges)
        red_lower1 = np.array([0, 120, 70])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([170, 120, 70])
        red_upper2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = mask1 | mask2

        # Create masks for other colors
        masks = {'red': red_mask}
        for color, (lower, upper) in color_ranges.items():
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            masks[color] = cv2.inRange(hsv, lower_bound, upper_bound)

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply binary thresholding
        _, shape_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # Add shape-based mask
        masks['shape'] = shape_mask

        detected_balls = []  # List to store ball information

        for color, mask in masks.items():
            # Detect contours
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                # Calculate contour area
                area = cv2.contourArea(contour)
                if area > 500:
                    # Calculate the enclosing circle
                    ((x, y), radius) = cv2.minEnclosingCircle(contour)
                    center = (int(x), int(y))
                    radius = int(radius)

                    # Check if the shape is circular
                    if radius > 10:
                        circularity = 4 * np.pi * (area / (cv2.arcLength(contour, True) ** 2))
                        if 0.7 < circularity < 1.3:  # Check if shape is close to a circle
                            detected_balls.append((color, area, radius, center))  # Save color, area, radius, and center coordinates

        # If any balls are detected, find the one with the largest area
        if detected_balls:
            largest_ball = max(detected_balls, key=lambda x: x[1])
            color, area, radius, center = largest_ball

            # Move the servo motor based on the color of the largest ball
            move_servo_based_on_color(color)
            time.sleep(1)  # Wait for the servo to stabilize

            # Draw the largest ball
            if color == 'blue':
                cv2.circle(frame, center, radius, (255, 0, 0), 2)
            elif color == 'red':
                cv2.circle(frame, center, radius, (0, 0, 255), 2)
            elif color == 'yellow':
                cv2.circle(frame, center, radius, (0, 255, 255), 2)
            cv2.putText(frame, '1', (center[0] - 10, center[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Display the frame
        cv2.imshow('Frame', frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

# Function to move the servo motor based on the ball color
def move_servo_based_on_color(color):
    if color in servo_mapping:
        channel, pulse = servo_mapping[color]
        move_servo(channel, pulse)

if __name__ == "__main__":
    main()

