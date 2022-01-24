import cv2
import numpy as np
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

# video = 'test.mp4'
# vid = cv2.VideoCapture(video)
# ret = True
# flag = True
# x_1,x_2,y_1,y_2 = 271,193,9,508
# height = 508
# width = 271
# # print(height,width)
# # print(x_1,x_2,y_1,y_2)
# data_points_x = []
# data_points_y = []

class shot():
    x_1 = 0
    x_2 = 0
    y_1 = 0
    y_2 = 0
    wid = 0
    het = 0
    def __init__(self):
        # self.video_camera = cv2.VideoCapture(0)

        self.data_points = []
        self.data_points_x = []
        self.data_points_y = []


    # def __del__(self):
    #     self.video_camera.release()

    def undistort(self,img):
        h, w = img.shape[:2]
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        x, y, w, h = roi
        dst = dst[y - 30:y + h + 30, x - 40:x + w + 40]
        return dst

    def after_initialised(self):
        # self.video_camera.release()
        height = 540
        width = 720
        blank_image = np.zeros((height, width, 3), np.uint8)

        blank_image[:, 0:width // 2] = (0,0,0)  # (B, G, R)
        blank_image[:, width // 2:width] = (0, 0, 0)

        ret, jpeg = cv2.imencode('.jpg', blank_image)
        return jpeg.tobytes()

    def get_frame(self):
        while True:
            image_result = blackFly.GetNextImage()
            image_converted = image_result.Convert(pyspin.PixelFormat_RGB8)
            im_cv2_format = image_converted.GetData().reshape(height, width, channels)
            # success, frame = self.video.read()
            success = True
            frame = im_cv2_format
            # success, frame = self.video_camera.read()
            if success == True:
                img = self.undistort(frame)
                print("Inside camera_module",img.shape)
                img = cv2.resize(img, (720, 540), interpolation=cv2.INTER_NEAREST)
                imgCrop = img[self.y_1:(self.y_1 + self.y_2), self.x_1: (self.x_1 + self.x_2)]
                print("Insside",self.x_1,self.x_2,self.y_1,self.y_2)
                img = imgCrop
                print("Inside camera_module after cropping", img.shape)
                imgBlank = np.zeros((720, 540, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
                imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # ADD GAUSSIAN BLUR
                imgThreshold = cv2.Canny(imgBlur, 0, 255)  # APPLY CANNY BLUR
                kernel = np.ones((3, 3))
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
                        x = self.wid - x
                        y = self.het - y
                        print("Inside camera",self.wid,self.het)
                        y1 = x * (400 / self.wid)
                        x1 = y * (1200 / self.het)
                        self.data_points_x.append(x1)
                        self.data_points_y.append(y1)
                    ret, jpeg = cv2.imencode('.jpg', imgCrop)


                    result = list(zip(self.data_points_x, self.data_points_y))
                    # print(list(result))
                    for i in range(len(self.data_points_x) - 1):
                        point = {
                            "initial_X": result[i][0],
                            "initial_Y": result[i][1],
                            "final_X": result[i + 1][0],
                            "final_Y": result[i + 1][1]
                        }
                        self.data_points.append(point)
                    return jpeg.tobytes()
# def data_camera():
#     while vid.isOpened():
#         ret, frame = vid.read()
#         if ret == True:
#             # thres = valTrackbars()
#             img = selfundistort(frame)
#             img = cv2.resize(img, (720, 540), interpolation=cv2.INTER_NEAREST)
#             imgCrop = img[y_1:(y_1 + y_2), x_1: (x_1 + x_2)]
#             img = imgCrop
#             imgBlank = np.zeros((720, 540, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
#             imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
#             imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)  # ADD GAUSSIAN BLUR
#             imgThreshold = cv2.Canny(imgBlur,0,255) # APPLY CANNY BLUR
#             kernel = np.ones((3,3))
#             imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)  # APPLY DILATION
#             # imgThreshold = cv2.erode(imgDial, kernel, iterations=1)  # APPLY EROSION
#
#             ## FIND ALL COUNTOURS
#             imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
#             imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
#             contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL,
#                                                    cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
#             cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS
#
#             # sort contours by cnt area / img area ratio from max to min
#             contours = sorted(contours, key=lambda x: cv2.contourArea(x) / imgThreshold.size, reverse=False)
#             for cnt in contours:
#                 area = cv2.contourArea(cnt)
#
#                 # area calculation
#                 (x, y), radius = cv2.minEnclosingCircle(cnt)
#
#
#                 if radius > 2 and radius < 7:
#                     cv2.circle(imgCrop, (int(x), int(y)), int(radius),
#                                (255, 0, 0), 2)
#                     # x1 = (1200 - height)/2 + y
#                     # y1 = (400 - width)/2 + (width - x)
#                     x = width - x
#                     y = height - y
#                     y1 = x * (400/width)
#                     x1 = y * (1200/height)
#                     data_points_x.append(x1)
#                     data_points_y.append(y1)
#
#             # cv2.imshow('Cropped', imgCrop)
#             # cv2.imshow('Blur',imgBlur)
#             # cv2.imshow("contours",imgContours)
#             # cv2.imshow('frame', img)
#             # cv2.imshow('edges',imgThreshold)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 ret = False
#                 break
#         else:
#             break
#     data_points=[]
#     result = list(zip(data_points_x, data_points_y))
#     # print(list(result))
#     for i in range(len(data_points_x)-1):
#         point={
#             "initial_X": result[i][0],
#             "initial_Y": result[i][1],
#             "final_X":result[i+1][0],
#             "final_Y":result[i+1][1]
#         }
#         data_points.append(point)
#
#     # print(data_points)
#     # return data_points_x,data_points_y
#     return data_points

if __name__ == "__main__":
    shot()
