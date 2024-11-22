#!/bin/bash

# Check if an ASCII video file is provided as an argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 ascii_video_file"
    exit 1
fi

ASCII_VIDEO_FILE="$1"

# Set the frames per second (should match the FPS used when generating the ASCII video)
FPS=30
DELAY=$(awk "BEGIN {print 1/$FPS}")

# Read the frames from the specified ASCII video file
frame=""
while IFS= read -r line; do
    if [[ "$line" == "===FRAME===" ]]; then
        # Clear the terminal screen
        clear
        # Display the frame
        printf '%s\n' "$frame"
        # Wait for the next frame
        sleep "$DELAY"
        # Reset the frame buffer
        frame=""
    else
        # Append the line to the current frame
        frame+="$line"$'\n'
    fi
done < "$ASCII_VIDEO_FILE"

