import os
import cv2
import argparse
import time
from functools import lru_cache
import curses

parser = argparse.ArgumentParser(description='ASCII Player')
parser.add_argument("--width", type=int, default=120, help="width of the ASCII art")
parser.add_argument("--fps", type=int, default=30, help="frames per second")
parser.add_argument("--inv", action='store_true', help="invert the shades")
parser.add_argument("--output", type=str, help="output text file to save ASCII frames")
parser.add_argument("video", type=str, help="path to video file or webcam index")
args = parser.parse_args()

video = args.video
try:
    video = int(video)
except ValueError:
    pass

width = args.width
characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']
if args.inv:
    characters = characters[::-1]
char_range = int(255 / len(characters))

@lru_cache(maxsize=None)
def get_char(val):
    return characters[min(int(val / char_range), len(characters) - 1)]

if isinstance(video, str) and not os.path.isfile(video):
    print("Failed to find video at:", args.video)
    exit(1)

video = cv2.VideoCapture(video)
ok, frame = video.read()
if not ok:
    print("Could not extract frame from video")
    exit(1)

ratio = width / frame.shape[1]
height = int(frame.shape[0] * ratio * 0.5)  # Adjust for character dimensions

frame_count = 0
start_time = time.time()

try:
    if args.output:
        # Saving frames to a text file
        with open(args.output, 'w') as f:
            while True:
                ok, orig_frame = video.read()
                if not ok:
                    break

                frame = cv2.resize(orig_frame, (width, height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Generate ASCII art for the frame
                ascii_frame = '\n'.join(
                    ''.join(get_char(pixel) for pixel in row)
                    for row in frame
                )

                # Write the frame and a separator to the file
                f.write(ascii_frame + '\n')
                f.write('===FRAME===\n')  # Frame separator

                frame_count += 1

        total_time = time.time() - start_time
        fps = frame_count / total_time
        print(f"Saved {frame_count} frames at an average of {fps:.2f} fps")
    else:
        # Playing the video directly in the terminal using curses
        curses.initscr()
        window = curses.newwin(height, width, 0, 0)
        curses.curs_set(0)  # Hide the cursor

        frame_delay = 1 / args.fps
        last_time = time.time()

        while True:
            ok, orig_frame = video.read()
            if not ok:
                break

            frame = cv2.resize(orig_frame, (width, height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Render the ASCII art onto the window
            for y in range(frame.shape[0]):
                for x in range(frame.shape[1]):
                    try:
                        window.addch(y, x, get_char(frame[y, x]))
                    except curses.error:
                        pass

            window.refresh()
            frame_count += 1

            # Control frame rate
            elapsed = time.time() - last_time
            sleep_time = frame_delay - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_time = time.time()

        total_time = time.time() - start_time
        fps = frame_count / total_time
        print(f"Played {frame_count} frames at an average of {fps:.2f} fps")
except KeyboardInterrupt:
    pass
finally:
    if not args.output:
        curses.endwin()
    cv2.destroyAllWindows()

