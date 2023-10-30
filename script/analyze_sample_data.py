import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'
from plotly.subplots import make_subplots
import plotly.graph_objects as go

os.chdir(r"D:\GitHub\wireless_radios")
base_dir = "ignore/radio_data_sample"

def processData(file_path, file_name):
    # read excel sheet with multi-line header
    df = pd.read_excel(file_path, sheet_name = 'Sheet1', header = [0, 1])
    
    # modify multi-header to single header for column names
    df.columns = ['_'.join(col) if not pd.isnull(col[1]) else col[0] for col in df.columns]
    df.columns = df.columns.str.replace(r'_Unnamed.*', '', regex = True) # replace all characters after Unnamed
    df.columns = df.columns.str.replace('# ', '') # remove # sign
    df.columns = df.columns.str.replace(r'[()]', '', regex = True) # remove parantheses
    df.columns = df.columns.str.strip().str.replace(' ', '_') # strip whitespace and add underscore
    
    # split time into month, date and hour
    df[['month', 'date', 'hour']] = df['Time'].str.extract(r'(\w+) (\d+) (\d+:\d+)')
    
    # datetime conversion
    df['month'] = pd.to_datetime(df['month'], format = '%b').dt.month
    df['date'] = df['date'].astype(int)
    df['hour'] = pd.to_datetime(df['hour'], format = '%H:%M').dt.hour
    
    # create timestamp object
    df['Time'] = pd.to_datetime('2023-' + df['month'].astype(str) + '-' + df['date'].astype(str)  + ' ' + df['hour'].astype(str) + ':00:00')
    
    # filter data for September and select columns
    cols = ['Up_Mbps', 'Down_Mbps', 'Latency_ms', 'Packet_Loss', '2.4_GHz_Noise', '5.8_GHz_Noise', 'date']
    df = df.loc[df.month == 9, cols]
    
    # compute average of metrics by date
    adf = df.groupby('date').agg(Up_Mbps = ('Up_Mbps', 'mean'),
                                 Down_Mbps = ('Down_Mbps', 'mean'),
                                 Latency_ms = ('Latency_ms', 'mean'),
                                 Packet_Loss = ('Packet_Loss', 'mean')).reset_index()
    
    # # pivot longer
    # adf = pd.melt(adf, id_vars = ['date'], var_name = 'Metrics', value_name = 'value')
    adf['intersection'] = file_name
    
    return adf

raw_files = {'Kierland': ['Bell_64th_Gateway', 'Greenway_66thSt'],
             'Thomas_E_I17': ['Thomas_43rdAve', 'Thomas_75Ave'],
             'SouthWest': ['LowerBuckeye_83rdAve', 'VanBuren_83rdAve']}

file_data = []
for folder, files in raw_files.items():
    for file in files:
        print("Processing file: ", file)
        file_path = os.path.join(base_dir, folder, f"{file}.xlsx")
        file_df = processData(file_path, file)
        file_data.append(file_df)

adf = pd.concat(file_data)

# latency analysis
fig1 = px.line(adf, x = 'date', y = 'Latency_ms', color = 'intersection',
               labels = {'date': 'Dates in September',
                         'Latency_ms': 'Latency in millisecond'})
fig1.update_layout(legend = dict(yanchor = 'top', y = 0.99, xanchor = 'left', x = 0.01))
fig1.show()

# packet loss analysis
fig2 = px.line(adf, x = 'date', y = 'Packet_Loss', color = 'intersection',
               labels = {'date': 'Dates in September',
                         'Packet_Loss': 'Packet Loss (%)'})
fig2.update_layout(legend = dict(yanchor = 'top', y = 0.99, xanchor = 'left', x = 0.01))
fig2.show()

fig = px.line(adf, x = 'date', y = 'value', color = 'intersection', facet_col = 'Metrics', facet_col_wrap = 2)
fig.update_xaxes(matches = None)
fig.update_yaxes(matches = None)
fig.show()

# throughput analysis
tdf = adf[['Up_Mbps', 'Down_Mbps', 'date', 'intersection']].copy(deep = True)
tdf = pd.melt(tdf, id_vars = ['date', 'intersection'], var_name = 'Throughput_Metrics', value_name = 'value')

fig3 = px.line(tdf, x = 'date', y = 'value', color = 'intersection', facet_col = 'Throughput_Metrics',
               labels = {'date': 'Dates in September',
                         'value': 'Speed in Mbps'})
fig3.update_layout(legend = dict(yanchor = 'top', y = 0.99, xanchor = 'left', x = 0.01))
fig3.show()

# # compute average of metrics by date
# adf = df.groupby('date').agg(Up_Mbps = ('Up_Mbps', 'mean'),
#                              Down_Mbps = ('Down_Mbps', 'mean'),
#                              Latency_ms = ('Latency_ms', 'mean'),
#                              Packet_Loss = ('Packet_Loss', 'mean'),
#                              Noise_24_GHz = ('2.4_GHz_Noise', 'mean'),
#                              Noise_58_GHz = ('5.8_GHz_Noise', 'mean')).reset_index()

# # select columns for correlation analysis
# cdf = df.iloc[:, 0:18].copy(deep = True)
# corr = cdf.corr()

# # plot correlation heatmap
# fig = plt.figure()
# ax = fig.add_subplot(111)
# cax = ax.matshow(corr,cmap='coolwarm', vmin=-1, vmax=1)
# fig.colorbar(cax)
# ticks = np.arange(0,len(cdf.columns),1)
# ax.set_xticks(ticks)
# plt.xticks(rotation=90)
# ax.set_yticks(ticks)
# ax.set_xticklabels(cdf.columns)
# ax.set_yticklabels(cdf.columns)
# plt.show()