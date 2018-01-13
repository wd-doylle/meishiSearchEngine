#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys
import urllib2
import numpy as np
import os
import h5py
import cv2
import shutil
import PIL
import time
from sklearn.cluster import MiniBatchKMeans
from scipy.cluster.vq import vq
from sklearn import preprocessing
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
import tensorflow

reload(sys)
sys.setdefaultencoding('utf-8')



def extract_feature(img_path):
    # weights: 'imagenet'
    # pooling: 'max' or 'avg'
    # input_shape: (width, height, 3), width and height should >= 48

    input_shape = (224, 224, 3)
    img = image.load_img(img_path, target_size=(input_shape[0], input_shape[1]))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    feat = model.predict(img)
    norm_feat = feat[0] / np.linalg.norm(feat[0])
    return norm_feat


model = VGG16(weights='imagenet', input_shape=(224, 224, 3), pooling='max',
              include_top=False)
sift = cv2.SIFT(nfeatures=300)

img_data_path = "./data/zhms"
files = os.listdir(img_data_path)
img_info_files = []
for file in files:
    img_info_files.append(os.path.join(img_data_path, file))

for i, img_info_file in enumerate(img_info_files):
    # get img info
    try:
        with open(img_info_file, "r") as f:
            img_info = f.read().encode("utf8").split("|")
        url = img_info[1]
    except:
        continue

    # download and process img
    if '.jpg' not in url and '.JPG' not in url and '.jpeg' not in url:
        continue
    if '/' in img_info[0]:
        continue
    req = urllib2.Request(url, None, {'Use37794666r-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'})
    print "Downloading %d img %s" % (i, url)
    try:
        img_data = urllib2.urlopen(req)
        print "Download success"
        time.sleep(1)
    except:
        print "FAIL"
        time.sleep(5)
        continue
    with open("./img/%s.jpg" % img_info[0], "wb") as pic:
        pic.write(img_data.read())
    shutil.move(img_info_file, "./used_data/zhms")
    cv_img = cv2.imread("./img/%s.jpg" % img_info[0])

    # get sift feature
    print "Extracting SIFT feature from %s " % img_info[0]
    kp, des = sift.detectAndCompute(cv_img, None)
    h5sift = h5py.File("./sift_data/%s_%d.h5" % (img_info[0], i), 'w')
    dset1 = h5sift.create_dataset("data", data=des)
    dset1.attrs["info"] = img_info
    h5sift.close()

    # get cnn feature
    print "Extracting CNN feature from %s " % img_info[0]
    cnn_feature = extract_feature("./img/%s.jpg" % img_info[0])
    h5cnn = h5py.File("./cnn_data/%s_%d.h5" % (img_info[0], i), 'w')
    dset2 = h5cnn.create_dataset("data", data=cnn_feature)
    dset2.attrs["info"] = img_info
    h5cnn.close()

