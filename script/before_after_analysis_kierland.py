import os
import pandas as pd

import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'
from plotly.subplots import make_subplots
import plotly.graph_objects as go

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/wireless_communication")

# read after data for Kierland area
akdf = pd.read_csv("ignore/data_after/kierland_intuicom_processed.txt", sep = '\t')

# read before data and filter for Kierland area
bdf = pd.read_csv("ignore/radio_data_processed_Jan.txt", sep = '\t')

# filter for Kierland area
bkdf = bdf.copy()[bdf.Area == 'Kierland']
bkdf.rename(columns = {'Time': 'DateTime', 'Upload (Mbps)': 'Upload', 'Download (Mbps)': 'Download', 
                       'Latency (ms)': 'Latency', 'Packet Loss': 'PacketLoss'}, inplace = True)

cols = ['Node', 'DateTime', 'Upload', 'Download', 'Latency', 'PacketLoss']

# select relevant columns and add period
bkdf = bkdf[cols]
akdf = akdf[cols]
bkdf['Period'] = 'Before'
akdf['Period'] = 'After'

# filter after data (exclude last date from analysis)
bkdf['DateTime'] = pd.to_datetime(bkdf['DateTime'])
akdf['DateTime'] = pd.to_datetime(akdf['DateTime'])
akdf = akdf[akdf.DateTime <= pd.Timestamp('2025-03-18 23:00:00')]

# update packet loss to %
bkdf['PacketLoss'] = bkdf['PacketLoss'] * 100
akdf['PacketLoss'] = akdf['PacketLoss'] * 100

# merge before and after datasets
kdf = pd.concat([bkdf, akdf], ignore_index = True)

var_names = {'Upload': 'Upload Speed (Mbps)', 
             'Download': 'Download Speed (Mbps)', 
             'Latency': 'Latency (ms)', 
             'PacketLoss': 'Packet Loss (%)'}

# function to create boxplot
def create_boxplot(variable):
    fig = px.box(kdf, x = 'Node', y = variable, color = 'Period',
           labels = {'Node': 'Nodes in Kierland Area', variable: var_names[variable]})
    fig.update_layout(font = dict(size = 16), 
                      legend = dict(yanchor = 'top', y = 0.99, xanchor = 'left', x = 0.01, bgcolor='rgba(0,0,0,0)'),
                      legend_title_text = '')
    fig.show()
    
create_boxplot('Upload')
create_boxplot('Download')
create_boxplot('Latency')
create_boxplot('PacketLoss')

# function to create heatmap
def create_heatmap(variable, plot_title):
    # function to create heatmap
    bk_pivot = bkdf.pivot_table(index = 'Node', columns = 'DateTime', values = variable, aggfunc = 'mean')
    ak_pivot = akdf.pivot_table(index = 'Node', columns = 'DateTime', values = variable, aggfunc = 'mean')
    
    # create subplot layout
    fig = make_subplots(
        rows = 2, cols = 1,
        shared_xaxes = False, shared_yaxes = False,
        subplot_titles = ['Before', 'After']
    )
    
    # compute global min and max across both datasets for shared legend
    zmax = max(bkdf[variable].min(), akdf[variable].max())
    if variable == 'PacketLoss':
        zmin = 0
        zmax = 100
    else:
        zmin = min(bkdf[variable].min(), akdf[variable].min())
    
    # before period heatmap
    fig.add_trace(go.Heatmap(
        z = bk_pivot.values,
        x = bk_pivot.columns,
        y = bk_pivot.index,
        zmin = zmin, zmax = zmax,
        colorscale = 'Viridis',
        showscale = False
    ), row = 1, col = 1)
    
    # after period heatmap
    fig.add_trace(go.Heatmap(
        z = ak_pivot.values,
        x = ak_pivot.columns,
        y = ak_pivot.index,
        zmin = zmin, zmax = zmax,
        colorscale = 'Viridis',
        colorbar = dict(
            title = plot_title, 
            orientation = 'h', x = 0.5, xanchor = 'center', y = 0.45, yanchor = 'bottom',
            thickness = 15, len = 0.5
        )
    ), row = 2, col = 1)
    
    # layout
    fig.update_layout(
        height = 750, font = dict(size = 16), title = ''
    )
    fig.show()

create_heatmap('Upload', 'Upload Speed (Mbps)')
create_heatmap('Download', 'Download Speed (Mbps)')
create_heatmap('Latency', 'Latency (ms)')
create_heatmap('PacketLoss', 'Packet Loss (%)')