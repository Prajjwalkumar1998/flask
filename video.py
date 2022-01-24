# importing libraries
import cv2
import pyspin
import numpy as np

width, height, channels = 720, 540, 3

system = pyspin.System.GetInstance()
blackFly_list = system.GetCameras()
blackFly = blackFly_list.GetByIndex(0)
blackFly.Init()
blackFly.AcquisitionMode.SetValue(pyspin.AcquisitionMode_Continuous)
blackFly.BeginAcquisition()



ret_flag = True
# Read until video is completed
while ret_flag:

    if ret_flag == True:

        image_result = blackFly.GetNextImage()
        image_converted = image_result.Convert(pyspin.PixelFormat_RGB8)
        im_cv2_format = image_converted.GetData().reshape(height, width, channels)
        # Display the resulting frame
        cv2.imshow('Frame', im_cv2_format)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Break the loop
    else:
        break


# Closes all the frames
cv2.destroyAllWindows()