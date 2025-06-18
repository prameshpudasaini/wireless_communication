import os
import pandas as pd

import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'
from plotly.subplots import make_subplots
import plotly.graph_objects as go

os.chdir(r"/Users/prameshpudasaini/Library/CloudStorage/OneDrive-UniversityofArizona/GitHub/wireless_communication")

# =============================================================================
# before data
# =============================================================================

# read before data and filter for Thomas area
bdf = pd.read_csv("ignore/radio_data_processed_Jan.txt", sep = '\t')
bdf = bdf[bdf.Area == 'Thomas']

bdf['Tx Rate (Mbps)'] = bdf['Tx Rate (Kbps)'] / 1000
bdf['Rx Rate (Mbps)'] = bdf['Rx Rate (Kbps)'] / 1000

bdf.rename(columns = {'Time': 'DateTime', 'Upload (Mbps)': 'Upload', 'Download (Mbps)': 'Download', 
                       'Latency (ms)': 'Latency', 'Packet Loss': 'PacketLoss'}, inplace = True)

cols = ['Node', 'DateTime', 'Tx Rate (Mbps)', 'Rx Rate (Mbps)', 'Latency', 'PacketLoss']
bdf = bdf[cols]

bdf['PacketLoss'] = bdf['PacketLoss'] * 100
bdf['Period'] = 'Before'

# function to create heatmap
def create_heatmap(xdf, var1, var2, plot_title):
    # function to create heatmap
    tx_pivot = xdf.pivot_table(index = 'Node', columns = 'DateTime', values = var1, aggfunc = 'mean')
    rx_pivot = xdf.pivot_table(index = 'Node', columns = 'DateTime', values = var2, aggfunc = 'mean')
    
    # create subplot layout
    fig = make_subplots(
        rows = 2, cols = 1,
        shared_xaxes = False, shared_yaxes = False,
        subplot_titles = ['Tx Rate (Mbps)', 'Rx Rate (Mbps)']
    )
    
    # before period heatmap
    fig.add_trace(go.Heatmap(
        z = tx_pivot.values,
        x = tx_pivot.columns,
        y = tx_pivot.index,
        colorscale = 'Viridis',
        showscale = False
    ), row = 1, col = 1)
    
    # after period heatmap
    fig.add_trace(go.Heatmap(
        z = rx_pivot.values,
        x = rx_pivot.columns,
        y = rx_pivot.index,
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

create_heatmap(bdf, 'Tx Rate (Mbps)', 'Rx Rate (Mbps)', 'Tx and Rx Rates')

box_PL = px.box(bdf, x = 'Node', y = 'PacketLoss', labels = {'PacketLoss': 'Packet Loss (%)'})
box_PL.update_layout(font = dict(size = 16))
box_PL.show()

# =============================================================================
# after data
# =============================================================================

# read after data for Thomas area
adf1 = pd.read_csv("ignore/data_after/Encom/2025-03-26 - 09-04-49 - Wireless Link Log.csv")
adf2 = pd.read_csv("ignore/data_after/Encom/2025-03-26 - 19-13-04 - Wireless Link Log.csv")
adf3 = pd.read_csv("ignore/data_after/Encom/2025-03-27 - 07-40-32 - Wireless Link Log.csv")
adf4 = pd.read_csv("ignore/data_after/Encom/2025-03-27 - 11-23-05 - Wireless Link Log.csv")

adf = pd.concat([adf1, adf2, adf3, adf4], ignore_index = False)

# select relevant columns
cols = ['Date', 'Time', 'Source Name', 'Dest Name', 'Tx Rate (Mbps)', 
        'Rx Rate (Mbps)', 'Tx CCQ (%)', 'Rx CCQ (%)']
adf = adf[cols]

# select relevant nodes
nodes = ['59th Ave Osborn Remote', '59th Ave Indian School Master', '59th Ave Thomas NB Remote']
adf = adf[adf['Source Name'].isin(nodes)]

# rename nodes
adf.rename(columns = {'Source Name': 'Node'}, inplace = True)
name_map = {
    '59th Ave Osborn Remote': 'Osborn Rd & 59th Ave',
    '59th Ave Thomas NB Remote': 'Thomas Rd & 59th Ave',
    '59th Ave Indian School Master': 'Indian School Rd & 59th Ave'
}
adf['Node'] = adf['Node'].map(name_map)

# convert datetime
adf['DateTime'] = pd.to_datetime(adf['Date'] + ' ' + adf['Time'], format = '%m/%d/%Y %H:%M:%S')
adf.drop(['Date', 'Time', 'Dest Name'], axis = 1, inplace = True)

# aggregate after period data to 1 min
adf = adf.set_index('DateTime')
adf = adf.groupby('Node')[cols[4:]].resample('1min').mean().reset_index()

adf.dropna(inplace = True)
adf['Period'] = 'After'

# =============================================================================
# before-after analysis
# =============================================================================

# comparison of Tx and Rx rates
common_cols = ['Node', 'DateTime', 'Period', 'Tx Rate (Mbps)', 'Rx Rate (Mbps)']
trdf = pd.concat([adf[common_cols], bdf[common_cols]])

# function to create boxplot
def create_boxplot(variable):
    fig = px.box(trdf, x = 'Node', y = variable, color = 'Period',
           labels = {'Node': 'Nodes in Thomas West of I-17 Area'})
    fig.update_layout(font = dict(size = 16), 
                      legend = dict(yanchor = 'top', y = 0.99, xanchor = 'left', x = 0.9, bgcolor='rgba(0,0,0,0)'),
                      legend_title_text = '')
    fig.show()
    
create_boxplot('Tx Rate (Mbps)')

# pivot longer for Tx CCQ and Rx CCQ
adf_CCQ = pd.melt(adf, id_vars = ['DateTime', 'Node'], value_vars = ['Tx CCQ (%)', 'Rx CCQ (%)'],
                  var_name = 'CCQ Type', value_name = 'CCQ Value')

box_CCQ = px.box(adf_CCQ, x = 'Node', y = 'CCQ Value', color = 'CCQ Type', 
                 labels = {'CCQ Value': 'Client Connection Quality (%)'})

box_CCQ.update_layout(font = dict(size = 16), 
                  legend = dict(yanchor = 'top', y = 0.99, xanchor = 'left', x = 0.9, bgcolor='rgba(0,0,0,0)'),
                  legend_title_text = '')
box_CCQ.show()