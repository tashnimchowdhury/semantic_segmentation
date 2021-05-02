'''
Masks are generated by my own scritps. Mask of all classes in uint8 format means multi hot encoded. This script tries to segment different types of buildings and roads.
Classes: 1. background 2. building 3. road
'''

from base import BaseDataSet, BaseDataLoader
from utils import palette
from glob import glob
import numpy as np 
import os
import cv2
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

Mask_dict = {'None':0, 'Debris':1, 'Water':2, 'Water_Clean':3, 'Water_Debris':4, 'Water_Flood':5,
            'Building_No_Damage':6, 'Building_Total':7, 'Building_Minor_Damage':8, 'Building_Major_Damage':9,
            'Vehicle':10, 'Road_Undamaged':11, 'Road_Debris':12, 'Road_Flooded':13, 'Tree_Undamaged':14, 
            'Tree_Damaged':15, 'Tree_Clear_Forest':16, 'Tree_Debris_Forest':17, 'Pool_Undamaged':18, 'Pool_Damaged':19, 
            'Sand':20, 'Pool':21}

#ignore_label = 255
ID_TO_TRAINID = {0: 0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:1, 7:1, 8:1, 9:1, 10:0, 11:2, 12:2, 13:2, 14:0, 15:0, 16:0, 17:0, 18:0, 19:0, 20:0, 21:0}
'''
ID_TO_TRAINID = {0: 0, 255:1}
'''

class MichaelDataset(BaseDataSet):
    def __init__(self, mode='fine', **kwarg):
        self.num_classes = 3
        self.palette = palette.Michael_palette_building_road
        self.id_to_trainid = ID_TO_TRAINID
        super(MichaelDataset, self).__init__(**kwarg)

    def _set_files(self):
        SUFIX_IMG = '.jpg'
        SUFIX_LABEL = '.png'
        img_dir_name = 'Michael-generated-masks-1976'
        split = self.split
        img_path = os.path.join(self.root, img_dir_name, self.split, split + '-org-img')
        label_path = os.path.join(self.root, img_dir_name, self.split, split + '-label-img')
        #assert os.listdir(img_path) == os.listdir(label_path)
        #print(img_path)
        #print(label_path)

        img_paths, label_paths = [], []
        img_paths.extend(sorted(glob(os.path.join(img_path, f'*{SUFIX_IMG}'))))
        label_paths.extend(sorted(glob(os.path.join(label_path, f'*{SUFIX_LABEL}'))))
        # @sh: add
        print(len(img_paths))
        print(len(label_paths))
        self.files = list(zip(img_paths,  label_paths))

    def _load_data(self, index):
        img_path, label_path = self.files[index]
        img_id = os.path.splitext(os.path.basename(img_path))[0]
        img = np.asarray(Image.open(img_path).convert('RGB'), dtype=np.float32)
        label = np.asarray(Image.open(label_path), dtype=np.float32)

        for k, v in self.id_to_trainid.items():
            label[ label == k] = v

        return img, label, img_id


class Michael(BaseDataLoader):
    def __init__(self, data_dir, batch_size, split, crop_size=None, base_size=None, scale=True, num_workers=1, mode='fine', val=False,
                    shuffle=False, flip=False, rotate=False, blur= False, augment=False, val_split= None, return_id=False):

        self.MEAN = [0.28689529, 0.32513294, 0.28389176] # how to calculate them for uavdataset??
        self.STD = [0.17613647, 0.18099176, 0.17772235] # how to calculate them for uavdataset??

        kwargs = {
            'root': data_dir,
            'split': split,
            'mean': self.MEAN,
            'std': self.STD,
            'augment': augment,
            'crop_size': crop_size,
            'base_size': base_size,
            'scale': scale,
            'flip': flip,
            'blur': blur,
            'rotate': rotate,
            'return_id': return_id,
            'val': val
        }

        self.dataset = MichaelDataset(mode=mode, **kwargs)
        super(Michael, self).__init__(self.dataset, batch_size, shuffle, num_workers, val_split)
