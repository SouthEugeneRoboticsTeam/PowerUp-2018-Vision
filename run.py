#!/usr/bin/env python

import time
import vision.network_utils as network
from vision.app import Vision
from threading import Thread


class VisionWorker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.kill_received = False
        self.app = Vision()

    def run(self):
        while not self.kill_received:
            self.app.run_frame()


class HeartbeatWorker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.kill_received = False

    def run(self):
        while not self.kill_received:
            self.heartbeat()

    def heartbeat(self):
        network.send({"alive": True})
        time.sleep(0.25)


def main():
    threads = [VisionWorker(), HeartbeatWorker()]

    for t in threads:
        t.start()

    while len(threads) > 0:
        try:
            print(threads)
            print(len(threads))
            threads = [t for t in threads if t is not None and t.isAlive()]
            time.sleep(2)
        except KeyboardInterrupt:
            print("Ctrl-c received! Sending kill to threads...")
            for t in threads:
                t.kill_received = True


if __name__ == '__main__':
    main()
