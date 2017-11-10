import argparse
import time
import cv2
import numpy

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-t", "--threshold", type=int, default=10, help="minimum threshold")
ap.add_argument("-d", "--delay", type=float, default=0, help="delay between frames processing (ignored if video file is specified)")
ap.add_argument("-a", "--accumalation", type=float, default=0.1, help="accumalation factor; e.g 0.5 to combine the mean image with the new image with the same weight")
args = vars(ap.parse_args())

if args.get("video", None) is None:
    # 0 is probably the webcam
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)
else:
    camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
mean_frame = None
frame_count = 0
thresh = args['threshold']

while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    text = "Unoccupied"
    frame_count += 1

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (21, 21), 0)

    if mean_frame is None:
        print("[INFO] starting background model...")
        mean_frame = frame.copy().astype("float")
        continue

    frame_delta = cv2.absdiff(cv2.convertScaleAbs(mean_frame), frame)
    frame_thresh = cv2.threshold(frame_delta, thresh, 255, cv2.THRESH_BINARY)[1]
    percentage = numpy.sum(frame_thresh) / 255.0 / frame_thresh.size
    cv2.imwrite('frame_%d.png' % frame_count, frame_thresh)
    cv2.imwrite('mean_%d.png' % frame_count, mean_frame)

    print("Frame {:d}: diff {:.2%}".format(frame_count, percentage))

    if args.get('delay') and not args.get('video'):
        time.sleep(args.get('delay'))

    cv2.accumulateWeighted(frame, mean_frame, 0.1)
