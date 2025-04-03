import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import IsolationForest

import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'

os.chdir(r"D:\GitHub\wireless_communication")

# read data
file_input = "ignore/radio_data_processed.txt"
df = pd.read_csv(file_input, sep = '\t')

study_areas = ['Kierland', ]

# =============================================================================
# data preprocessing
# =============================================================================

# convert time to datetime
df.Time = pd.to_datetime(df.Time) # convert to pandas datetime

# # check next hop upstream router
# hop_df = df.copy()[['Node', 'Next Hop Upstream Router']]
# hop_df.drop_duplicates(inplace = True)

# check data availability for each node
# px.scatter(df, x = 'Time', y = 'Node').show()

# add month, day, hour variables
df['Month'] = df.Time.dt.month
df['Day'] = df.Time.dt.day_name()
df['Hour'] = df.Time.dt.hour

# classify hours into 4 peaks
df['Peak'] = np.select([(df.Hour >= 6) & (df.Hour < 10),
                        (df.Hour >= 10) & (df.Hour < 15),
                        (df.Hour >= 15) & (df.Hour < 19),
                        (df.Hour >= 19) | (df.Hour < 6)],
                       ['Morning', 'Mid-day', 'Evening', 'Night'])

# filter data for January 2024
df = df[df.Month == 1]

# select relevant metrics
metrics_all = ['Upload (Mbps)', 'Download (Mbps)',
               'Latency (ms)', 'Packet Loss',
               '2.4 GHz Noise', '5.8 GHz Noise',
               'Tx Rate (Kbps)', 'Rx Rate (Kbps)',
               '2.4 GHz Airtime Total', '5.8 GHz Airtime Total',
               '2.4 GHz Routed Clients', 'Hop Count']
perf_metrics = metrics_all[:4]
# Note: '5.8_GHz_Routed_Clients' is removed as it has 0 values.

# select relevant columns for analysis
df = df[['Area', 'Node', 'Time', 'Peak'] + metrics_all]

# convert columns to float type
cols_float = ['Packet Loss', '2.4 GHz Airtime Total', '5.8 GHz Airtime Total']
df[cols_float] = df[cols_float].astype(float)

# df.to_csv("ignore/radio_data_processed_Jan.txt", sep = '\t', index = False)

# =============================================================================
# functions
# =============================================================================

# function to plot correlation
def plot_correlation(cor_df, area):
    corr = cor_df.corr() # compute correlation
    
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
            
    plt.title(f"{area}", fontweight = 'bold')
    
    output_path = os.path.join("output/correlation_heatmap_202401_" + area + '.png')
    plt.savefig(output_path, dpi = 1200, bbox_inches = 'tight')
    plt.show()

# function to summarize statistics of perf metrics
def perf_metrics_summary(metric):
    # compute mean, st dev, and median
    xdf = df.groupby(['Area', 'Node'])[metric].agg(
        Mean = 'mean',
        Std = 'std',
        Median = 'median'
    ).reset_index()
    
    # add metric as varible
    xdf['Metric'] = metric
    
    return xdf

# =============================================================================
# correlation analysis
# =============================================================================

# correlation in all study areas
cor_df = df.copy()[metrics_all]
# plot_correlation(cor_df, 'All Study Areas')

# correlation by study areas
for area in list(df.Area.unique()):
    cor_df_area = df.copy()[metrics_all][df.Area == area]
    # plot_correlation(cor_df_area, area)

# =============================================================================
# spatiotemporal analysis
# =============================================================================

# list of nodes in each study area
area_K = list(df[df.Area == 'Kierland'].Node.unique())
area_T = list(df[df.Area == 'Thomas'].Node.unique())
area_S = list(df[df.Area == 'Southwest'].Node.unique())

# specify plotting order
order_day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
order_peak = ['Morning', 'Mid-day', 'Evening', 'Night']
order_area = ['Kierland', 'Thomas', 'Southwest']
order_node = area_K + area_T + area_S

# upload speed by study area
px.box(
    df,
    x = 'Node',
    y = 'Upload (Mbps)',
    color = 'Area',
    category_orders = {'Area': order_area}
).update_layout(
    xaxis_title_font = dict(size = 18),
    yaxis_title_font = dict(size = 18),
    legend_title_font = dict(size = 18),
    font = dict(size = 18)
).show()

# upload speed by study area and peak
px.box(
    df,
    x = 'Node',
    y = 'Upload (Mbps)',
    color = 'Peak',
    category_orders = {'Node': order_node, 'Peak': order_peak}
).show()

# download speed by study area and peak
px.box(
    df,
    x = 'Node',
    y = 'Download (Mbps)',
    color = 'Peak',
    category_orders = {'Node': order_node, 'Peak': order_peak}
).show()

# latency by study area
px.box(
    df,
    x = 'Node',
    y = 'Latency (ms)',
    color = 'Area',
    category_orders = {'Area': order_area}
).update_layout(
    xaxis_title_font = dict(size = 18),
    yaxis_title_font = dict(size = 18),
    legend_title_font = dict(size = 18),
    font = dict(size = 18)
).show()

