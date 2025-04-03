import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

os.chdir(r"D:\GitHub\wireless_communication")

# read data
file_input = "ignore/radio_data_processed_Jan.txt"
df = pd.read_csv(file_input, sep = '\t')

# drop Node and Time variables to anlayze the influence of predictors on perf metric
df.drop(['Node', 'Time'], axis = 1, inplace = True)

# convert area and peak to category type
df[['Area', 'Peak']] = df[['Area', 'Peak']].astype('category')

# # select area and drop column
# area = 'Southwest'
# df = df[df.Area == area]
# df.drop('Area', axis = 1, inplace = True)

# one-hot encoding: Peak
peak_dummies = pd.get_dummies(df.Peak, prefix = 'is_peak', prefix_sep = '_', drop_first = True, dtype = int)
df = pd.concat([df, peak_dummies], axis = 1)
df.drop('Peak', axis = 1, inplace = True)

# one-hot encoding: Area
area_dummies = pd.get_dummies(df.Area, prefix = 'is_area', prefix_sep = '_', drop_first = True, dtype = int)
df = pd.concat([df, area_dummies], axis = 1)
df.drop('Area', axis = 1, inplace = True)

# specify target and predictor variables
targets = ['Upload (Mbps)', 'Download (Mbps)', 'Latency (ms)', 'Packet Loss']
predictors = [col for col in df.columns if col not in targets]

target = targets[1]

# create dataset
df = df[[target] + predictors]
df.dropna(subset = target, axis = 0, inplace = True)

# specify predictors
X = df[predictors]
y = df[target]
features = list(X.columns)

# split dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 42)

# instantiate XGBoost regressor object
xgb_model = xgb.XGBRegressor(
    n_estimators = 200,
    learning_rate = 0.1,
    max_depth = 5,
    min_child_weight = 5,
    gamma = 0.1,
    reg_alpha = 0.5,
    reg_lambda = 0.5
)

# fit regressor to training set
xgb_model.fit(X_train, y_train)

# predict labels of the test set
y_pred = xgb_model.predict(X_test)

# compute RMSE and MAPE of predictions
mape = mean_absolute_percentage_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"MAPE, RMSE: {mape:.2f}, {rmse:.2f}")

# plot feature importance
xgb.plot_importance(xgb_model)
plt.rcParams['figure.figsize'] = [5, 5]
plt.show()