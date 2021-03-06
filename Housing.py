# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 13:40:52 2018

@author: Seizure
"""


import pandas as pd
from sklearn.pipeline import make_pipeline
from xgboost import XGBRegressor
from sklearn.model_selection import cross_val_score
from sklearn.impute import SimpleImputer
import datetime

################################   STEP ONE: ONE HOT ENCODING COMBINED DATA SET   ################################

train_file_path = 'C:/Users/Seizure/Documents/MachineLearning/Housing/train.csv'
test_file_path = 'C:/Users/Seizure/Documents/MachineLearning/Housing/test.csv'
combined_file_path = 'C:/Users/Seizure/Documents/MachineLearning/Housing/traintest.csv'
housing_data = pd.read_csv(combined_file_path)


#fill NA in the LotFrontage column with the average value
housing_data["LotFrontage"].fillna(housing_data.LotFrontage.mean(), inplace = True)
now = datetime.datetime.now()

coly = housing_data.columns.to_series().groupby(housing_data.dtypes).groups 
n_vars = list(housing_data.dtypes[housing_data.dtypes!="object"].index)
to_remove = ['Id', 'MSSubClass', 'OverallQual', 'OverallCond', 'YearBuilt','YearRemodAdd', 
             'GarageYrBlt', 'MoSold', 'YrSold']
for item in to_remove:
    n_vars.remove(item)
c_vars = list(housing_data.dtypes[housing_data.dtypes == "object"].index)
c_vars.extend(('OverallQual', 'OverallCond', #'YearBuilt','YearRemodAdd', 'GarageYrBlt'
                             'MoSold', 'YrSold'))

for variable in c_vars:
    dummies = pd.get_dummies(housing_data[variable], prefix=variable)
    housing_data = pd.concat([housing_data, dummies], axis = 1)
    housing_data.drop([variable], axis=1, inplace = True)

features = list(housing_data.columns.values)
icelist = ['Id', 'MSSubClass', 'YearBuilt', 'YearRemodAdd', 'GarageYrBlt', 'SalePrice']
for icecubes in icelist:
    features.remove(icecubes)
    
combined_X = housing_data[features]

#housing_data.to_csv('OneHotEncodedHousingData.csv', index = False)
#Split up OneHotEncoded File Manually then continue yourself.    
################################   STEP TWO: FEATURE ENGINEERING TEST DATA  ################################
    
    


# =============================================================================
# testcoly = test_data.columns.to_series().groupby(test_data.dtypes).groups
# test_n_vars = list(test_data.dtypes[test_data.dtypes!="object"].index)
# for item in to_remove:
#     test_n_vars.remove(item)
# test_c_vars = list(test_data.dtypes[test_data.dtypes == "object"].index)
# test_c_vars.extend(('OverallQual', 'OverallCond', #'YearBuilt','YearRemodAdd', 'GarageYrBlt'
#                              'MoSold', 'YrSold'))
# 
# test_features = list(test_data.columns.values)
# for
# for variable in test_c_vars:
#     dummies = pd.get_dummies(test_data[variable], prefix=variable)
#     test_data = pd.concat([test_data, dummies], axis = 1)
#     test_data.drop([variable], axis=1, inplace = True)
# =============================================================================
    
  



################################   STEP THREE: MODELLING  ################################
training_data = pd.read_csv(train_file_path)
y = training_data.SalePrice
X = training_data[features]
training_data['HouseAge'] = int(now.year) - training_data['YearRemodAdd']
training_data['GarageAge'] = int(now.year) - training_data['GarageYrBlt']

#train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1)

my_pipeline = make_pipeline(SimpleImputer(), XGBRegressor(n_estimators = 1000, 
                            n_early_stopping_rounds = 5, learning_rate = 0.05, n_jobs = -1))

my_pipeline.fit(X, y)
training_predictions = my_pipeline.predict(X)

traintest_predictions = my_pipeline.predict(combined_X)


################################   STEP FOUR: CROSS VALIDATION   ################################
scores = cross_val_score(my_pipeline, X, y, cv=5,  scoring = "neg_mean_absolute_error")
print(scores)
answer = (sum(scores)/len(scores))
print("Using XGBRegressor the " + str(answer) + ' Average Negative Mean Absolute Error.')
print(1+((answer)/180921.195890))

################################   STEP FIVE: PREDICT AGAINST TEST   ################################
test_data = pd.read_csv(test_file_path)
test_data["LotFrontage"].fillna(housing_data.LotFrontage.mean(), inplace = True)

test_data['HouseAge'] = int(now.year) - test_data['YearRemodAdd']
test_data['GarageAge'] = int(now.year) - test_data['GarageYrBlt']

test_X = test_data[features]  

test_predictions = my_pipeline.predict(test_X)
print(test_predictions)

df = pd.concat([test_data.Id, pd.DataFrame(test_predictions, columns = ['SalePrice'])], axis = 1)
df.to_csv('HousingPredictions_2b1s_02.csv', index = False)

import matplotlib.pyplot as plt
correlationmatrixdata = pd.read_csv('C:/Users/Seizure/Documents/MachineLearning/Housing/OriginalHousingDataSet/train.csv')
plt.matshow(correlationmatrixdata.corr())
def plot_corr(data):
    """This function plots a graphical correlation matrix for each pair of columns in the dataframe
    The length and width of the graph are limited to the amount of columns & rows divided by 8 to increase
    ease of use of outputted plots.
    Input:
        df: pandas DataFrame"""
        
    corr = data.corr()
    fig, ax = plt.subplots(figsize=(len(correlationmatrixdata.columns), len(correlationmatrixdata.columns)))
    ax.matshow(corr)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation = 90);
    plt.yticks(range(len(corr.columns)), corr.columns);
    plt.imshow(data.corr(), cmap='hot', interpolation = 'nearest')
    plt.colorbar()
    fig.set_size_inches(len(correlationmatrixdata.columns)/8,len(correlationmatrixdata.columns)/8)
    plt.savefig('correlationmatrix.png', dpi = 100)
plot_corr(correlationmatrixdata)


def Numerical_Data_Boxplot(DataFrame, n_vars):
    for n_var in n_vars:
        plt.figure()
        DataFrame.boxplot([n_var])
        plt.savefig('boxplot_'+str(n_var)+'.png', dpi = 100)
        plt.close()

def plot_bars(DataFrame, c_vars):
    """This function plots bar graphs for each one hot encoded variablem. The length and width
    of the graph are limited to increase ease of use of outputted plots.
    Input:
        df: pandas DataFrame"""
        
    for c_var in c_vars:
        plt.figure()
        DataFrame.plot.bar([c_var])
        plt.savefig('bargraph_'+str(c_var)+'.png', dpi = 100)
        plt.close
        