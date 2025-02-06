import numpy as np
import cv2 as cv
import math
from datetime import datetime

radius = 200


def clock(image, center=(256, 256)):
    # Get current time
    now = datetime.now()
    
    # Background circle
    cv.circle(image, center, radius, (255, 255, 255), thickness=-1)
    
    # Border of watch
    cv.circle(image, center, radius, (0, 0, 0), thickness=5)

    # Draw hour markers
    for hour in range(12):

        # Calculate angle for each hour (30 degrees per hour)
        angle = math.radians(hour * 30 - 90)  # -90 to start at 12 o'clock

        # Start from 90% of radius for the outer end
        start_length = radius * 0.9
    
        # End at 80% of radius for the inner end
        end_length = radius * 0.8

        start_point = (
            int(center[0] + start_length * math.cos(angle)),
            int(center[1] + start_length * math.sin(angle))
        )
        end_point = (
            int(center[0] + end_length * math.cos(angle)),
            int(center[1] + end_length * math.sin(angle))
        )

        thickness = 2

        cv.line(image, start_point, end_point, (0, 0, 0), thickness)
    
    # Calculate angles for each hand
    # Hour hand: 360° / 12 = 30° per hour + small adjustment for minutes
    hour_angle = math.radians((now.hour % 12 + now.minute / 60.0) * 30 - 90)
    
    # Minute hand: 360° / 60 = 6° per minute + small adjustment for seconds
    minute_angle = math.radians(now.minute * 6 + now.second / 10.0 - 90)
    
    # Second hand: 360° / 60 = 6° per second
    second_angle = math.radians(now.second * 6 - 90)
    
    # Calculate end points for clock hands
    # Hour hand (shorter)
    hour_length = radius * 0.5
    hour_end = (
        int(center[0] + hour_length * math.cos(hour_angle)),
        int(center[1] + hour_length * math.sin(hour_angle))
    )
    
    # Minute hand (longer)
    minute_length = radius * 0.7
    minute_end = (
        int(center[0] + minute_length * math.cos(minute_angle)),
        int(center[1] + minute_length * math.sin(minute_angle))
    )
    
    # Second hand (longest and thinnest)
    second_length = radius * 0.9
    second_end = (
        int(center[0] + second_length * math.cos(second_angle)),
        int(center[1] + second_length * math.sin(second_angle))
    )
    
    # Draw the hands
    cv.line(image, center, hour_end, (0, 0, 0), thickness=6)     # Hour hand (thickest)
    cv.line(image, center, minute_end, (0, 0, 0), thickness=4)   # Minute hand (medium)
    cv.line(image, center, second_end, (0, 0, 190), thickness=2) # Second hand (thinnest, in red)

    return image

# Example usage
img = np.full((512, 512, 3), 255, np.uint8)  # Creating np array filled with 255 (white)

while True:
    img.fill(255)  # Reset to white background
    clock(img)  # Draw clock
    
    # Display the image in a window named 'Clock'
    cv.imshow('Clock', img)
    
    # Wait for 1000ms (1 second) and check if window was closed
    key = cv.waitKey(1000)
    if key & 0xFF == ord('q') or cv.getWindowProperty('Clock', cv.WND_PROP_VISIBLE) < 1:
        break

cv.destroyAllWindows()