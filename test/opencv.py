# Program To Read video
# and Extract Frames
import os
import cv2

class ReadFrames:
    def __init__(self, path):
        self.vidObj = cv2.VideoCapture(path)
        self.success = True
        self.image = None

    def read(self):
        if self.success:
            self.success, image_l = self.vidObj.read()
            dsize = (160, 120)
            image_bgr = cv2.resize(image_l, dsize)
            image_r = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            self.image = cv2.rotate(image_r, cv2.ROTATE_90_CLOCKWISE)
        return self.image


if __name__ == "__main__":
    path = os.path.split(os.path.realpath(__file__))[0]
    v = ReadFrames(os.path.join(path, 'test.mp4'))
    image = v.read()
    cv2.imwrite("frame.jpg", image)

#