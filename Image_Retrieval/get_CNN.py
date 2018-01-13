#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import h5py

feats = []
info_list = []
cnn_data_files = os.listdir("./cnn_data")
length = len(cnn_data_files)
for i, cnn_data_file in enumerate(cnn_data_files):
    path = os.path.join("./cnn_data", cnn_data_file)
    h5cnn = h5py.File(path, "r")
    dset = h5cnn["data"]
    feats.append(dset[:])
    info_list.append('|'.join(dset.attrs["info"]))
    print "img %s extracted %d out of %d" % (dset.attrs["info"][0], i + 1, length)
    h5cnn.close()

h5f = h5py.File("CNNFeature.h5", 'w')
h5f.create_dataset('data_1', data=feats)
h5f.create_dataset('data_2', data=info_list)
h5f.close()
