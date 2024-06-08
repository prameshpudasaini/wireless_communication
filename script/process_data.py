import os
import numpy as np
import pandas as pd

os.chdir(r"D:\GitHub\wireless_communication")

# list of folder paths with radio performance data
folders = ["ignore/radio_data_20231226_20240125", 
           "ignore/radio_data_20240403_20240503"]

# list of column names
cols = ['Time', 'Upstream (Mbps)', 'Downstream (Mbps)', 'Latency (ms)',
       'Packet Loss', '2.4 GHz Noise', '5.8 GHz Noise', '2.4 GHz Airtime - TX',
       '2.4 GHz Airtime - RX', '2.4 GHz Airtime - Total',
       '5.8 GHz Airtime - TX', '5.8 GHz Airtime - RX',
       '5.8 GHz Airtime - Total', 'PSP', 'RPSP', 'Tx Rate (Kbps)',
       'RxRate (Kbps)', '5.8 GHz Tx Rate (Kbps)', '5.8 GHz Rx Rate (Kbps)',
       '# 2.4 GHz Routed Clients', '# 5.8 GHz Routed Clients', '# Neighbors',
       'Hop Count', '2.4 GHz Channel', '5.8 GHz Channel',
       'Next Hop Upstream Router']

list_df = [] # initialize empty list to store raw data from each node

# loop through each folder
for folder in folders:
    print(f"\nFolder: {folder}")
    files = os.listdir(folder) # list of files in folder
    
    # loop through each file in folder
    for file in files:
        print(f"File: {file}")
        file_path = os.path.join(folder, file)
        
        # check whether the file ends in .csv or .xlsx
        # these extensions have different formatting styles for the header
        if file.endswith('.csv'):
            data = pd.read_csv(file_path, header = None, names = cols, skiprows = 1)
            node = file[:-4]
        elif file.endswith('.xlsx'):
            data = pd.read_excel(file_path, sheet_name = 'Sheet1', header = None, names = cols, skiprows = 2)
            node = file[:-5]
            
        # format column names: remove parentheses and # sign
        data.columns = [col.replace('(', '').replace(')', '').replace('#', '').replace('-', '') for col in data.columns]
        
        # strip whitespace at start/end of column names
        data.columns = data.columns.str.strip()
        
        # strip whitespace from column names and add underscore
        data.columns = [col.replace('  ', ' ').replace(' ', '_') for col in data.columns]
        
        # add node/intersection name as variable and append data to list
        data['Node'] = node
        list_df.append(data)

df = pd.concat(list_df, ignore_index = True)

# filter out data from December 2023 (due to holidays)
df = df[~df.Time.str.contains('Dec')]

# convert time to datetime
df.Time = '2024 ' + df.Time.str[:9]
df.Time = pd.to_datetime(df.Time, format = '%Y %b %d %H')

# add study area
df['Area'] = np.select([df.Node.str.contains('Greenway|Thunderbird'), 
                        df.Node.str.contains('Indian School|Osborn|Thomas'), 
                        df.Node.str.contains('Van Buren|Buckeye')], 
                       ['Kierland', 'Thomas West of I-17', 'Southwest'])

# save file
output_path = "ignore/radio_data_processed.txt"
df.to_csv(output_path, index = False, sep = '\t')