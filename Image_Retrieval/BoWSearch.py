#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import cv2
import numpy as np
import os
from sklearn.cluster import MiniBatchKMeans
from sklearn import preprocessing
from scipy.cluster.vq import vq
import h5py

# with open("BoWFeature.pkl", "rb") as input:
#     feature_code = pickle.load(input)
#     cluster_points = pickle.load(input)
#     img_names = pickle.load(input)
h5f = h5py.File("BoWFeature.h5",'r')
feature_code = h5f['data_1'][:]
cluster_points = h5f['data_2'][:]
info_list = h5f['data_3'][:]
h5f.close()

numClusterPoints = 1000


def histo(descriptors):
    feature = np.zeros(numClusterPoints, "float32")
    cluster_idx, distance = vq(descriptors, cluster_points)
    for idx in cluster_idx:
        feature[idx] += 1
    feature /= np.linalg.norm(feature)
    return feature


def search_img(img_path, topnum):
    sift = cv2.SIFT(nfeatures=150)
    img = cv2.imread(img_path)
    kp, des = sift.detectAndCompute(img, None)
    ori_feature = histo(des)
    dist_list = np.zeros(len(feature_code), "float32")
    for i, feature in enumerate(feature_code):
        dist = np.linalg.norm(feature - ori_feature)
        dist_list[i] = dist
    rank_idx = np.argsort(dist_list)
    # sim_list = np.dot(ori_feature, feature_code.T)
    # rank_idx = np.argsort(-sim_list)
    result = []
    for idx in rank_idx[:topnum]:
        result.append(info_list[idx])
    return result
