import os
import re
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = 'browser'

os.chdir(r"D:\GitHub\wireless_communication")
base_dir = "ignore/radio_data_20231226_20240125"

# list of files with radio performance data
files = os.listdir(base_dir)

# # convert numeric values to ordinal
# def convert_ordinal(n):
#     return "%d%s" % (n, 'th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))

# # convert intersection/node name to standard format
# def convert_node_name(name):
#     # remove trailing ".xlsx"
#     name = name.replace('.xlsx', '')
    
#     # replace numeric street number with ordinals
#     name = re.sub(r'\b(\d+)\b', lambda x: convert_ordinal(int(x.group())), name) # numeric-ordinal conversion
    
#     # replace parts
#     parts = name.replace(' ave', '').split()
    
#     # join parts with &
#     return ' & '.join(parts)
    
# nodes = [convert_node_name(name) for name in files]

# reads Excel file and resolve header formatting
def readExcelFile(file_path, file_name):
    file_path = os.path.join(base_dir, file_name)
    df = pd.read_excel(file_path, sheet_name = 'Sheet1', header = [0, 1])
    
    # modify multi-header to single header for column names
    df.columns = ['_'.join(col) if not pd.isnull(col[1]) else col[0] for col in df.columns]
    
    # format column name
    df.columns = df.columns.str.replace(r'_Unnamed.*', '', regex = True) # replace all characters after Unnamed
    df.columns = df.columns.str.replace('# ', '') # remove # sign
    df.columns = df.columns.str.replace('r[()]', '', regex = True) # remove parentheses
    df.columns = df.columns.str.strip().str.replace(' ', '_') # strip whitespace and add underscore
    
    return df

ldf = [] # stores each Excel file as df 

# read all Excel files
for file in files:
    print("Reading file: ", file)
    file_path = os.path.join(base_dir, file)

    temp = readExcelFile(file_path, file)    
    temp['Node'] = file[:-5] # add node name as column    
    ldf.append(temp) # append to combined df

cdf = pd.concat(ldf) # concatenate all

# split time into month, date and hour
cdf[['month', 'date', 'hour']] = cdf['Time'].str.split(' ', expand = True)
cdf.month = cdf.month.apply(lambda x: datetime.strptime(x, '%b').month).astype(str)
cdf.hour = cdf.hour.str.extract(r'(\d+)')

# filter data for January
cdf = cdf[cdf.month == '1']
cdf['year'] = '2024' # add year column

# convert time to timestamp
cdf.Time = pd.to_datetime(cdf.year + ' ' + cdf.month + ' ' + cdf.date + ' ' + cdf.hour, format = '%Y %m %d %H')
cdf.drop(['year', 'month', 'date', 'hour'], axis = 1, inplace = True)

# update node names to standard format
node_names = {
    'Buckeye 67 ave': 'Buckeye Rd & 67th Ave',
    'Greenway 64 ST': 'Greenway Rd & 64th St',
    'IndianSchool 59 ave': 'Indian School Rd & 59th Ave',
    'Lowerbuckeye 67 ave': 'Lower Buckeye Rd & 67th Ave',
    'Lowerbuckeye 75 ave': 'Lower Buckeye Rd & 75th Ave',
    'Lowerbuckeye 83 ave': 'Lower Buckeye Rd & 83rd Ave',
    'Osborn 43 ave': 'Osborn Rd & 43rd Ave',
    'Osborn 59': 'Osborn Rd & 59th Ave',
    'Thomas 31 ave': 'Thomas Rd & 31st Ave',
    'Thomas 43ave': 'Thomas Rd & 43rd Ave',
    'Thomas 59 ave': 'Thomas Rd & 59th Ave',
    'Thunderbird 64 ST': 'Thunderbird Rd & 64th St',
    'ThunderbirdHAWK 70 ST': 'Thunderbird Rd & 70th St HAWK',
    'VanBuren 67 ave': 'Van Buren St & 67th Ave'}

cdf.Node = cdf.Node.replace(node_names)

# add study area
cdf['Area'] = np.select([cdf.Node.str.contains('Greenway|Thunderbird'),
                         cdf.Node.str.contains('Indian School|Osborn|Thomas'),
                         cdf.Node.str.contains('Van Buren|Buckeye')],
                        ['Kierland', 'Thomas West of I-17', 'Southwest'])

# drop redundant columns from analysis
cols = ['2.4_GHz_Airtime_TX',
        '2.4_GHz_Airtime_RX',
        '2.4_GHz_Airtime_Total',
        '5.8_GHz_Airtime_TX',
        '5.8_GHz_Airtime_RX',
        '5.8_GHz_Airtime_Total',
        '5.8_GHz_Tx_Rate_(Kbps)',
        '5.8_GHz_Rx_Rate_(Kbps)',
        '2.4_GHz_Routed_Clients',
        '5.8_GHz_Routed_Clients',
        'Hop_Count',
        '2.4_GHz_Channel',
        '5.8_GHz_Channel',
        'Next_Hop_Upstream_Router']

cdf.drop(cols, axis = 1, inplace = True)

# specify plotting orders for study areas and nodes
area_order = {'Area': ['Kierland', 'Thomas West of I-17', 'Southwest']}

area_K = list(cdf[cdf.Area == 'Kierland'].Node.unique())
area_T = list(cdf[cdf.Area == 'Thomas West of I-17'].Node.unique())
area_S = list(cdf[cdf.Area == 'Southwest'].Node.unique())
node_order = {'Node': area_K + area_T + area_S}

