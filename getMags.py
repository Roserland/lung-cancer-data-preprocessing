# -*- coding: utf-8 -*-


# 是否需要先统计每个文件夹中的wsi的个数？
import openslide
import os
import numpy as np
from collections import Counter
import json
import time

# _subTypeName = "HNSC"
# dataParentPath = '/mnt/data/spark/TCGA/'
# LUAD_WSI_DIR = os.path.join(dataParentPath, _subTypeName)

def get_wsi_mag(wsi_path):
    wsi = openslide.open_slide(wsi_path)
    return wsi.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER]

def generate_Mag_json(wsi_dir, subTypeName = 'LUAD'):
    # print(wsi_dir)
    valid_exts = ['.svs']
    wsi_nameList = os.listdir(wsi_dir)

    aimDir = "/home/fzw/TCGA-CC/annotations/"
    jsonName = os.path.join(aimDir, subTypeName + '-tcga.json')

    mag_dict = {}

    valid_num = 0
    invalid_num = 0
    invalide_path = []
    # 因为含有二级目录
    for wsi_name_1 in wsi_nameList:
        # 一级目录
        cd_dir = os.path.join(wsi_dir, wsi_name_1)
        if not os.path.isdir(cd_dir):
            continue

        for wsi_name in os.listdir(cd_dir):
            # 二级目录
            curr_name = os.path.join(cd_dir, wsi_name)
            if os.path.splitext(curr_name)[-1].lower() not in valid_exts:
                continue
            print(curr_name)

            try:
                mag = get_wsi_mag(curr_name)
                # 使用完全绝对路径名， 对于后续数据导入可能有帮助，代价是文件名过场
                mag_dict[curr_name] = mag
                valid_num += 1
            except KeyError:
                print(curr_name, "doesn't have prorerties: openslide.objective-power, which is correlated with Magnification")
                invalid_num += 1
                invalide_path.append(curr_name)
                continue


    with open(jsonName, 'w') as j:
        json.dump(mag_dict, j)

    txt_name = subTypeName + '-' + "counter.txt"
    txtPath = os.path.join(aimDir, txt_name)
    invalid_txt = "/home/fzw/TCGA-CC/annotations/invalid.txt"

    with open(invalid_txt, "w") as f:
        for i in range(len(invalide_path)):
            f.writelines(invalide_path[i] + '\n')

    with open(txtPath, 'w') as f:
        f.writelines("in directory: \t" + wsi_dir + '\n')
        f.writelines("subtpye name is :\t" + subTypeName + '\n')
        f.writelines("valid:\t" + str(valid_num) + '\n')
        f.writelines("invalid:\t" + str(invalid_num) + '\n')

        f.writelines("*********The invalid wsi path:*********\n")
        for i in range(len(invalide_path)):
            f.writelines(invalide_path[i] + '\n')
        print("done")


# _wsi_dir = r"D:\pythonFiles\Lung-cancer-data-process\7c43c0d1-42e4-4176-89ee-2b98083819b2"
# generate_Mag_json(wsi_dir=LUAD_WSI_DIR)

if __name__ == "__main__":
    subTypeNameList = ['ACC', 'BLCA', 'BRCA', 'CESC', 'CHOL', 'COAD', 'GBM', 'HNSC', 'KICH',
                       'KIRC', 'KIRP', 'LGG', 'LIHC', 'LUAD', 'LUSC', 'OV', 'PAAD', 'PCPG',
                       'PRAD', 'READ', 'SARC', 'SKCM', 'ESCA', 'STAD', 'TGCT', 'THCA', 'THYM',
                       'UCEC', 'UCS', 'UVM']
    dataParentPath = '/mnt/data/spark/TCGA/'
    for i in range(len(subTypeNameList)):
        temp_subTypeName = subTypeNameList[i]
        WSI_DIR = os.path.join(dataParentPath, temp_subTypeName)
        print(WSI_DIR)
        print("##############")
        time.sleep(3)

        generate_Mag_json(wsi_dir=WSI_DIR, subTypeName=temp_subTypeName)
        print("********************************\n\n")
        print("Begin the next subtype")

    # nameList = os.listdir(LUAD_WSI_DIR)
    # 
    # count = {}
    # valid_exts = ['.svs']
    # for name in nameList:
    #     cd_dir = os.path.join(LUAD_WSI_DIR, name)
    #     # print(cd_dir)
    #     # 一级目录
    #     if not os.path.isdir(cd_dir):
    #         continue
    #     #print(cd_dir)
    # 
    #     for name2 in os.listdir(cd_dir):
    #         # 二级目录
    #         curr_name = os.path.join(cd_dir, name2)
    #         #print(curr_name)
    #         if os.path.splitext(curr_name)[-1] != ".svs":
    #             continue
    #         print(curr_name)
    #         if name2 not in count.keys():
    #             count[name] = 1
    #         else:
    #             count[name] += 1
    # 
    # with open('./test.json', 'w') as j:
    #     json.dump(count, j)









