import cv2
import json
import math
import numpy as np
from PIL import Image,ImageFilter
import sys
import os

cloud_image = Image.open('imagedata/5672_mars_12k_topo.jpg')

enlarge = True
antialias = True
smooth = True
scale = True
denoise  = True
dim_scale_factor = 3
if enlarge == True:
    width, height = cloud_image.size
    new_width = width*dim_scale_factor
    concat = int(new_width/float(cloud_image.size[0]))
    size = int((float(cloud_image.size[1])*float(concat)))
    if antialias == False:
        cloud_image = cloud_image.resize((new_width,size))
    if antialias == True:
        cloud_image = cloud_image.resize((new_width,size), Image.BICUBIC)
        

np_cloud_image = np.array(cloud_image, dtype=np.uint8)
if denoise == True:
    print("Denoising")
    np_cloud_image = cv2.fastNlMeansDenoising(np_cloud_image, None, 20, 7, 21) 
np_cloud_image = np.array(np_cloud_image, dtype=np.float32)
if scale == True:
    print("Scaling started");
    for x in range(np_cloud_image.shape[0]):
        for y in range(np_cloud_image.shape[1]):
            np_cloud_image[x][y] = np_cloud_image[x][y]*10
    print("Scaling finished")

border = 3
if smooth == True:
    print("Smoothing started")
    np_cloud_image = cv2.copyMakeBorder(np_cloud_image, border, border, border, border, cv2.BORDER_WRAP)
    for i in range(0,3):
        ksize = (3, 3)
        #np_cloud_image = cv2.bilateralFilter(np_cloud_image,2,200,200)
        #np_cloud_image = cv2.GaussianBlur(np_cloud_image, ksize,3,3)
        np_cloud_image = cv2.blur(np_cloud_image, ksize)
print("Smoothing finished")

print("Dumping data:")

path = "imagedata/5672_mars_12k_topo_up_medium_scalled_smooth_wrap_blur_denoised.txt"
if(os.path.exists(path)):
    print("removing ", path)
    os.remove(path)
file = open(path, "w+")
if(smooth == False):
    file.write(str(np_cloud_image.shape[1]))
    file.write("\n")
    file.write(str(np_cloud_image.shape[0]))
    file.write("\n")
    current_val = 0
    for y in range(np_cloud_image.shape[1]):
        for x in range(np_cloud_image.shape[0]):
            file.write(str(int(np_cloud_image[x][y])))
            if x != np_cloud_image.shape[0] - 1 or y != np_cloud_image.shape[1] - 1:
                file.write("\n")
if(smooth == True):
    file.write(str(np_cloud_image.shape[1]-2*border))
    file.write("\n")
    file.write(str(np_cloud_image.shape[0]-2*border))
    file.write("\n")
    current_val = 0
    for y in range(border,np_cloud_image.shape[1]-border):
        for x in range(border,np_cloud_image.shape[0]-border):
            file.write(str(int(np_cloud_image[x][y])))
            if x != np_cloud_image.shape[0] - (1+border) or y != np_cloud_image.shape[1] - (1+border):
                file.write("\n")                
file.close()