# =============================================================================
# throughput analysis
# =============================================================================

# box plots
thru_up_box = px.box(
    cdf, 
    x = 'Node', 
    y = 'Up_(Mbps)', 
    color = 'Area', 
    category_orders = node_order, 
    labels = {'Up_(Mbps)': 'Upload speed in Mbps'})
thru_up_box.update_layout(legend = dict(yanchor = 'top', y = 0.99, xanchor = 'right', x = 0.99))
thru_up_box.show()

thru_down_box = px.box(
    cdf, 
    x = 'Node', 
    y = 'Down_(Mbps)', 
    color = 'Area', 
    category_orders = node_order, 
    labels = {'Down_(Mbps)': 'Download speed in Mbps'})
thru_down_box.update_layout(legend = dict(yanchor = 'top', y = 0.99, xanchor = 'right', x = 0.99))
thru_down_box.show()

# heatmap
thru_up_heatmap = go.Figure(data = go.Heatmap(
    x = cdf['Time'], 
    y = cdf['Node'], 
    z = cdf['Up_(Mbps)'], 
    colorscale = 'Reds'))
thru_up_heatmap.update_layout(
    title = dict(text = 'Throughput analysis: upload speed (Mbps) in January'),
    yaxis = dict(categoryorder = 'array', categoryarray = list(node_order.values())[0]))
thru_up_heatmap.show()

thru_down_heatmap = go.Figure(data = go.Heatmap(
    x = cdf['Time'], 
    y = cdf['Node'], 
    z = cdf['Down_(Mbps)'], 
    colorscale = 'Viridis'))
thru_down_heatmap.update_layout(
    title = dict(text = 'Throughput analysis: download speed (Mbps) in January'),
    yaxis = dict(categoryorder = 'array', categoryarray = list(node_order.values())[0]))
thru_down_heatmap.show()

# =============================================================================
# latency analysis
# =============================================================================

# box plots
latency_box = px.box(
    cdf, 
    x = 'Node', 
    y = 'Latency_(ms)', 
    color = 'Area', 
    category_orders = node_order, 
    labels = {'Latency_(ms)': 'Latency in millisecond'})
latency_box.update_layout(legend = dict(yanchor = 'top', y = 0.99, xanchor = 'right', x = 0.99))
latency_box.show()

# heatmap
latency_heatmap = go.Figure(data = go.Heatmap(
    x = cdf['Time'], 
    y = cdf['Node'], 
    z = cdf['Latency_(ms)'], 
    colorscale = 'Reds'))
latency_heatmap.update_layout(
    title = dict(text = 'Latency analysis'),
    yaxis = dict(categoryorder = 'array', categoryarray = list(node_order.values())[0]))
latency_heatmap.show()

# =============================================================================
# packet loss analysis
# =============================================================================

# box plots
packet_box = px.box(
    cdf, 
    x = 'Node', 
    y = 'Packet_Loss', 
    color = 'Area', 
    category_orders = node_order, 
    labels = {'Packet_Loss': 'Packet loss'})
packet_box.update_layout(legend = dict(yanchor = 'top', y = 0.99, xanchor = 'right', x = 0.6))
packet_box.show()

# heatmap
packet_heatmap = go.Figure(data = go.Heatmap(
    x = cdf['Time'], 
    y = cdf['Node'], 
    z = cdf['Packet_Loss'], 
    colorscale = 'Reds'))
packet_heatmap.update_layout(
    title = dict(text = 'Packet loss analysis'),
    yaxis = dict(categoryorder = 'array', categoryarray = list(node_order.values())[0]))
packet_heatmap.show()

# =============================================================================
# received signal strength analysis
# =============================================================================

# box plots
rss_box = px.box(
    cdf, 
    x = 'Node', 
    y = 'RPSP', 
    color = 'Area', 
    category_orders = node_order, 
    labels = {'RPSP': 'Received point-to-point signal strength'})
rss_box.update_layout(legend = dict(yanchor = 'top', y = 0.99, xanchor = 'right', x = 0.99))
rss_box.show()

# heatmap
rss_heatmap = go.Figure(data = go.Heatmap(
    x = cdf['Time'], 
    y = cdf['Node'], 
    z = cdf['RPSP'], 
    colorscale = 'Viridis'))
rss_heatmap.update_layout(
    title = dict(text = 'Received signal strength analysis'),
    yaxis = dict(categoryorder = 'array', categoryarray = list(node_order.values())[0]))
rss_heatmap.show()

# =============================================================================
# correlation heatmap
# =============================================================================

# select columns for correlation analysis
cor_df = cdf.iloc[:, 1:11].copy(deep = True)
corr = cor_df.corr()

# plot correlation heatmap
fig = plt.figure()
ax = fig.add_subplot(111)
cax = ax.matshow(corr, cmap = 'coolwarm', vmin = -1, vmax = 1)
fig.colorbar(cax)
ticks = np.arange(0, len(cor_df.columns), 1)
ax.set_xticks(ticks)
plt.xticks(rotation = 90)
ax.set_yticks(ticks)
ax.set_xticklabels(cor_df.columns)
ax.set_yticklabels(cor_df.columns)

for i in range(len(cor_df.columns)):
    for j in range(len(cor_df.columns)):
        text = f"{corr.iloc[i, j]:.2f}"
        ax.text(j, i, text, ha = 'center', va = 'center', color = 'black', fontsize = 6)

plt.savefig('output/correlation_heatmap_202401.png', dpi = 1200, bbox_inches = 'tight')
plt.show()
