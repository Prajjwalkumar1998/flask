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



class shot():
    x_1 = 0
    x_2 = 0
    y_1 = 0
    y_2 = 0
    wid = 0
    het = 0
    def __init__(self):
        # self.video_camera = cv2.VideoCapture("1.mp4")

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

    def Points(self):
        # print("In Points inside initialise.py")
        # print(self.points)
        res = []
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
        # [res.append(x) for x in self.data_points if x not in res]
        points = self.data_points

        return points

    def after_initialised(self):
        # self.video_camera.release()
        height = 540
        width = 720
        blank_image = np.zeros((height, width, 3), np.uint8)

        blank_image[:, 0:width // 2] = (0,0,0)  # (B, G, R)
        blank_image[:, width // 2:width] = (0, 0, 0)

        ret, jpeg = cv2.imencode('.jpg', blank_image)
        return jpeg.tobytes()

    # def get_frame(self):
    #     while self.video_camera.isOpened():
    #         # image_result = blackFly.GetNextImage()
    #         # image_converted = image_result.Convert(pyspin.PixelFormat_RGB8)
    #         # im_cv2_format = image_converted.GetData().reshape(height, width, channels)
    #         # success, frame = self.video.read()
    #         success, frame = self.video_camera.read()
    #         # success = True
    #         # frame = im_cv2_format
    #
    #         if success == True:
    #             img = self.undistort(frame)
    #             print("Inside camera_module",img.shape)
    #             img = cv2.resize(img, (720, 540), interpolation=cv2.INTER_NEAREST)
    #             imgCrop = img[self.y_1:(self.y_1 + self.y_2), self.x_1: (self.x_1 + self.x_2)]
    #             print("Insside",self.x_1,self.x_2,self.y_1,self.y_2)
    #             frame=img.copy()
    #             cv2.rectangle(frame, (self.x_1, self.y_1), (self.x_1 + self.x_2, self.y_1 + self.y_2), (0.255, 0), 12)
    #             img = imgCrop
    #             print("Inside camera_module after cropping", img.shape)
    #             imgBlank = np.zeros((720, 540, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
    #             imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
    #             imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # ADD GAUSSIAN BLUR
    #             imgThreshold = cv2.Canny(imgBlur, 0, 255)  # APPLY CANNY BLUR
    #             kernel = np.ones((3, 3))
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
    #                 if radius > 0 and radius < 7:
    #                     cv2.circle(imgCrop, (int(x), int(y)), int(radius),
    #                                (255, 0, 0), 2)
    #                     cv2.circle(frame, (int(x + self.x_1), int(y + self.y_1)), int(radius), (255, 0, 0), 2)
    #                     # x1 = (1200 - height)/2 + y
    #                     # y1 = (400 - width)/2 + (width - x)
    #                     x = self.wid - x
    #                     # y = self.het - y
    #                     print("Inside camera",self.wid,self.het)
    #                     y1_ = x * (400 / self.het)
    #                     x1_ = y * (1200 / self.wid)
    #                     self.data_points_x.append(x1_)
    #                     self.data_points_y.append(y1_)
    #             ret, jpeg = cv2.imencode('.jpg', frame)
    #
    #
    #
    #             return jpeg.tobytes()

    def get_frame(self):

        while True:
            image_result = blackFly.GetNextImage()
            image_converted = image_result.Convert(pyspin.PixelFormat_RGB8)
            im_cv2_format = image_converted.GetData().reshape(height, width, channels)
            # success, frame = self.video.read()
            # success, frame = self.video_camera.read()
            success = True
            frame = im_cv2_format
            if success == True:
                # print("####################################################################################################")
                # print(self.i)
                img = self.undistort(frame)

                img = cv2.resize(img, (720, 540), interpolation=cv2.INTER_NEAREST)

                imgCrop = img[self.y_1:(self.y_1 + self.y_2), self.x_1: (self.x_1 + self.x_2)]

                framet = img.copy()
                cv2.rectangle(framet, (self.x_1,self.y_1), (self.x_1 + self.x_2,self.y_1 + self.y_2), (0.255,0), 10)
                img = imgCrop

                imgBlank = np.zeros((720, 540, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
                imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # ADD GAUSSIAN BLUR
                imgThreshold = cv2.Canny(imgBlur, 0, 255)  # APPLY CANNY BLUR
                kernel = np.ones((3, 3))
                imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)  # APPLY DILATION
                # imgThreshold = cv2.erode(imgDial, kernel, iterations=1)  # APPLY EROSION
                # time.sleep(0.2)
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

                    if radius > 0 and radius < 7:
                        cv2.circle(imgCrop, (int(x), int(y)), int(radius),
                                   (255, 0, 0), 2)
                        cv2.circle(framet, (int(x + self.x_1), int(y + self.y_1)), int(radius),
                                   (255, 0, 0), 2)
                        # x1 = (1200 - height)/2 + y
                        # y1 = (400 - width)/2 + (width - x)

                        # print(self.wid,self.het, "Width and height")
                        x = self.wid - x
                        # y = self.het - y

                        y1_ = x * (400 / self.wid)
                        x1_ = y * (1200 / self.het)
                        # print(x1_,y1_,"convert")
                        self.data_points_x.append(x1_)
                        self.data_points_y.append(y1_)
                # print("For loop ended")
                ret, jpeg = cv2.imencode('.jpg', framet)
                # print("Printing result")
                # result = list(zip(self.data_points_x, self.data_points_y))
                # print("Result",result)
                # print("Length of result",len(result))
                # print("####################################################################################################")
                # # result.sort()
                # for i in range(len(self.data_points_x) - 1):
                #     point = {
                #         "initial_X": result[i][0],
                #         "initial_Y": result[i][1],
                #         "final_X": result[i + 1][0],
                #         "final_Y": result[i + 1][1]
                #     }
                #     self.data_points.append(point)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                # self.i = self.i + 1
                return jpeg.tobytes()
class initialise():
    def __init__(self):
        # self.video = cv2.VideoCapture("1.mp4")
        self.points = []
        self.x_coord = []
        self.y_coord = []
        self.width = []
        self.height = []
        self.start_time = time.time()
        self.seconds = 10
    #
    # def __del__(self):
    #     # self.video.release()

    def undistort(self,img):
        h, w = img.shape[:2]
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        x, y, w, h = roi
        dst = dst[y - 30:y + h + 30, x - 40:x + w + 40]
        return dst

    def Points(self):
        for i in self.points:
            self.x_coord.append(i[0])
            self.y_coord.append(i[1])
            self.width.append(i[2])
            self.height.append(i[3])
        occurrences_x = list(collections.Counter(self.x_coord))
        occurrences_y = list(collections.Counter(self.y_coord))
        occurrences_width = list(collections.Counter(self.width))
        occurrences_height = list(collections.Counter(self.height))
        x_1 = (occurrences_x[0] + occurrences_x[0]) / 2
        y_1 = (occurrences_y[0] + occurrences_y[1] + occurrences_y[2] + occurrences_y[3] + occurrences_y[4]) / 5
        x_2 = (occurrences_width[0] + occurrences_width[1] + occurrences_width[2] + occurrences_width[3] +
               occurrences_width[4]) / 5
        y_2 = (occurrences_height[0] + occurrences_height[1] + occurrences_height[2] + occurrences_height[3] +
               occurrences_height[4]) / 5

        x_1, x_2, y_1, y_2 = int(x_1), int(x_2), int(y_1), int(y_2)

        return [x_1, x_2, y_1, y_2]

    def after_initialised(self):
        # self.video.release()
        height = 540
        width = 720
        blank_image = np.zeros((height, width, 3), np.uint8)

        blank_image[:, 0:width // 2] = (0,0,0)  # (B, G, R)
        blank_image[:, width // 2:width] = (0,0,0)

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
            if success == True:
                img = self.undistort(frame)
                img = cv2.resize(img, (720, 540), interpolation=cv2.INTER_NEAREST)
                imgBlank = np.zeros((720, 540, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
                imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # ADD GAUSSIAN BLUR
                imgThreshold = cv2.Canny(imgBlur, 0, 207)  # APPLY CANNY BLUR
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
                        img = cv2.rectangle(img, (x, y - 10), (x + w + 20, y + h + 20), (0, 0, 255), 2)
                        data = [x, y - 20, w + 10, h + 20]
                        self.points.append(data)

                ret, jpeg = cv2.imencode('.jpg', img)
                return jpeg.tobytes()

if __name__ == "__main__":
    initialise()