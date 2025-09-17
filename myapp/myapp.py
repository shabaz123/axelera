#!/usr/bin/env python3
# ANPR-for-All
# rev 0.1 - shabaz - August 2025

# ANPR app for Metis M.2 AI Module on
# Aetina RK3588 platform

import os
import pwd
import sys
import time
import cv2
import find_camera

# globals
camera_search_term = "HD Pro"  # part of the camera name to search for
input_source_name = ""  # this will be set later to (say) "usb:20"
stream = None  # the inference stream object

# terminal colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"

user = pwd.getpwuid(os.getuid()).pw_name
print(f"Running as user: {user}")

if not os.environ.get('AXELERA_FRAMEWORK'):
    print(f"{BOLD}{RED}Please activate the Axelera environment! Type:{RESET}")
    print("source /axelera/voyager-sdk/venv/bin/activate")
    print("and run again")
    sys.exit(1)

# add the voyager-sdk path to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "/axelera/voyager-sdk"))
sys.path.append(project_root)

from axelera.app import config, display
from axelera.app.stream import create_inference_stream

# banner title
def print_banner():
    print("\n\n\n")
    print(f"          _   _ _____  _____   __                  _ _ ")
    print(f"    /\   | \ | |  __ \|  __ \ / _|           /\   | | |")
    print(f"   /  \  |  \| | |__) | |__) | |_ ___  _ __ /  \  | | |")
    print(f"  / /\ \ | . ` |  ___/|  _  /|  _/ _ \| '__/ /\ \ | | |")
    print(f" / ____ \| |\  | |    | | \ \| || (_) | | / ____ \| | |")
    print(f"/_/    \_\_| \_|_|    |_|  \_\_| \___/|_|/_/    \_\_|_|")
    print("\n")
    print(f"Automatic Number Plate Recognition")
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n")

# returns True if camera found
# sets input_source_name to a value like "usb:20"
def locate_camera():
    global input_source_name
    camera_id = find_camera.find_camera(camera_search_term)
    if camera_id < 0:
        return False
    else:
        input_source_name = f"usb:{camera_id}"
        print(f"Camera '{camera_search_term}' found as {input_source_name} (/dev/video{camera_id})")
        return True
    
#########################################################
# inference loop
#########################################################
def inference_loop(window, stream, app):
    window.options(0, title="Vehicles View")  # window #0
    VEHICLE = ('car', 'truck', 'motorcycle')
    PLATES = ('licenseplate',)  
    center = lambda box: ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)

    for frame_result in stream:
        boxlist = []  # list of all of the boxes in this frame
        window.show(frame_result.image, frame_result.meta, frame_result.stream_id)
        # for veh in frame_result.tracking:
        # for veh in frame_result["plate-detections"]:
        for veh in getattr(frame_result, "tracking"):
            if veh.label.name not in PLATES:
                continue
            if len(veh.history) < 2:
                continue
            boxlist.append(veh.history[0])
            # print(f"{veh.label.name} {veh.track_id}: {center(veh.history[0])} → {center(veh.history[-1])} @ stream {frame_result.stream_id}")
        # find the top three largest boxes
        boxlist = sorted(boxlist, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)[:3]
        for b in boxlist:
            print(f"box: {b} center: {center(b)}")
        # if there is one or more boxes, crop the largest one and save it to out.jpg
        if len(boxlist) > 0:
            box = boxlist[0]
            # x1, y1, x2, y2 = box
            pil_img = frame_result.image.aspil()
            crop = pil_img.crop(box)
            crop.save("output_crop.jpg", format="JPEG", quality=95)

        image, meta = frame_result.image, frame_result.meta
        if image is None and meta is None:
            if window.is_closed:
                break
            continue

        if image:
            window.show(image, meta, frame_result.stream_id)

        if window.is_closed:
            break
    if stream.is_single_image():  # and args.display:
        print("stream has a single frame, close the window or press Q to exit...")
        window.wait_for_close()

#########################################################
# main function
#########################################################
def main():
    global stream
    if not locate_camera():
        print(f"{BOLD}{RED}Camera with name containing '{camera_search_term}' not found!{RESET}")
        sys.exit(1)
    print_banner()

    
    # was network="yolov5m-v7-coco-tracker",
    # replaced with
    # network="vehicles-then-plates",
    try:
        stream = create_inference_stream(
            network="vehicle-plates-reference-design",
            sources=[
                # str(input_source_name),
                "/axelera/voyager-sdk/media/test_traffic_h264_1080p60.mp4",
            ],
        )

        with display.App(visible=True) as app:
            wnd = app.create_window("Graphic Window", (900, 600))
            app.start_thread(inference_loop, (wnd, stream, app), name='InferenceThread')
            app.run()
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"{BOLD}{RED}Error: {e}{RESET}")
    finally:
        if stream:
            stream.stop()
        print("Exiting")



if __name__ == "__main__":
    main()