# packet loss by study area
px.box(
    df,
    x = 'Node',
    y = 'Packet Loss',
    color = 'Area',
    category_orders = {'Area': order_area}
).update_layout(
    xaxis_title_font = dict(size = 18),
    yaxis_title_font = dict(size = 18),
    legend_title_font = dict(size = 18),
    font = dict(size = 18)
).show()


list_perf_df = [] # store stats of performance metrics in a list

# loop through each metric and store resulting statistics
for metric in perf_metrics:
    list_perf_df.append(perf_metrics_summary(metric))

# combine summary df from list    
pdf = pd.concat(list_perf_df, ignore_index = True)

# round statistics
pdf[['Mean', 'Std', 'Median']] = pdf[['Mean', 'Std', 'Median']].round(2)

# pivot wider and rename columns
pdf = pdf.pivot_table(index = ['Area', 'Node'], columns = 'Metric', values = ['Mean', 'Std', 'Median'], aggfunc = 'first')
pdf.columns = ['{}_{}'.format(stat, metric) for stat, metric in pdf.columns]
pdf.reset_index(inplace = True)

# save summary statistics of performance metrics
# pdf.to_csv("ignore/radio_data_perf_summary.csv", index = False)

# =============================================================================
# impact of environmental factors
# =============================================================================

env_metrics = ['2.4 GHz Noise', '5.8 GHz Noise', 'Hop Count']
list_env_df = [] # store stats of network utilization in a list

# loop through each metric and store resulting statistics
for metric in env_metrics:
    list_env_df.append(perf_metrics_summary(metric))
    
# combine summary df from list    
edf = pd.concat(list_env_df, ignore_index = True)

# round statistics
edf[['Mean', 'Std', 'Median']] = edf[['Mean', 'Std', 'Median']].round(2)

# pivot wider and rename columns
edf = edf.pivot_table(index = ['Area', 'Node'], columns = 'Metric', values = ['Mean', 'Std', 'Median'], aggfunc = 'first')
edf.columns = ['{}_{}'.format(stat, metric) for stat, metric in edf.columns]
edf.reset_index(inplace = True)

# save summary statistics of environmental factors
# edf.to_csv("ignore/radio_data_env_summary.csv", index = False)

# =============================================================================
# efficiency of network resources
# =============================================================================

util_metrics = ['Tx Rate (Kbps)', 'Rx Rate (Kbps)', '2.4 GHz Airtime Total', '5.8 GHz Airtime Total']
list_util_df = [] # store stats of network utilization in a list

# loop through each metric and store resulting statistics
for metric in util_metrics:
    list_util_df.append(perf_metrics_summary(metric))
    
# combine summary df from list    
udf = pd.concat(list_util_df, ignore_index = True)

# round statistics
udf[['Mean', 'Std', 'Median']] = udf[['Mean', 'Std', 'Median']].round(2)

# pivot wider and rename columns
udf = udf.pivot_table(index = ['Area', 'Node'], columns = 'Metric', values = ['Mean', 'Std', 'Median'], aggfunc = 'first')
udf.columns = ['{}_{}'.format(stat, metric) for stat, metric in udf.columns]
udf.reset_index(inplace = True)

# save summary statistics of utilization metrics
# udf.to_csv("ignore/radio_data_util_summary.csv", index = False)

# airtime usage by node and peak
px.box(
    df,
    x = 'Node',
    y = '2.4 GHz Airtime Total',
    color = 'Peak',
    category_orders = {'Node': order_node, 'Peak': order_peak}
).show()

# =============================================================================
# anomaly detection using Isolation Forest
# =============================================================================

# drop rows with missing values
idf = df.copy()
idf.dropna(inplace = True)

# initialize model
isolation_forest = IsolationForest(contamination = 0.01, random_state = 42)

# fit model
isolation_forest.fit(idf[perf_metrics])

# predict anomalies
idf['anomaly_score'] = isolation_forest.predict(idf[perf_metrics])

# mark anomalies (anomaly score = -1) and normal points (anomaly_score = 1)
idf['is_anomaly'] = idf['anomaly_score'] == -1

for area in list(idf.Area.unique()):
    # filter for study area
    idf_area = idf.copy()[idf.Area == area]
    
    # normal points and anomalies
    normal_points = idf_area[idf_area['is_anomaly'] == False]
    anomalies = idf_area[idf_area['is_anomaly'] == True]

    # plot normal points and anomalies
    plt.figure()
    
    plt.scatter(
        normal_points['Upload (Mbps)'],
        normal_points['Latency (ms)'],
        c = 'green',
        label = 'Normal',
        alpha = 0.7,
        edgecolors = 'w',
        s = 30
    )
    
    plt.scatter(
        anomalies['Upload (Mbps)'],
        anomalies['Latency (ms)'],
        c = 'red',
        label = 'Anomaly',
        alpha = 0.7,
        edgecolors = 'w',
        s = 30
    )
    
    # titles and labels
    plt.title(f"{area}", fontweight = 'bold')
    plt.xlabel('Upload (Mbps)')
    plt.ylabel('Latency (ms)')
    plt.legend()    
    
    output_path = os.path.join("output/anomaly_detection_202401_" + area + '.png')
    plt.savefig(output_path, dpi = 1200, bbox_inches = 'tight')
    plt.show()
