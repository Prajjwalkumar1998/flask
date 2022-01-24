import cv2
import numpy as np
import collections
import time
import pyspin


width, height, channels = 720, 540, 3
system = pyspin.System.GetInstance()
blackFly_list = system.GetCameras()
blackFly = blackFly_list.GetByIndex(0)
blackFly.Init()
blackFly.AcquisitionMode.SetValue(pyspin.AcquisitionMode_Continuous)
blackFly.BeginAcquisition()

#color range
lower = np.array([220,220,220])
upper = np.array([255,255,255])

newcameramtx = np.array([[160.37167358,0.0, 383.25053993],
       [0.0, 167.47367859, 313.9882118 ],
       [0.0,0.0,1.0]])

roi = (211, 161, 339, 283)

mtx = np.array([[340.83799544,0.0, 366.85826138],
       [0.0, 319.09694275, 291.79004651],
       [0.0,0.0,1.0]])
dist = np.array([[-0.25469037,  0.06959525, -0.00146772,  0.00109326, -0.00878955]])


def nothing(x):
    pass


def initializeTrackbars(intialTracbarVals=0):
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Threshold1", "Trackbars", 200, 255, nothing)
    cv2.createTrackbar("Threshold2", "Trackbars", 200, 255, nothing)

initializeTrackbars()
def valTrackbars():
    Threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
    Threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
    src = Threshold1, Threshold2
    return src

def undistort(img):
        h, w = img.shape[:2]
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        x, y, w, h = roi
        dst = dst[y - 30:y + h + 30, x - 40:x + w + 40]
        return dst

def Points(points):
    # print("In Points inside initialise.py")
    # print(self.points)
    x_coord,y_coord,width,height = [],[],[],[]
    for i in points:
        x_coord.append(i[0])
        y_coord.append(i[1])
        width.append(i[2])
        height.append(i[3])
    occurrences_x = list(collections.Counter(x_coord))
    occurrences_y = list(collections.Counter(y_coord))
    occurrences_width = list(collections.Counter(width))
    occurrences_height = list(collections.Counter(height))
    x_1 = (occurrences_x[0] + occurrences_x[0]) / 2
    y_1 = (occurrences_y[0] + occurrences_y[0] + occurrences_y[0] + occurrences_y[0] + occurrences_y[0]) / 5
    x_2 = (occurrences_width[0] + occurrences_width[0] + occurrences_width[0] + occurrences_width[0] +
           occurrences_width[0]) / 5
    y_2 = (occurrences_height[0] + occurrences_height[0] + occurrences_height[0] + occurrences_height[0] +
           occurrences_height[0]) / 5

    x_1, x_2, y_1, y_2 = int(x_1), int(x_2), int(y_1), int(y_2)

    return [x_1,x_2,y_1,y_2]

def after_initialised(self):
    self.video.release()
    height = 720
    width = 540
    blank_image = np.zeros((height, width, 3), np.uint8)

    blank_image[:, 0:width // 2] = (183,250,165)  # (B, G, R)
    blank_image[:, width // 2:width] = (209, 252, 198)

    ret, jpeg = cv2.imencode('.jpg', blank_image)
    return jpeg.tobytes()
def get_frame():
    points = []
    # video = cv2.VideoCapture(0)
    while 1:
        # success, frame = video.read()
        image_result = blackFly.GetNextImage()
        image_converted = image_result.Convert(pyspin.PixelFormat_RGB8)
        im_cv2_format = image_converted.GetData().reshape(height, width, channels)
        # success, frame = self.video.read()
        success = True
        frame = im_cv2_format
        if success == True:
            img = undistort(frame)
            img = cv2.resize(img, (720, 540), interpolation=cv2.INTER_NEAREST)
            thres = valTrackbars()
            imgBlank = np.zeros((720, 540, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
            imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # ADD GAUSSIAN BLUR
            imgThreshold = cv2.Canny(imgBlur, thres[0],thres[1])  # APPLY CANNY BLUR
            kernel = np.ones((3, 3))
            imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)  # APPLY DILATION
            imgThreshold = cv2.erode(imgDial, kernel, iterations=1)  # APPLY EROSION

            ## FIND ALL COUNTOURS
            imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
            imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
            contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
            cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS

            rects = [cv2.boundingRect(cnt) for cnt in contours]
            rects = sorted(rects, key=lambda x: x[1], reverse=True)

            for rect in rects:
                x, y, w, h = rect
                area = w * h
                if area > 90000:
                    img = cv2.rectangle(img, (x - 10, y - 10), (x + w + 10, y + h), (0, 0, 255), 2)
                    data = [x - 10, y - 10, w + 20, h + 10]
                    points.append(data)

            cv2.imshow('frame', img)
            cv2.imshow('frame1', imgContours)
            cv2.imshow('frame2', imgThreshold)
            # cv2.imshow('frame3', img)

            # the 'q' button is set as the
            # quitting button you may use any
            # desired button of your choice
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

if __name__ == "__main__":
    get_frame()