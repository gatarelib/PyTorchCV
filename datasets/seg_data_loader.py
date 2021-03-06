#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Donny You(youansheng@gmail.com)
# Class for the Semantic Segmentation Data Loader.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import torch
from torch.utils import data

from datasets.seg.fs_data_loader import FSDataLoader
from datasets.seg.mr_data_loader import MRDataLoader
import datasets.tools.pil_aug_transforms as pil_aug_trans
import datasets.tools.cv2_aug_transforms as cv2_aug_trans
import datasets.tools.transforms as trans
from datasets.tools.collate_functions import CollateFunctions
from utils.tools.logger import Logger as Log


class SegDataLoader(object):

    def __init__(self, configer):
        self.configer = configer

        if self.configer.get('data', 'image_tool') == 'pil':
            self.aug_train_transform = pil_aug_trans.PILAugCompose(self.configer, split='train')
        elif self.configer.get('data', 'image_tool') == 'cv2':
            self.aug_train_transform = cv2_aug_trans.CV2AugCompose(self.configer, split='train')
        else:
            Log.error('Not support {} image tool.'.format(self.configer.get('data', 'image_tool')))
            exit(1)

        if self.configer.get('data', 'image_tool') == 'pil':
            self.aug_val_transform = pil_aug_trans.PILAugCompose(self.configer, split='val')
        elif self.configer.get('data', 'image_tool') == 'cv2':
            self.aug_val_transform = cv2_aug_trans.CV2AugCompose(self.configer, split='val')
        else:
            Log.error('Not support {} image tool.'.format(self.configer.get('data', 'image_tool')))
            exit(1)

        self.img_transform = trans.Compose([
            trans.ToTensor(),
            trans.Normalize(div_value=self.configer.get('normalize', 'div_value'),
                            mean=self.configer.get('normalize', 'mean'),
                            std=self.configer.get('normalize', 'std')), ])

        self.label_transform = trans.Compose([
            trans.ToLabel(),
            trans.ReLabel(255, self.configer.get('data', 'num_classes')), ])

    def get_trainloader(self):
        if self.configer.get('method') == 'fcn_segmentor':
            trainloader = data.DataLoader(
                FSDataLoader(root_dir=os.path.join(self.configer.get('data', 'data_dir'), 'train'),
                             aug_transform=self.aug_train_transform,
                             img_transform=self.img_transform,
                             label_transform=self.label_transform,
                             configer=self.configer),
                batch_size=self.configer.get('train', 'batch_size'), shuffle=True, drop_last=True,
                collate_fn=lambda *args: CollateFunctions.our_collate(
                    *args, data_keys=['img', 'labelmap'],
                    configer=self.configer,
                    trans_dict=self.configer.get('train', 'data_transformer')
                )
            )

            return trainloader

        elif self.configer.get('method') == 'mask_rcnn':
            trainloader = data.DataLoader(
                MRDataLoader(root_dir=os.path.join(self.configer.get('data', 'data_dir'), 'train'),
                             aug_transform=self.aug_train_transform,
                             img_transform=self.img_transform,
                             configer=self.configer),
                batch_size=self.configer.get('train', 'batch_size'), shuffle=True,
                collate_fn=lambda *args: CollateFunctions.our_collate(
                    *args, data_keys=['img', 'bboxes', 'labels', 'polygons'],
                    configer=self.configer,
                    trans_dict=self.configer.get('train', 'data_transformer')
                )
            )

            return trainloader

        else:
            Log.error('Method: {} loader is invalid.'.format(self.configer.get('method')))
            return None

    def get_valloader(self):
        if self.configer.get('method') == 'fcn_segmentor':
            valloader = data.DataLoader(
                FSDataLoader(root_dir=os.path.join(self.configer.get('data', 'data_dir'), 'val'),
                             aug_transform=self.aug_val_transform,
                             img_transform=self.img_transform,
                             label_transform=self.label_transform,
                             configer=self.configer),
                batch_size=self.configer.get('val', 'batch_size'), shuffle=True, drop_last=True,
                collate_fn=lambda *args: CollateFunctions.our_collate(
                    *args, data_keys=['img', 'labelmap'],
                    configer=self.configer,
                    trans_dict=self.configer.get('val', 'data_transformer')
                )
            )

            return valloader

        elif self.configer.get('method') == 'mask_rcnn':
            valloader = data.DataLoader(
                MRDataLoader(root_dir=os.path.join(self.configer.get('data', 'data_dir'), 'val'),
                             aug_transform=self.aug_val_transform,
                             img_transform=self.img_transform,
                             configer=self.configer),
                batch_size=self.configer.get('val', 'batch_size'), shuffle=True,
                collate_fn=lambda *args: CollateFunctions.our_collate(
                    *args, data_keys=['img', 'bboxes', 'labels', 'polygons'],
                    configer=self.configer,
                    trans_dict=self.configer.get('val', 'data_transformer')
                )
            )

            return valloader

        else:
            Log.error('Method: {} loader is invalid.'.format(self.configer.get('method')))
            return None

    @staticmethod
    def _seg_collate(batch):
        """Custom collate fn for dealing with batches of images that have a different
        number of associated object annotations (bounding boxes).
        Arguments:
            batch: (tuple) A tuple of tensor images and lists of annotations
        Return:
            A tuple containing:
                1) (tensor) batch of images stacked on their 0 dim
                2) (list of tensors) annotations for a given image are stacked on 0 dim
        """
        transposed = [list(sample) for sample in zip(*batch)]
        return transposed

if __name__ == "__main__":
    # Test data loader.
    pass
