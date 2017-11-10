import argparse
import datetime
import imutils
import time
import cv2
import numpy
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-t", "--threshold", type=int, default=10**6, help="minimum threshold")
args = vars(ap.parse_args())

if args.get("video", None) is None:
    # 0 is probably the webcam
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)
else:
    camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
previous_frame = None
frame_count = 0
thresh = args['threshold']

def wait(seconds):
    t1 = time.time()
    t2 = time.time()
    while (t2-t1) < seconds:
        _ = camera.read()
        t2 = time.time()

while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    frame_count += 1

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        print("Frame %s not grabbed" % frame_count)
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (21, 21), 0)

    if frame_count <= 1:
        previous_frame = frame
        continue

    if previous_frame.shape != frame.shape:
        print("Frame different, %s vs %s" % (previous_frame.shape, frame.shape) )
        break

    frame_delta = cv2.absdiff(previous_frame, frame)
    print("Frame %s" % frame_count)

    # cv2.imwrite("/tmp/foo.jpg", frame_delta)
    # cv2.imshow("foo", frame_delta)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    if frame_delta.sum() > thresh:
        print("MOVED! %s" % frame_delta.sum())

    # diff = numpy.mean(frame_delta, axis=2)
    # diff[diff<=thresh] = 0
    # diff[diff>thresh] = 255
    # mask = numpy.dstack([diff]*3)
    # below_threshold = len(list(filter(lambda k: k==0, mask.flatten())))
    # above_threshold = len(list(filter(lambda k: k!=0, mask.flatten())))
    # percentage = below_threshold / (below_threshold + above_threshold)
    # print("Frame %s: diff %s%%" % (frame_count, percentage))

    wait(3)

    previous_frame = frame
