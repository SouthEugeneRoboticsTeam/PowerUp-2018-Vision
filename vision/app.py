#!/usr/bin/env python

import cv2
import numpy as np
import vision.cv_utils as cv_utils
import vision.network_utils as network
from imutils.video import WebcamVideoStream
from . import args


class Vision:
    def __init__(self):
        self.args = args

        self.cube_lower = np.array(self.args["cube_lower_color"])
        self.cube_upper = np.array(self.args["cube_upper_color"])

        self.min_area = int(self.args["min_area"])
        self.max_area = int(self.args["max_area"])

        self.image = self.args["image"]

        self.display = self.args["display"]

        self.verbose = self.args["verbose"]

        self.source = self.args["source"]

        self.kill_received = False

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

                network.send({"found": True,
                              "offset_x": offset_x,
                              "offset_y": offset_y})

                if self.display:
                    # Draw image details
                    im = cv_utils.draw_images(im, x1, y1, w1, h1)

                    return im
            else:
                network.send_new({"found": False})
        else:
            network.send_new({"found": False})

        return im

    def run_image(self):
        if self.verbose:
            print("Image path specified, reading from %s" % self.image)

        bgr = cv2.imread(self.image)
        im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        cube_blobs, cube_mask = cv_utils.get_blob(im, self.cube_lower, self.cube_upper)

        im = self.do_image(im, cube_blobs)

        if self.display:
            # Show the images
            cv2.imshow("Original", cv2.cvtColor(im, cv2.COLOR_HSV2BGR))

            if cube_blobs is not None:
                cv2.imshow("Cube", cube_mask)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run_video(self):
        if self.verbose:
            print("No image path specified, reading from camera video feed")

        camera = WebcamVideoStream(src=self.source).start()

        timeout = 0

        while not self.kill_received:
            bgr = camera.read()

            cube_lower = self.cube_lower
            cube_upper = self.cube_upper

            if bgr is not None:
                im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
                im = cv2.resize(im, (680, 480), 0, 0)

                cube_blobs, cube_mask = cv_utils.get_blob(im, cube_lower, cube_upper)

                im = self.do_image(im, cube_blobs)

                if cube_blobs is not None and self.display and cube_blobs is not None:
                        cv2.imshow("Cube", cube_mask)
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

    def stop(self):
        self.kill_received = True

    @property
    def stopped(self):
        return self.kill_received
