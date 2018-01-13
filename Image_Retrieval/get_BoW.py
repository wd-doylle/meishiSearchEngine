#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys
import cv2
import numpy as np
import os
from sklearn.cluster import MiniBatchKMeans
from scipy.cluster.vq import vq
from sklearn import preprocessing
import h5py
import gc

reload(sys)
sys.setdefaultencoding('utf-8')


des_list = []
info_list = []
sift_data_files = os.listdir("./sift_data")
length = len(sift_data_files)
for i, sift_data_file in enumerate(sift_data_files[:20000]):
    path = os.path.join("./sift_data", sift_data_file)
    h5sift = h5py.File(path, "r")
    try:
        dset = h5sift["data"]
        des_list.append(dset[:])
        info_list.append("|".join(dset.attrs["info"]))
        print "img %s extracted %d out of %d" % (dset.attrs["info"][0], i + 1, length)
        h5sift.close()
    except:
        h5sift.close()
        continue

length = len(info_list)

h5f = h5py.File("BoWFeature.h5", 'w')
h5f.create_dataset('data_3', data=info_list)
h5f.close()
del info_list

descriptors = list(des_list[0])
for i, descriptor in enumerate(des_list[1:]):
    print i
    # descriptors = np.vstack((descriptors, descriptor))
    for ele in descriptor:
        descriptors.append(ele)
gc.collect()
numClusterPoints = 1000
print "Start k-means: %d cluster points, %d key points" % (numClusterPoints, len(descriptors))
np.random.seed(5)
clf = MiniBatchKMeans(n_clusters=numClusterPoints)
clf.fit(descriptors)
cluster_points = clf.cluster_centers_

feature_code = np.zeros((length, numClusterPoints), "float32")
for i in xrange(length):
    cluster_idx, distance = vq(des_list[i], cluster_points)
    for idx in cluster_idx:
        feature_code[i][idx] += 1

for ele in feature_code:
    ele /= np.linalg.norm(ele)

h5f = h5py.File("BoWFeature.h5", 'a')
h5f.create_dataset('data_1', data=feature_code)
h5f.create_dataset('data_2', data=cluster_points)
h5f.close()
