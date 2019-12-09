import os
import pandas as pd
from collections import Counter

metadata = "./modelMeta_all_20191209.txt"

df = pd.read_table(metadata)

patiens = list(df['patient'])
cancer_types  = list(df['cancer'])

subTypeDict = Counter(cancer_types)
print(subTypeDict)

subTypeNames = list(subTypeDict.keys())
print(subTypeNames)



# print(df.head(5))