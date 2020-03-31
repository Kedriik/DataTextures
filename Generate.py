# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 20:28:33 2019

@author: Kedrowsky
"""
import numpy as np
import cv2
import json
import math
from PIL import Image
import os 
import urllib.request
from datetime import datetime
import time
Pi = 3.14159
weather_cmd = 'bin\grib2json.cmd'
wind_input_data = 'gribdata\windsigma995.anl'
wind_output_data = 'jsondata\windsigma995.json'
wind_texture = 'imagedata\speedwindsigma995.jpg'
wind_dirs_texture = 'imagedata\dirswindsigma995.jpg'

clouds_input_data = 'gribdata\clouds'
clouds_output_data = 'jsondata\clouds.json'
clouds_texture = 'imagedata\clouds.jpg'

weather_input_data = 'gribdata\weather'
weather_output_data = 'jsondata\weather'
now = datetime.fromtimestamp(time.time()-3600*6)
h = 0
if now.hour >= 6:
    h=6
if(now.hour>=12):
    h=12
if(now.hour>=18):
    h=18
d = '{}{:02d}{:02d}'.format(now.year, now.month,now.day,h)

#windurl = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t{:02d}z.pgrb2.0p25.anl&lev_0.995_sigma_level=on&var_UGRD=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}'.format(h,d)
#url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t{:02d}z.pgrb2.0p25.f000&var_TCDC=on&var_UGRD=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}%2F{:02d}'.format(h,d,h)
url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t{:02d}z.pgrb2.0p25.anl&lev_0.995_sigma_level=on&var_UGRD=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}%2F{:02d}'.format(h,d,h)
urllib.request.urlretrieve(url, weather_input_data)
os.system('{} -n -d -o {} {}'.format(weather_cmd, weather_output_data,weather_input_data))
os.system('{} -n -o {} {}'.format(weather_cmd, 'current_headers.txt',weather_input_data))

##TCPC is not in package with winds...
tcpcurl = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t{:02d}z.pgrb2.0p25.f000&var_TCDC=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}%2F{:02d}'.format(h,d,h)
urllib.request.urlretrieve(tcpcurl, 'gribdata\clouds')
os.system('{} -n -d -o {} {}'.format(weather_cmd, clouds_output_data,'gribdata\clouds'))

wind_vmax = 30
def rgb(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2.0 * (value-minimum) / (maximum - minimum)
    r = (max(0.0, 255.0*(1.0 - ratio)))
    b = (max(0.0, 255.0*(ratio - 1.0)))
    g = 255 - b - r
    return r, g, b


def compute_color1(val):
    r,g,b = rgb(0.0,wind_vmax,val)
    _color = (r/255.0,g/255.0,b/255.0)
    color = ((r), (g),b)
    return color, _color

def generate_windspeedmap(u,v,data):
    image = []
    nx = (data[u]['header']['nx'])
    ny = (data[u]['header']['ny'])
    numberPoints = (data[0]['header']['numberPoints']);
    for i  in range(numberPoints):
        val, _val = compute_color1(math.sqrt(math.pow(data[u]['data'][i],2)+math.pow(data[v]['data'][i],2)))
        for c in range(len(val)):
            image.append(val[c]);
    
    image = np.array(image);
    image = image.reshape(ny,nx,3);
    image1 = image[0:ny, 0:int(nx/2)]
    image2 = image[0:ny, int(nx/2):nx]
    image=np.concatenate((image2, image1), axis=1)
    return image

def generate_total_clouds_coverage(n,data):
    image = []
    nx = (data[0]['header']['nx'])
    ny = (data[0]['header']['ny'])

    for i in range(len(data)):
        for j in range(data[0]['header']['numberPoints']):
            if(i==n):
                image.append(255*data[i]['data'][j])
                image.append(255*data[i]['data'][j])
                image.append(255*data[i]['data'][j])
                
    image = np.array(image);
    image = image.reshape(ny,nx,3);
    image1 = image[0:ny, 0:int(nx/2)]
    image2 = image[0:ny, int(nx/2):nx]
    image=np.concatenate((image2, image1), axis=1)    
    image = np.fliplr(image)
    return image;

def wind_dirs(u,v,data):
    image = []
    nx = (data[u]['header']['nx'])
    ny = (data[u]['header']['ny'])
    numberPoints = (data[0]['header']['numberPoints']);
    maxu = -99999;
    minu = 99999;
    maxv = -99999;
    minv = 99999;    
    for i  in range(numberPoints):
        if(data[u]['data'][i]>maxu):
            maxu = data[u]['data'][i]
        if(data[u]['data'][i] < minu):
            minu = data[u]['data'][i]
            
        if(data[u]['data'][i]>maxv):
            maxv = data[v]['data'][i]
        if(data[u]['data'][i] < minv):
            minv = data[v]['data'][i]

        image.append(127 + int(data[u]['data'][i]))
        image.append(127 + int(data[v]['data'][i]))
        image.append(0)
    
    image = np.array(image);
    image = image.reshape(ny,nx,3);
    image1 = image[0:ny, 0:int(nx/2)]
    image2 = image[0:ny, int(nx/2):nx]
    image=np.concatenate((image2, image1), axis=1)
    print('maxu:',maxu, 'minu:',minu)
    print('maxv:',maxv, 'minv:',minv);
    return image

with open(weather_output_data) as json_file:
    data = json.load(json_file)
    for i in range(len(data)):
        if (data[i]['header']['parameterNumberName'] == 'U-component_of_wind' and
            data[i]['header']['surface1Value'] == 0.995):
            u=i
        if (data[i]['header']['parameterNumberName'] == 'V-component_of_wind' and
            data[i]['header']['surface1Value'] == 0.995):
            v=i
    image = generate_windspeedmap(u,v,data)
    cv2.imwrite(wind_texture, image)       
    image = wind_dirs(u,v,data)
    cv2.imwrite(wind_dirs_texture,image)
    
with open(clouds_output_data) as json_file:
    data = json.load(json_file)
    for i in range(len(data)):
        if(i==0):
            image = generate_total_clouds_coverage(i,data)
        else:
            image += generate_total_clouds_coverage(i,data);
    image /= (len(data)*50)
    cv2.imwrite('imagedata\clouds.jpg', image)    