
import cv2 as cv
import numpy as np
 
 
#粗略的调节对比度和亮度
def contrast_brightness_image(src1, a, g):
    h, w, ch = src1.shape#获取shape的数值，height和width、通道
 
    #新建全零图片数组src2,将height和width，类型设置为原图片的通道类型(色素全为零，输出为全黑图片)
    src2 = np.zeros([h, w, ch], src1.dtype)
    dst = cv.addWeighted(src1, a, src2, 1-a, g)#addWeighted函数说明如下
    cv.imshow("after", dst)
 
src = cv.imread("14_cam-image_array_.jpg")
cv.namedWindow("befoe", cv.WINDOW_NORMAL)
cv.imshow("before", src)
contrast_brightness_image(src, 1.5, 20)#第一个1.5为对比度  第二个为亮度数值越大越亮
cv.waitKey(0)
cv.destroyAllWindows()
