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
bdf = bdf[bdf.Area == 'Southwest']
bdf['DateTime'] = pd.to_datetime(bdf['Time'])

bdf['Packet Loss (%)'] = bdf['Packet Loss'] * 100

# heatmap for upload and download speed
def create_heatmap(xdf, var1, var2, plot_title):
    # function to create heatmap
    u_pivot = xdf.pivot_table(index = 'Node', columns = 'DateTime', values = var1, aggfunc = 'mean')
    d_pivot = xdf.pivot_table(index = 'Node', columns = 'DateTime', values = var2, aggfunc = 'mean')
    
    # create subplot layout
    fig = make_subplots(
        rows = 2, cols = 1,
        shared_xaxes = False, shared_yaxes = False,
        subplot_titles = ['Upload Speed (Mbps)', 'Download Speed (Mbps)']
    )
    
    # before period heatmap
    fig.add_trace(go.Heatmap(
        z = u_pivot.values,
        x = u_pivot.columns,
        y = u_pivot.index,
        colorscale = 'Viridis',
        showscale = False
    ), row = 1, col = 1)
    
    # after period heatmap
    fig.add_trace(go.Heatmap(
        z = d_pivot.values,
        x = d_pivot.columns,
        y = d_pivot.index,
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

create_heatmap(bdf, 'Upload (Mbps)', 'Download (Mbps)', 'Upload and Download Speeds')

# function to create boxplot
def create_boxplot(variable):
    fig = px.box(bdf, x = 'Node', y = variable, labels = {'Node': 'Nodes in SouthWest Area'})
    fig.update_layout(font = dict(size = 16), 
                      legend = dict(yanchor = 'top', y = 0.99, xanchor = 'left', x = 0.9, bgcolor='rgba(0,0,0,0)'),
                      legend_title_text = '')
    fig.show()
    
create_boxplot('Latency (ms)')
create_boxplot('Packet Loss (%)')
