#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import numpy as np
import h5py
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input


# h5cnn = h5py.File("CNNFeature.h5", 'r')
# length = len(h5cnn.keys())
# feats = []
# info_list = []
# for i, img_dset_key in enumerate(h5cnn.keys()):
#     dset = h5cnn[img_dset_key]
#     feats.append(dset[:])
#     info_list.append(dset.attrs["info"])
#     print "img %s extracted %d out of %d" % (dset.attrs["info"][0], i+1, length)
# h5cnn.close()


h5f = h5py.File("CNNFeature.h5", 'r')
feats = h5f['data_1'][:]
info_list = h5f['data_2'][:]
h5f.close()


def extract_feature(img_path):

    input_shape = (224, 224, 3)
    model = VGG16(weights='imagenet', input_shape=(input_shape[0], input_shape[1], input_shape[2]), pooling='max',
                  include_top=False)

    img = image.load_img(img_path, target_size=(input_shape[0], input_shape[1]))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    feat = model.predict(img)
    norm_feat = feat[0] / np.linalg.norm(feat[0])
    return norm_feat


def search_img(img_path, topnum):
    queryDir = img_path
    queryVec = extract_feature(queryDir)
    dist_list = np.zeros(len(feats), "float32")
    for i, feature in enumerate(feats):
        dist = np.linalg.norm(queryVec - feature)
        dist_list[i] = dist
    rank_idx = np.argsort(-dist_list)[::-1]
    # scores = np.dot(queryVec, feats.T)
    # rank_idx = np.argsort(scores)[::-1]
    # rank_score = scores[rank_idx]
    result = [info_list[index] for i,index in enumerate(rank_idx[:topnum])]
    return result

