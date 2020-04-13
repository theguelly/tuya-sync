import numpy
import cv2
import mss
import time
import pytuya
import _thread
import math

from frame_color_lib import FrameColorLib
FRAME_COLOR_LIB = FrameColorLib()

refresh_rate = 4 ## higher is slower

input_image_reduced_size = 50
channels_min_threshold = 50
channels_max_threshold = 180
dim_brightness = 3
starting_brightness = 110
min_non_zero_count = 0.2
max_non_zero_count = 20
number_of_k_means_clusters = 8
color_spread_threshold = 0.4
color_skip_sensitivity = 30
result_color = None
light_update_wait = .250 * refresh_rate
screen_update_wait = .200 * refresh_rate
skip_frame = False


##left = pytuya.BulbDevice("02056700840d8e8fc52e","10.0.0.61","b4d9303747f70ae3")
##right = pytuya.BulbDevice("66072756807d3a3eeea7","10.0.0.64","4f84c33d3004a9d8")
##ldata = left.status()
##rdata = left.status()
##right.set_status(True)
###print('Dictionary %r' % data)
##print('left state (bool, true is ON) %r' % ldata['dps']['1'])
##print('right state (bool, true is ON) %r' % rdata['dps']['1'])

def bulb_update(name, id, ip, localkey):
        global skip_frame
        print("Enter")
        bulb = pytuya.BulbDevice(id, ip, localkey)
        data = bulb.status();
        print('Dictionary %r' % data)
        bulb.set_status(True)
        while(True):
                try:
                        if not skip_frame:
                                bulb.set_colour(result_color.color[2],result_color.color[1],result_color.color[0])
                except:
                        print(name, " failed to update.")
                time.sleep(light_update_wait)
                
def screen_color():
        global result_color
        global skip_frame
        prev_color = None
        
        with mss.mss() as sct:
                
                while(True):
                                       
                        last_time = time.time()

                        mon1 = sct.monitors[1]
                        box = {
                            'top': mon1['top'] + 300,
                            'left': mon1['left'] + 100,
                            'width': 1960,
                            'height': 880,
                        }
                                
                                    
                        # Get raw pixels from the screen, save it to a Numpy array
                        img = numpy.array(sct.grab(box))
                        
                        # Shrink image for performance sake
                        current_frame = FRAME_COLOR_LIB.shrink_image(img, input_image_reduced_size)
                        
                        # Apply dark color threshold and compute mask
                        masked_frame = FRAME_COLOR_LIB.apply_frame_mask(current_frame, channels_min_threshold)
                        
                        # Calculate relevant color for this frame
                        result_color = FRAME_COLOR_LIB.calculate_hue_color(masked_frame, (number_of_k_means_clusters), color_spread_threshold, channels_min_threshold, channels_max_threshold)
                        
                        print("rgb: ",result_color.color[0]," ",result_color.color[1]," ",result_color.color[2])

                        if prev_color is not None:
                                skip_frame = True
                                for j in range (0,3):
                                        ch_diff = math.fabs(int(prev_color.color[j]) - int(result_color.color[j]))
                                if ch_diff > color_skip_sensitivity:
                                        skip_frame = False
                                print("Frame skipped? ",skip_frame)
                        prev_color = result_color
                        
                        time.sleep(screen_update_wait)

_thread.start_new_thread(screen_color,())
_thread.start_new_thread(bulb_update,("Left","02056700840d8e8fc52e","10.0.0.61","b4d9303747f70ae3"))
_thread.start_new_thread(bulb_update,("Right","66072756807d3a3eeea7","10.0.0.64","4f84c33d3004a9d8"))

while 1:
   pass
