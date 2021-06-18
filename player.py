import os
import sys
import cv2
import curses
import argparse
import time

parser = argparse.ArgumentParser(description='ASCII Player')
parser.add_argument("--width", type=int, default = 120, help="width of the terminal window")
parser.add_argument("--fps", type=int, default = 30, help="width of the terminal window")
parser.add_argument("--show", type=bool, default = False, help="width of the terminal window")
parser.add_argument("video", type=str, help="path to video")
args = parser.parse_args()

width = args.width
characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']

def get_char(val):
    range = int(255 / len(characters))
    return characters[min(int(val/range), len(characters)-1)]


try:
    if not os.path.isfile(args.video):
        print("failed to find video at:", args.video)

    video = cv2.VideoCapture(args.video)
    ok, frame = video.read()
    if not ok:
        print("could not extract frame from video")

    ratio = width/frame.shape[1]
    height = int(frame.shape[0]*ratio) // 2  # charachter height is 2 times character width
    print(frame.shape)
    print(width, height, ratio)

    curses.initscr()
    window = curses.newwin(height, width, 0, 0)

    frame_count = 0
    frames_per_ms = args.fps/1000
    start = time.perf_counter_ns()//1000000
    while True:
        ok, orig_frame = video.read()
        if not ok:
            print("done capturing.")
            break

        frame = cv2.resize(orig_frame, (width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if args.show:
            cv2.imshow("frame", orig_frame)
            cv2.waitKey(1)

        for y in range(0, frame.shape[0]):
            for x in range(0, frame.shape[1]):
                try:
                    window.addch(y, x, get_char(frame[y, x]))
                except (curses.error):
                    pass

        elapsed = (time.perf_counter_ns()//1000000) - start
        supposed_frame_count = frames_per_ms * elapsed
        if frame_count > supposed_frame_count:
            time.sleep((frame_count-supposed_frame_count)*(1/frames_per_ms)/1000)
        window.refresh()
        frame_count += 1
finally:
    cv2.destroyAllWindows()
    curses.endwin()