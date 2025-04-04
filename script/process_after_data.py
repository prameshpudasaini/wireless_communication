import os
import numpy as np
import pandas as pd

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/wireless_communication")

# =============================================================================
# process Kierland study area data
# =============================================================================

cols = ['Date-Time', 'EpochByteRx', 'EpochByteTx', 
        'EpochPacketRx', 'EpochPacketTx', 'EpochDropRx', 'EpochDropTx', 'EpochQDropTx',
        'AvgLatency (ms)']
cols_final = ['DateTime', 'Upload', 'Download', 'Latency', 'PacketLoss']

def process_kierland_data(sheet_name, node):
    # read node-specific data and select relevant columns
    kdf = pd.read_excel("ignore/data_after/kierland_intuicom.xlsx", sheet_name = sheet_name, skiprows = 2)
    kdf = kdf[cols]
    
    # convert No Data values to nan
    kdf['AvgLatency (ms)'] = pd.to_numeric(kdf['AvgLatency (ms)'], errors = 'coerce')
    
    # datetime conversion
    kdf['Date-Time'] = pd.to_datetime(kdf['Date-Time'], format = '%Y.%m.%d-%H.%M.%S')
    
    # byte to MB conversion
    kdf['Upload'] = round(kdf['EpochByteTx'] * 8 / 1_000_000, 2) # total bytes transmitted
    kdf['Download'] = round(kdf['EpochByteRx'] * 8 / 1_000_000, 2) # total bytes received
    
    # combined packet loss during Tx and Rx
    kdf['dropped_packets'] = kdf['EpochDropRx'] + kdf['EpochDropTx'] + kdf['EpochQDropTx']
    kdf['total_packets'] = kdf['EpochPacketRx'] + kdf['EpochPacketTx'] + kdf['dropped_packets'] # including dropped packets
    kdf['PacketLoss'] = round(kdf['dropped_packets'] / kdf['total_packets'] * 100, 2)
    
    # rename Latency col
    kdf = kdf.rename(columns = {'AvgLatency (ms)': 'Latency', 'Date-Time': 'DateTime'})
    
    # select relevant columns and save file
    kdf = kdf[cols_final]
    
    # add study area and node info
    kdf['Area'] = 'Kierland'
    kdf['Node'] = node
    
    return kdf

# process data for each node        
df1 = process_kierland_data("Link 1 Bell-Greenway on 64th", "Greenway Rd & 64th St")
df2 = process_kierland_data("Link2-Greenway-Thunderbird-64th", "Thunderbird Rd & 64th St")
df3 = process_kierland_data("Link 3- 64th-70th on Thunerbird", "Thunderbird Rd & 70th St HAWK")

# combine data and save
df = pd.concat([df1, df2, df3], ignore_index = True)
df.to_csv(os.path.join("ignore/data_after", "kierland_intuicom_processed.txt"), sep = '\t', index = False)