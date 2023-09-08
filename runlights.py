import numpy
import mss
import time
import tinytuya
import _thread
import math
import os
from dotenv import load_dotenv
from frame_color_lib import FrameColorLib

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID")
DEVICE_IP = os.getenv("DEVICE_IP")
DEVICE_LOCAL_KEY = os.getenv("DEVICE_LOCAL_KEY")

FRAME_COLOR_LIB = FrameColorLib()

refresh_rate = 1 ## higher is slower

input_image_reduced_size = 100
channels_min_threshold = 50
channels_max_threshold = 190
dim_brightness = 3
starting_brightness = 1000
min_non_zero_count = 0.2
max_non_zero_count = 20
number_of_k_means_clusters = 10
color_spread_threshold = 0.4
color_skip_sensitivity = 10
result_color = None
light_update_wait = .250 * refresh_rate
screen_update_wait = .200 * refresh_rate
skip_frame = False
first_run = True
monitor_index = 1

def bulb_update(name, id, ip, localkey):
    global skip_frame
    global first_run
    bulb = tinytuya.BulbDevice(
        dev_id=id,
        address=ip,      # Or set to 'Auto' to auto-discover IP address
        local_key=localkey, 
        version=3.3
    )

    try:
        data = bulb.status();
        print(name, 'State: %r' % 'on' if data['dps']['20'] else 'off')  
        bulb.set_status(True)
        while(True):
            try:
                if first_run or not skip_frame:
                    if is_monochrome_color((result_color.color[2], result_color.color[1], result_color.color[0]), tolerance=10):
                        bulb.set_white_percentage((result_color.color[2] / 255) * 100, 100, nowait=True)
                        print_bgr_color((result_color.color[2], result_color.color[2], result_color.color[2]), text='set white: success!')
                    else:
                        bulb.set_colour(r=result_color.color[2], g=result_color.color[1], b=result_color.color[0], nowait=True)
                        print_bgr_color((result_color.color[2], result_color.color[1], result_color.color[0]), text='set color: success!')
                    first_run = False
            except Exception as e:
                print(name, " failed to update.")
                print(str(e))
            time.sleep(light_update_wait)
    except:
        print('Light State: \'off\'')

                
def screen_color():
    global result_color
    global skip_frame
    prev_color = None
    
    with mss.mss() as sct:
        while(True):        
            last_time = time.time()

            mon1 = sct.monitors[monitor_index]
                        
            # Get raw pixels from the screen, save it to a Numpy array
            img = numpy.array(sct.grab(mon1))
            
            # Shrink image for performance sake
            current_frame = FRAME_COLOR_LIB.shrink_image(img, input_image_reduced_size)
            
            # Apply dark color threshold and compute mask
            masked_frame = FRAME_COLOR_LIB.apply_frame_mask(current_frame, channels_min_threshold)
            
            # Calculate relevant color for this frame
            result_color = FRAME_COLOR_LIB.calculate_hue_color(masked_frame, (number_of_k_means_clusters), color_spread_threshold, channels_min_threshold, channels_max_threshold)
            
            if prev_color is not None:
                skip_frame = True
                for j in range (0,3):
                    ch_diff = math.fabs(int(prev_color.color[j]) - int(result_color.color[j]))
                if ch_diff > color_skip_sensitivity:
                    skip_frame = False
                if prev_color.brightness != result_color.brightness:
                    skip_frame = False

            prev_color = result_color
            
            time.sleep(screen_update_wait)

def is_monochrome_color(rgb, tolerance=10):
    # Extract the individual RGB values
    r, g, b = rgb

    # Check if the absolute differences between channels are within the tolerance
    return abs(int(r) - int(g)) <= tolerance and abs(int(r) - int(b)) <= tolerance and abs(int(g) - int(b)) <= tolerance

def print_bgr_color(rgb, text):
    r, g, b = rgb
    color_code = f"\x1b[38;2;{r};{g};{b}m"
    textrgb = f'R:{str(r).rjust(3, "0")}|G:{str(g).rjust(3, "0")}|B:{str(b).rjust(3, "0")}'
    
    # Reset text color
    reset_code = "\x1b[0m"
    
    # Print the colored text
    print(f"{color_code}{text} ({textrgb}){reset_code}")

_thread.start_new_thread(screen_color,())
_thread.start_new_thread(bulb_update,('Main Light', DEVICE_ID, DEVICE_IP, DEVICE_LOCAL_KEY))

while 1:
   pass
