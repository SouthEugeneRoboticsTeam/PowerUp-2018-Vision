#!/usr/bin/env python

import cv2
import numpy as np
import vision.cv_utils as cv_utils
import vision.nt_utils as nt_utils
from imutils.video import WebcamVideoStream
from . import args
import os

verbose = args["verbose"]


class Vision:
    def __init__(self):
        self.args = args

        self.cube_lower = np.array(self.args["cube_lower_color"])
        self.cube_upper = np.array(self.args["cube_upper_color"])

        self.tape_lower = np.array(self.args["tape_lower_color"])
        self.tape_upper = np.array(self.args["tape_upper_color"])

        self.min_area = int(self.args["min_area"])
        self.max_area = int(self.args["max_area"])

        self.image = self.args["image"]

        self.display = self.args["display"]

        self.verbose = self.args["verbose"]

        self.source = self.args["source"]

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
            x2, y2, w2, h2 = cv2.boundingRect(blobs[1])

            area = w1 * h1 + w2 * h2
            if (area > self.min_area) and (area < self.max_area):
                if verbose:
                    print("Cube] x: %d, y: %d, w: %d, h: %d, total "
                          "area: %d" % (x1, y1, w1, h1, area))

                offset_x, offset_y = cv_utils.process_image(
                    im, x1, y1, w1, h1, x2, y2, w2, h2
                )

                print(offset_x, offset_y)

                if self.display:
                    # Draw image details
                    im = cv_utils.draw_images(im, x1, y1, w1, h1)
                    im = cv_utils.draw_images(im, x2, y2, w2, h2)

                    return im

                try:
                    nt_utils.put_boolean("cube_found", True)
                    nt_utils.put_number("cube_offset_x", offset_x)
                    nt_utils.put_number("cube_offset_y", offset_y)
                except:
                    pass
            else:
                try:
                    nt_utils.put_boolean("tape_found", False)
                except:
                    pass
        else:
            try:
                nt_utils.put_boolean("tape_found", False)
            except:
                pass

        return im

    def run_image(self):
        if self.verbose:
            print("Image path specified, reading from %s" % self.image)

        bgr = cv2.imread(self.image)
        im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        blobs, im_mask = cv_utils.get_blob(im, self.cube_lower, self.cube_upper)
        if blobs is not None:
            x1, y1, w1, h1 = cv2.boundingRect(blobs[0])
            x2, y2, w2, h2 = cv2.boundingRect(blobs[1])

            if w1 * h1 > self.min_area and w2 * h2 > self.min_area:
                if verbose:
                    print("[Blob 1] x: %d, y: %d, w: %d, h: %d, "
                          "area: %d" % (x1, y1, w1, h1, w1 * h1))
                    print("[Blob 2] x: %d, y: %d, w: %d, h: %d, "
                          "area: %d" % (x2, y2, w2, h2, w2 * h2))

                im_rect = cv_utils.draw_images(
                    im, x1, y1, w1 + (x2 - x1), h2, False
                )

                offset_x, offset_y = cv_utils.process_image(
                    im, x1, y1, w1, h1, x2, y2, w2, h2
                )

                print(offset_x)
                print(offset_y)

                try:
                    nt_utils.put_number("offset_x", offset_x)
                    nt_utils.put_number("offset_y", offset_y)
                except:
                    pass
        else:
            if verbose:
                print("No largest blob was found")

        if self.display:
            # Show the images
            if blobs is not None:
                cv2.imshow("Original", cv2.cvtColor(im_rect, cv2.COLOR_HSV2BGR))
                cv2.imshow("Mask", im_mask)
            else:
                cv2.imshow("Original", cv2.cvtColor(im, cv2.COLOR_HSV2BGR))

            cv2.waitKey(0)

            cv2.destroyAllWindows()

    def run_video(self):
        camera = WebcamVideoStream(src=self.source).start()

        if self.verbose:
            print("No image path specified, reading from camera video feed")

        timeout = 0

        while True:
            if nt_utils.get_boolean("shutdown", False):
                os.system("shutdown -H now")
                break

            bgr = camera.read()
            im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

            try:
                cube_lower = np.array([nt_utils.get_number("cube_lower_hue"),
                                       nt_utils.get_number("cube_lower_sat"),
                                       nt_utils.get_number("cube_lower_val")])
                cube_upper = np.array([nt_utils.get_number("cube_upper_hue"),
                                       nt_utils.get_number("cube_upper_sat"),
                                       nt_utils.get_number("cube_upper_val")])
            except:
                cube_lower = self.cube_lower
                cube_upper = self.cube_upper

            try:
                tape_lower = np.array([nt_utils.get_number("tape_lower_hue"),
                                       nt_utils.get_number("tape_lower_sat"),
                                       nt_utils.get_number("tape_lower_val")])
                tape_upper = np.array([nt_utils.get_number("tape_upper_hue"),
                                       nt_utils.get_number("tape_upper_sat"),
                                       nt_utils.get_number("tape_upper_val")])
            except:
                tape_lower = self.tape_lower
                tape_upper = self.tape_upper

            if im is not None:
                im = cv2.resize(im, (680, 480), 0, 0)

                cube_blobs, cube_mask = cv_utils.get_blob(im, cube_lower, cube_upper)
                tape_blobs, tape_mask = cv_utils.get_blob(im, tape_lower, tape_upper)

                im = self.do_image(im, cube_blobs)
                im = self.do_image(im, tape_blobs)

                if cube_blobs is not None or tape_blobs is not None:
                    if self.display:
                        # Show the images
                        cv2.imshow("Orig", cv2.cvtColor(im, cv2.COLOR_HSV2BGR))

                        if cube_blobs is not None:
                            cv2.imshow("Cube", cube_mask)

                        if tape_mask is not None:
                            cv2.imshow("Tape", tape_mask)
                else:
                    if verbose:
                        print("No largest blob found")

                    if self.display:
                        cv2.imshow("Orig", cv2.cvtColor(im, cv2.COLOR_HSV2BGR))

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                if (timeout == 0):
                    print("No camera detected")

                timeout += 1

                if (timeout > 500):
                    print("Camera search timed out")
                    break

        cv2.destroyAllWindows()
