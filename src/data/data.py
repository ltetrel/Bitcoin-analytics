import os
import re
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
import src.models as models

# def create_data_object():

#     tempdata = feestotal.set_index('timestamp').join(minedblock.set_index('timestamp'),rsuffix='mb')\
#         .join(transactioncount.set_index('timestamp'),rsuffix='tc').join(volume.set_index('timestamp'),rsuffix='v')\
#         .join(circulatingsupply.set_index('timestamp'),rsuffix='cs').join(RCHodlewave['1m_3m']).join(sendingent['delta'])\
#         .join(percentutxosinprofit).join(FRM).join(asopr).join(mvrvratio).join(liveliness).join(puellmultiple).join(nvtsignal)\
#         .join(relativeunrealizedprofit)


#     tempdata['feepertxn'] = tempdata['value']/tempdata['valuetc']
#     tempdata['feeperblock']= tempdata['value']/tempdata['valuemb']
#     tempdata['volumepertxn'] = tempdata['valuev']/tempdata['valuetc']
#     tempdata['supplypervol'] = tempdata['valuecs']/tempdata['valuev']
#     tempdata=tempdata[tempdata.index>'2015-01-17']


#     data2=tempdata[['feepertxn','volumepertxn','feeperblock','supplypervol','%UTXOinprofit','FRM','mvrv','liveliness','nvtsig','RelativeUprofit','Puell','delta']]\
#     .join(price[['pd','stdev']])

#     data2=data2[data2['stdev']<0.07]

# #    data2.to_csv(r'C:\Users\User\Google Drive\Boule cristale de Bitcoin\Bitcoin serious\Nov11\data.csv', sep=',')
#     return data2

def get_files_list(dir, includes=["*"], excludes=["(?!x)x"]):
    filepaths = []
    for root, _, files in os.walk(dir):
        for file in files:
            filepath = os.path.join(root, file)
            match_include = False
            for incl in includes:
                if re.search(incl, filepath) is not None:
                    match_include = True
                    break
            match_exclude = False
            for excl in excludes:
                if re.search(excl, filepath) is not None:
                    match_exclude = True
                    break
            if match_include & (not match_exclude):
                filepaths += [filepath]
    
    return filepaths

def mat_from_file(filepath):
    vals = []
    time = []
    
    with open(filepath) as f:
        lines = f.readlines()[1:]

    for data in lines:
        # checking for empty strings
        if not data.split(",")[0]:
            curr_time = None
        else:
            curr_time = float(data.split(",")[0])
        if not data.split(",")[1][:-1]:
            curr_val = None
        else:
            curr_val = float(data.split(",")[1][:-1])
        time += [curr_time]
        vals += [curr_val]
        
    return np.array(vals), np.array(time).astype(int)

def check_features(list_files_features):
    list_valid_featurest = []

    for f in list_files_features:
        _, time = mat_from_file(f)
        if len(time) > 1000:
            list_valid_featurest += [f]
        else:
            print("{} is not valid with len {}".format(f, len(time)))

    return list_valid_featurest


def read(dirpath):
    # reading hourly USD price data
    includes = ["price_usd_close_BTC_24h"]
    file_price = get_files_list(dirpath, includes=includes)[0]
    price, timeref = mat_from_file(file_price)
    # reading daily features, excluding glassnode predictions and derivatives of the price
    includes = ["BTC_24h"]
    excludes = ["futures/", "market/", "unrealized_profit", "unrealized_loss", "nupl", "nvts", "puell_multiple", "rcap_account_based", "realized_loss", "realized_profit",
    "reserve_risk", "sopr"]
    list_files_features = get_files_list(dirpath, includes=includes, excludes=excludes)
    # checking data
    list_valid_features = check_features(list_files_features)

    # timestamp from the USD price will serve as reference to check for data integrity
    data_integrity = np.empty((1, len(timeref)), dtype=bool)
    for f in list_valid_features:
        _, time = mat_from_file(f)
        mask = np.in1d(timeref, time, assume_unique=True)
        data_integrity = np.append(data_integrity, mask[np.newaxis, :], axis=0)

    # now we keep the common denominator, it will be our new reference to get the data to be fed in the model
    plt.imshow(1 - data_integrity, cmap="gray")
    plt.axis("tight")
    plt.yticks(np.arange(len(list_valid_features)), list_valid_features, rotation='horizontal')
    plt.xlabel("Num of days after day Zero")
    plt.show()

if __name__ == '__main__':

    # feestotal,minedblock,transactioncount,volume,circulatingsupply,price,RCHodlewave, sendingent,percentutxosinprofit,\
    # FRM,asopr,mvrvratio,liveliness,puellmultiple,nvtsignal,relativeunrealizedprofit = models.Nov11.load_indicator_data()
    dirpath = "data/"
    read(dirpath)