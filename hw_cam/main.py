import argparse
import datetime
import imutils
import time
import cv2
import numpy
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-t", "--threshold", type=int, default=50, help="minimum threshold")
args = vars(ap.parse_args())

if args.get("video", None) is None:
    # 0 is probably the webcam
    camera = cv2.VideoCapture(1)
    time.sleep(0.25)
else:
    camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
previous_frame = None
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
    frame = imutils.resize(frame, width=500)
    if frame_count <= 1:
        previous_frame = frame
        continue

    if previous_frame.shape != frame.shape:
        print("Frame different")

    frame_delta = cv2.absdiff(previous_frame, frame).sum()

    diff = numpy.mean(frame_delta, axis=2)
    diff[diff<=thresh] = 0
    diff[diff>thresh] = 255
    mask = numpy.dstack([diff]*3)
    below_threshold = len(list(filter(lambda k: k==0, mask.flatten())))
    above_threshold = len(list(filter(lambda k: k!=0, mask.flatten())))
    percentage = below_threshold / (below_threshold + above_threshold)
    print("Frame %s: diff %s%%" % (frame_count, percentage))

    ## show the image
    #         cv2.imshow(text, frame)
    #         cv2.waitKey(0)
    #         cv2.destroyAllWindows()

    time.sleep(5)

    previous_frame = frame
