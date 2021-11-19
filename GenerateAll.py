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
import os

def reshape_image(image, nx,ny):
    image = np.array(image);
    image = image.reshape(ny,nx,3);
    image1 = image[0:ny, 0:int(nx/2)]
    image2 = image[0:ny, int(nx/2):nx]
    image=np.concatenate((image2, image1), axis=1)    
    #image = np.fliplr(image)
    return image;

def rgb(minimum, maximum, value):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2.0 * (value-minimum) / (maximum - minimum)
    r = (max(0.0, 255.0*(1.0 - ratio)))
    b = (max(0.0, 255.0*(ratio - 1.0)))
    g = 255 - b - r
    return r, g, b

def compute_winds_color(val):
    wind_vmax = 140
    r,g,b = rgb(0.0,wind_vmax,val)
    _color = (r/255.0,g/255.0,b/255.0)
    color = ((r), (g),b)
    return color, _color

def wind_dirs(header, UGRD, VGRD):
    image = []
    nx = header['nx']
    ny = header['ny']
    numberPoints = header['numberPoints'];
    maxu = -99999;
    minu = 99999;
    maxv = -99999;
    minv = 99999;    
    for i  in range(numberPoints):
        if(UGRD[i]>maxu):
            maxu = UGRD[i]
        if(UGRD[i] < minu):
            minu = UGRD[i]
            
        if(VGRD[i]>maxv):
            maxv = VGRD[i]
        if(VGRD[i] < minv):
            minv = VGRD[i]

        image.append(127 + int(UGRD[i]))
        image.append(127 + int(VGRD[i]))
        image.append(0)
    
    return reshape_image(image, nx,ny)
def generate_wind_speed_map(header,UGRD,VGRD):
    image = []
    nx = header['nx']
    ny = header['ny']
    numberPoints = header['numberPoints']
    for i  in range(numberPoints):
        val, _val = compute_winds_color(math.sqrt(math.pow(UGRD[i],2)+math.pow(VGRD[i],2)))
        for c in range(len(val)):
            image.append(val[c]);
    return reshape_image(image, nx,ny)

def generate_total_clouds_coverage(headers,datas):
    nx = headers[0]['nx']
    ny = headers[0]['ny']
    clound_factor = 0.5
    images = []
    for i in range(len(headers)):
        image = []
        header = headers[i]
        data = datas[i]
        nx = header['nx']
        ny = header['ny']
        for j in range(header['numberPoints']):
            image.append(clound_factor*data[j])
            image.append(clound_factor*data[j])
            image.append(clound_factor*data[j])
        image = reshape_image(image, nx,ny)
        images.append(image)
    final_image = images[0]
    for i in range(1,len(images)):
        final_image+=images[i]
    #image/=50
    return final_image

def generate_temperature(header, data):
    image = []
    nx = header['nx']
    ny = header['ny']
    numberPoints = header['numberPoints']
    for i  in range(numberPoints):
        val = [-data[i],0,data[i]]
        for c in range(len(val)):
            image.append(val[c]);
    return reshape_image(image, nx,ny)    

Pi = 3.14159
weather_cmd = 'bin\grib2json.cmd'
now = datetime.fromtimestamp(time.time()-3600*6)
h = 0
if now.hour >= 6:
    h=6
if(now.hour>=12):
    h=12
if(now.hour>=18):
    h=18
d = '{}{:02d}{:02d}'.format(now.year, now.month,now.day)
dirname = '{}{:02d}{:02d}{}'.format(now.year, now.month,now.day,h)
weather_vars = ["4LFTX","ABSV","ACPCP","ALBDO","APCP",
                "CAPE","CFRZR","CICEP","CIN","CLWMR",
                "CNWAT","CPOFP","CPRAT","CRAIN","CSNOW","CWAT",
                "CWORK","DLWRF","DPT","DSWRF","DZDT","FLDCP","FRICV",
                "GFLUX","GRLE","GUST","HCDC","HGT","HINDEX","HLCY",
                "HPBL","ICAHT","ICEC","ICEG","ICETK","ICETMP",
                "ICMR","LAND","LCDC","LFTX","LHTFL","MCDC","MSLET",
                "O3MR","PEVPR","PLPL","POT","PRATE","PRES","PRMSL","PWAT",
                "REFC","REFD","RH","RWMR","SFCR","SHTFL","SNMR","SNOD",
                "SOILL","SOILW","SOTYP","SPFH","SUNSD","TCDC","TMAX","TMIN",
                "TMP","TOZNE","TSOIL","UFLX","UGRD","U-GWD","ULWRF",
                "USTM","USWRF","VEG","VFLX","VGRD","V-GWD","VIS","VRATE",
                "VSTM","VVEL","VWSH","WATR","WEASD","WILT"]
selected_vars = ["TMP"]
#for i in range(len(weather_vars)):
datas = []

if not os.path.isdir(dirname):
    os.makedirs(dirname)
if not os.path.isdir(dirname + "/temp"):
    os.makedirs(dirname + "/temp")
cout = 0
data_dict = {}
header_dict = {}
for weather_var in weather_vars:
    if weather_var not in selected_vars:
        continue
    grib_data = dirname+f"/temp/{weather_var}"
    json_data = dirname+f"/temp/{weather_var}.json"
    json_header = dirname+f"/temp/{weather_var}.header.json"
    image_data  = dirname+f"/temp/{weather_var}.jpg"
    print("Processing "+weather_var)
    data = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t{:02d}z.pgrb2.0p25.f000&var_{}=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}%2F{:02d}%2Fatmos'.format(h,weather_var,d,h)
    if not os.path.isfile(json_data):
        urllib.request.urlretrieve(data, grib_data)
        try:    
            os.system('{} -n  -o {} {}'.format(weather_cmd, json_header, grib_data))
            os.system('{} -n  -d -o {} {}'.format(weather_cmd, json_data, grib_data)) 
        except:
            print("grib2json.cmd failed for " + weather_var)
        else:
            print("grib2json.cmd success for " + weather_var)

    with open(json_data)  as json_file:
        json_data = json.load(json_file)
        datas=[]
        headers=[]
        for i in range(len(json_data)):
            datas.append(json_data[i]['data'])
        for i in range(len(json_data)):
            headers.append(json_data[i]['header'])
        #header = json.load(json_file)[0]
        data_dict[weather_var]=datas
        header_dict[weather_var]=headers
        
        #print(len(data))
    #break
        #cv2.imwrite(image_data, image) 
if "UGRD" in header_dict.keys() and "VGRD" in header_dict.keys():
    cv2.imwrite(dirname+'\wind_speeds.jpg', generate_wind_speed_map(header_dict["UGRD"][0],data_dict["UGRD"][0],data_dict["VGRD"][0]))
    cv2.imwrite(dirname+'\wind_directions.jpg', wind_dirs(header_dict["UGRD"][0],data_dict["UGRD"][0],data_dict["VGRD"][0]))
if "TCDC" in header_dict.keys():
    cv2.imwrite(dirname+'\clouds_coverage.jpg', generate_total_clouds_coverage(header_dict["TCDC"],data_dict["TCDC"]))
if "TMP" in header_dict.keys():
    cv2.imwrite(dirname+'\temperature.jpg', generate_temperature(header_dict["TMP"],data_dict["TMP"]))
print("finished")

