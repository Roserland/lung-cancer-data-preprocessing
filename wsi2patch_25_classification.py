# -*- coding: utf-8 -*-

## 实验前提，假设保证图片条件和Nature文章 "Classification----"基本相同

## 1. 边缘选取：
###   在detection任务中，我们保留了一些边缘图片，对应的patch大小是3000或者6000
###   在classification任务中，参照论文，我们选取的patch大小是512， 因此选择不保留边缘部分

## 2. 背景阈值判定：
###   在detection任务的clip_wsi2patch.py文件中，选取RGB中的G图层灰度最为判定
###   大于210，作为纯白色处理，小于10作为纯黑色处理
###+  判定过程中，将patch转化为灰度图像gray_patch，再根据gray_patch的灰度
###   大于220，判断为背景

# 首先下载三个亚型，各两张svs(连同文件夹)到本地作测试

## 3. Magnification有 40x 和 20x两种形式
## 但是我们需要的是20x， 或者5x

## 4. 如果根据mag大小等比切割patch:
###  + 4.1 在mag=20的wsi中， patch大小 512x512(与原论文相同)
###  + 4.2 在mag=40的wsi中， patch大小 1024x1024， 需要在训练时的预处理部分，重新resize

## 5.出现了有文件没有放大倍数这一属性的的情况
##    可能会作丢弃处理

## 6. 同一个病患ID的svs分割在同一个文件夹下





import openslide
import numpy as np
from PIL import Image
import os
import cv2
import json
from multiprocessing.dummy import Pool as ThreadPool

from Config import *

# configuration parameters
_cfg = Config()

def singleWsi_2_patchs(args):
    """
    Used in level0, with no downsampling process
    :param wsi_path:        path of single wsi slide
    :param mag:             magnification of wsi
    :param patches_dir:     storing path of clipper patchs
    :return:
    """

    (wsi_path, mag, patches_dir) = args
    cfg = _cfg
    print('reading...', wsi_path)
    print("will be stored in: ", patches_dir)

    wsi = openslide.open_slide(wsi_path)
    orig_w = int(wsi.properties.get('openslide.level[0].width'))
    orig_h = int(wsi.properties.get('openslide.level[0].height'))

    # get case id, eg. TCGA-CV-A45Z
    basename = os.path.basename(wsi_path)
    #basename = basename.split('.')[0]
    #case_id = basename[:12]

    if (mag == 20) | (mag == 5):
        patch_size=(cfg.crop_patch_size, cfg.crop_patch_size)
        stride_size=(cfg.crop_stride_size, cfg.crop_stride_size)
        # h_thr=400
        # w_thr=400

    elif(mag == 40):
        patch_size=(cfg.crop_patch_size*2, cfg.crop_patch_size*2)
        stride_size=(cfg.crop_stride_size*2, cfg.crop_stride_size*2)


    else:
        print('mag is not 20x or 40x or 5x')
        raise KeyError

    print('wsi: ', wsi_path)
    print('width: ', orig_w, 'height: ', orig_h)

    # 获取要截取坐标，并剔除不要的坐标, w 是 x 轴， h 是 y 轴
    for h in range(0, orig_h // patch_size[1]):
        for w in range(0, orig_w // patch_size[0]):
            # 因为patch不大，边缘直接滤除，未作保留
            # 直接从RGBA中提取RGB
            patch = np.array(wsi.read_region((w * patch_size[0], h * patch_size[1]), 0, patch_size),
                             dtype=np.uint8)[..., 0:3]

            # 剔除空白过多与黑暗过多的图片
            # 与detection方案中，利用RGB中的G图层的灰度作为判断不同，这里转化成为灰度图像进行判断
            gray = Image.fromarray(patch).convert('L')
            gray = np.array(gray, dtype=np.uint8)
            # gray = patch[:, :, 0] * 0.299 + patch[:, :, 1] * 0.587 + patch[:, :, 2] * 0.114
            # L = R * 0.299 + G * 0.587+ B * 0.114
            whitePixelRatio = (gray > cfg.white_gray).astype(int).sum() / (patch_size[0] * patch_size[1])
            blackPixelRatio = (gray < cfg.black_gray).astype(int).sum() / (patch_size[0] * patch_size[1])

            # omit the invalid patches
            if (whitePixelRatio > cfg.white_ratio_thres or blackPixelRatio > cfg.black_ratio_thres):
                continue

            if cfg.save:
                # 转换颜色空间，符合cv2的颜色方式
                patch = cv2.cvtColor(patch, cv2.COLOR_RGB2BGR)
                save_path = os.path.join(patches_dir,
                                         basename + '_wsi_' + str(w) + '_' + str(h) + '.jpg')
                print('save_path:', save_path)
                cv2.imwrite(save_path, patch)

    wsi.close()

def clip_wsi2patch(json_name, all_patches_dir='/mnt/data/spark/PATCHES-TCGA/', cfg=_cfg):
    """
    clip all whole slide images in wsi_dir, and then stored in the patch_dir,
    per wsi has its own child directory in patch_dir
    :param wsi_dir:
    :param patch_dir:
    :return:
    """
    # 参数设置
    # TODO:
    valid_exts = ['.svs']               # 检查文件名后缀，是否为.svs文件
    valid_dataset_prefix = ['TCGA']     # 检查数据前缀

    print("begin2")


    wsi_mag_dict = json.load(open(json_name))
    """
    format in wsi_mag_dictall_
    single_wsi_absolute_path: magnification
    """
    # traverse wsi_dir
    if not os.path.exists(all_patches_dir):
        os.makedirs(all_patches_dir)

    para_lst = []
    for single_wsi_path_name in wsi_mag_dict.keys():
        basename = os.path.basename(single_wsi_path_name)   # .svs图片基本名， 不包含路径
        basename = basename.split('.')[0]
        if os.path.splitext(basename)[-1].lower() not in valid_exts:
            continue
        # os.path.splitext(wsi_name)[-1].lower()是文件名后缀的小写形式

        if basename[0:4] not in valid_dataset_prefix:
            continue
        # 检查图片对应的case id是否在TCGA中

        # 准备切割单张wsi参数：据对路径，mag大小， 存储文件夹名
        wsi_absolute_path = single_wsi_path_name
        mag = wsi_mag_dict[single_wsi_path_name]
        mag = int(mag)

        case_id = basename[:12]
        stored_patches_dir = os.path.join(all_patches_dir, case_id)
        if not os.path.exists(stored_patches_dir):
            os.makedirs(stored_patches_dir)
        # preparation finished
        para_lst.append((wsi_absolute_path, mag, stored_patches_dir,
                        #cfg
                          ))
        # clip_single_wsi(os.path.join(wsi_dir, wsi_name), mag, patches_dir)

    # multiprocess pool
    pool = ThreadPool(1)

    # pool.starmap or pool.map?
    # python2 has no starmap
    pool.map(singleWsi_2_patchs, para_lst)
    pool.close()
    pool.join()

if __name__ == "__main__":
    print("begin1")
    _json_name = '/home/fzw/TCGA-CC/annotations/ACC-tcga.json'
    _all_patches_dir = _cfg.patches_stored_dir
    clip_wsi2patch(json_name=_json_name, all_patches_dir=_all_patches_dir, cfg=_cfg)
