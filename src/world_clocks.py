import numpy as np
import cv2 as cv
import math
from datetime import datetime
import pytz

radius = 80  # small to fit multiple clocks

# Function to create noisy background
def create_noise_background(shape):
    # Create base noise with wider range including darker values
    noise = np.random.randint(100, 200, (shape[0]//8, shape[1]//8), dtype=np.uint8)
    
    # Resize to full size using nearest neighbor interpolation for pixelated effect
    noise = cv.resize(noise, (shape[1], shape[0]), interpolation=cv.INTER_NEAREST)
    
    # Coarse grain noise with darker variations
    # Values from 0 to 60 and subtract 30 to get range -30 to +30
    fine_noise = np.random.randint(0, 60, (shape[0]//4, shape[1]//4), dtype=np.uint8)
    fine_noise = fine_noise - 30  # Now we have values from -30 to +30
    fine_noise = cv.resize(fine_noise, (shape[1], shape[0]), interpolation=cv.INTER_NEAREST)
    
    # Add the noise and clip to valid range
    noise = noise.astype(np.int16) + fine_noise  # Convert to int16 to handle negative values
    noise = np.clip(noise, 0, 255).astype(np.uint8)
    
    # Convert to 3 channels
    noise = cv.merge([noise, noise, noise])
    
    return noise

def clock(image, center, timezone_str):
    # Get current time in the specified timezone
    timezone = pytz.timezone(timezone_str)
    now = datetime.now(pytz.UTC).astimezone(timezone)
    
    # Background circle
    cv.circle(image, center, radius, (255, 255, 255), thickness=-1)
    
    # Border of watch
    cv.circle(image, center, radius, (0, 0, 0), thickness=2)

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
    cv.line(image, center, hour_end, (0, 0, 0), thickness=4)     # Hour hand (thickest)
    cv.line(image, center, minute_end, (0, 0, 0), thickness=3)   # Minute hand (medium)
    cv.line(image, center, second_end, (0, 0, 190), thickness=2) # Second hand (thinnest, in red)

    # Add timezone label
    offset = timezone.utcoffset(datetime.now()).total_seconds() / 3600
    label = f"UTC{'+' if offset >= 0 else ''}{int(offset)}"
    text_size = cv.getTextSize(label, cv.FONT_HERSHEY_COMPLEX_SMALL, 1.2, 2)[0]
    text_x = center[0] - text_size[0] // 2
    text_y = center[1] + radius + 35
    cv.putText(image, label, (text_x, text_y), cv.FONT_HERSHEY_COMPLEX_SMALL, 1.2, (0, 0, 0), 2)

    # Add city name
    city = timezone_str.split('/')[-1].replace('_', ' ')
    text_size = cv.getTextSize(city, cv.FONT_HERSHEY_COMPLEX_SMALL, 1.2, 2)[0]
    text_x = center[0] - text_size[0] // 2
    text_y = center[1] + radius + 65
    cv.putText(image, city, (text_x, text_y), cv.FONT_HERSHEY_COMPLEX_SMALL, 1.2, (0, 0, 0), 2)

    return image

img = np.full((700, 1200, 3), 255, np.uint8)  # Adjusted height for better spacing

# Define the timezones and their positions
timezones = [
    # Row 1
    ('America/Los_Angeles', (200, 200)),  # Los Angeles
    ('America/New_York', (400, 200)),     # New York
    ('America/Caracas', (600, 200)),      # Caracas
    ('Europe/Paris', (800, 200)),         # Paris
    ('Europe/London', (1000, 200)),       # London
    
    # Row 2
    ('Asia/Dubai', (200, 450)),           # Dubai
    ('Asia/Shanghai', (400, 450)),        # Shanghai
    ('Asia/Tokyo', (600, 450)),           # Tokyo
    ('Australia/Sydney', (800, 450)),     # Sydney
    ('Pacific/Auckland', (1000, 450)),    # Auckland
]

last_second = None

while True:
    # Noise background instead of solid white
    img = create_noise_background((700, 1200, 3))
    
    # Current time to check if we need to update clocks
    current_time = datetime.now()
    current_second = current_time.second
    
    # Store the clock overlay if it's a new second or first run
    if last_second is None or current_second != last_second:
        # Create a clean overlay for clocks
        clock_overlay = np.zeros((700, 1200, 3), dtype=np.uint8)
        clock_overlay.fill(255)  # Fill with white instead of black
        
        # Draw all clocks on the overlay
        for tz, pos in timezones:
            clock(clock_overlay, pos, tz)
            
        # Store the current second
        last_second = current_second
    
    # Combine background noise with clock overlay
    final_img = img.copy()
    
    # Create mask from non-white pixels in the overlay
    mask = np.all(clock_overlay != [255, 255, 255], axis=2)
    
    # Apply the mask
    final_img[mask] = clock_overlay[mask]
    
    # Add white background for clock faces
    for _, pos in timezones:
        cv.circle(final_img, pos, radius, (255, 255, 255), thickness=-1)
        
    # Redraw clocks on top to ensure clean appearance
    for tz, pos in timezones:
        clock(final_img, pos, tz)
    
    # Display the image in a window named 'World Clocks'
    cv.imshow('World Clocks', final_img)
    
    # Wait for 50ms and check if window was closed
    key = cv.waitKey(50)
    if key & 0xFF == ord('q') or cv.getWindowProperty('World Clocks', cv.WND_PROP_VISIBLE) < 1:
        break

cv.destroyAllWindows()