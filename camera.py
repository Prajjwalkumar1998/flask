import cv2
import numpy as np
# import imageio
# from skimage import img_as_ubyte
# import imutils
import time
# import initialise

count=0
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


def undistort(img):
    h,w = img.shape[:2]
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
    x,y,w,h = roi
    dst = dst[y-30:y+h+30, x-40:x+w+40]
    return dst

video = 'test.mp4'
vid = cv2.VideoCapture(video)
ret = True
flag = True
x_1,x_2,y_1,y_2 = 271,193,9,508
height = 508
width = 271
# print(height,width)
# print(x_1,x_2,y_1,y_2)
data_points_x = []
data_points_y = []
def data_camera():
    while vid.isOpened():
        ret, frame = vid.read()
        if ret == True:
            # thres = valTrackbars()
            img = undistort(frame)
            img = cv2.resize(img, (720, 540), interpolation=cv2.INTER_NEAREST)
            imgCrop = img[y_1:(y_1 + y_2), x_1: (x_1 + x_2)]
            img = imgCrop
            imgBlank = np.zeros((720, 540, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
            imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)  # ADD GAUSSIAN BLUR
            imgThreshold = cv2.Canny(imgBlur,0,255) # APPLY CANNY BLUR
            kernel = np.ones((3,3))
            imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)  # APPLY DILATION
            # imgThreshold = cv2.erode(imgDial, kernel, iterations=1)  # APPLY EROSION

            ## FIND ALL COUNTOURS
            imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
            imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
            contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
            cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS

            # sort contours by cnt area / img area ratio from max to min
            contours = sorted(contours, key=lambda x: cv2.contourArea(x) / imgThreshold.size, reverse=False)
            for cnt in contours:
                area = cv2.contourArea(cnt)

                # area calculation
                (x, y), radius = cv2.minEnclosingCircle(cnt)


                if radius > 2 and radius < 7:
                    cv2.circle(imgCrop, (int(x), int(y)), int(radius),
                               (255, 0, 0), 2)
                    # x1 = (1200 - height)/2 + y
                    # y1 = (400 - width)/2 + (width - x)
                    x = width - x
                    y = height - y
                    y1 = x * (400/width)
                    x1 = y * (1200/height)
                    data_points_x.append(x1)
                    data_points_y.append(y1)

            # cv2.imshow('Cropped', imgCrop)
            # cv2.imshow('Blur',imgBlur)
            # cv2.imshow("contours",imgContours)
            # cv2.imshow('frame', img)
            # cv2.imshow('edges',imgThreshold)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                ret = False
                break
        else:
            break
    data_points=[]
    result = list(zip(data_points_x, data_points_y))
    # print(list(result))
    for i in range(len(data_points_x)-1):
        point={
            "initial_X": result[i][0],
            "initial_Y": result[i][1],
            "final_X":result[i+1][0],
            "final_Y":result[i+1][1]
        }
        data_points.append(point)

    # print(data_points)
    # return data_points_x,data_points_y
    return data_points

if __name__ == "__main__":
    data_camera()
