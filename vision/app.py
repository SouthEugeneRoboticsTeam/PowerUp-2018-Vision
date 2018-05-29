#!/usr/bin/env python

import cv2
import numpy as np
import vision.cv_utils as cv_utils
from vision.network_utils import Network
from imutils.video import WebcamVideoStream
from . import args


class Vision:
    def __init__(self):
        self.args = args

        self.lower = np.array(self.args["lower_color"])
        self.upper = np.array(self.args["upper_color"])

        self.min_area = int(self.args["min_area"])
        self.max_area = int(self.args["max_area"])

        self.image = self.args["image"]
        self.image_out = self.args["output"]

        self.display = self.args["display"]
        self.source = self.args["source"]
        self.tuning = self.args["tuning"]
        self.verbose = self.args["verbose"]

        self.kill_received = False

        self.network = Network()

        if self.verbose:
            print(self.args)

    def run(self):
        if self.image is not None:
            self.run_image()
        else:
            self.run_video()

    def do_image(self, im, blobs):
        if blobs is not None:
            x1, y1, w1, h1 = cv2.boundingRect(blobs[0])

            area = w1 * h1
            if (area > self.min_area) and (area < self.max_area):
                if self.verbose:
                    print("[Cube] x: %d, y: %d, w: %d, h: %d, total "
                          "area: %d" % (x1, y1, w1, h1, area))

                offset_x, offset_y = cv_utils.process_image(im, x1, y1, w1, h1)

                self.network.send({"found": True,
                                   "offset_x": offset_x,
                                   "offset_y": offset_y})

                if self.display:
                    # Draw image details
                    im = cv_utils.draw_images(im, x1, y1, w1, h1)

                    return im
            else:
                self.network.send_new({"found": False})
        else:
            self.network.send_new({"found": False})

        return im

    def run_image(self):
        if self.verbose:
            print("Image path specified, reading from %s" % self.image)

        bgr = cv2.imread(self.image)
        im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        # Ensure that things get drawn as if it were to be displayed
        old_display = self.display
        self.display = True

        blobs, mask = cv_utils.get_blob(im, self.lower, self.upper)

        im = self.do_image(im, blobs)

        self.display = old_display

        if self.display:
            # Show the images
            cv2.imshow("Original", cv2.cvtColor(im, cv2.COLOR_HSV2BGR))

            if blobs is not None:
                cv2.imshow("Cube", mask)

            cv2.waitKey(0)
            cv2.destroyAllWindows()

        if self.image_out is not None:
            if mask is None:
                mask = np.zeros(im.shape[0:2])

            print(im.shape)
            print(mask.shape)

            cv2.imwrite(self.image_out, np.concatenate((cv2.cvtColor(np.uint8(im), cv2.COLOR_HSV2BGR), cv2.cvtColor(np.uint8(mask), cv2.COLOR_GRAY2BGR)), axis=0))

        self.kill_received = True

    def run_video(self):
        if self.verbose:
            print("No image path specified, reading from camera video feed")

        camera = WebcamVideoStream(src=self.source).start()

        timeout = 0

        if self.tuning:
            cv2.namedWindow("Settings")
            cv2.resizeWindow("Settings", 700, 350)

            cv2.createTrackbar("Lower H", "Settings", self.lower[0], 255,
                               lambda val: self.update_setting(True, 0, val))
            cv2.createTrackbar("Lower S", "Settings", self.lower[1], 255,
                               lambda val: self.update_setting(True, 1, val))
            cv2.createTrackbar("Lower V", "Settings", self.lower[2], 255,
                               lambda val: self.update_setting(True, 2, val))

            cv2.createTrackbar("Upper H", "Settings", self.upper[0], 255,
                               lambda val: self.update_setting(False, 0, val))
            cv2.createTrackbar("Upper S", "Settings", self.upper[1], 255,
                               lambda val: self.update_setting(False, 1, val))
            cv2.createTrackbar("Upper V", "Settings", self.upper[2], 255,
                               lambda val: self.update_setting(False, 2, val))

        while not self.kill_received:
            bgr = camera.read()

            if bgr is not None:
                im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
                im = cv2.resize(im, (680, 480), 0, 0)

                blobs, mask = cv_utils.get_blob(im, self.lower, self.upper)

                im = self.do_image(im, blobs)

                if blobs is not None and self.display and blobs is not None:
                        cv2.imshow("Cube", mask)
                elif self.verbose:
                        print("No largest blob found")

                if self.display:
                    cv2.imshow("Original", cv2.cvtColor(im, cv2.COLOR_HSV2BGR))

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.kill_received = True
                    break
            else:
                if timeout == 0:
                    print("No camera detected... Retrying...")

                timeout += 1

                if timeout > 5000:
                    print("Camera search timed out!")
                    break

        camera.stop()
        cv2.destroyAllWindows()

    def update_setting(self, lower, index, value):
        if lower:
            self.lower[index] = value
        else:
            self.upper[index] = value

    def stop(self):
        self.kill_received = True

    @property
    def stopped(self):
        return self.kill_received
