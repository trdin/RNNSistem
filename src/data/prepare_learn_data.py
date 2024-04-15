import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from sklearn.feature_selection import mutual_info_regression


def printSkew(all_data):
    skewness_info = []
    for column in all_data.columns[1:]:
        skew = all_data[column].skew()
        skewness_info.append((column, skew))

    # Pretvori seznam v DataFrame za lažje prikazovanje
    skewness_df = pd.DataFrame(skewness_info, columns=['Column Name', 'Skewness'])

    # Izpišite oznako stolpca in njegovo poševnost
    print(skewness_df)


def information_gain(all_data):
    target = all_data['available_bike_stands']
    target_feature = all_data.drop('date', axis=1)

    info_gains = mutual_info_regression(target_feature.drop('available_bike_stands', axis=1), target)

    info_gain_df = pd.DataFrame({'Feature': target_feature.columns.drop('available_bike_stands'), 'Information_Gain': info_gains})
    info_gain_df = info_gain_df.sort_values(by='Information_Gain', ascending=False)

    print(info_gain_df)

    threshold = 0.03
    selected_features = info_gain_df[info_gain_df['Information_Gain'] >= threshold]['Feature']
    return selected_features

def prepare_data(path_to_data):
    all_data = pd.read_csv(path_to_data)
    print(all_data.head())



    all_data['date'] = pd.to_datetime(all_data['date'])
    all_data.sort_values(by='date', inplace=True)

    all_data.set_index('date', inplace=True)
    all_data = all_data.resample('H').mean()
    all_data.reset_index(inplace=True)
    all_data = all_data.dropna()

    features = ['available_bike_stands', 'temperature', 'relative_humidity',
                'apparent_temperature', 'dew_point', 'precipitation_probability',
                'surface_pressure','bike_stands', 'rain']
    all_data = all_data[['date'] + features]

    all_data.isnull().sum()

    missing_values = all_data.isnull().sum()

    print(missing_values)
    features_with_missing_values = missing_values[missing_values > 0].index
        
    all_data = all_data.copy()
    columns_with_missing_values = all_data.columns[all_data.isnull().any()].tolist()
    columns_complete_values = all_data.drop(columns_with_missing_values + ["date"], axis=1).columns.tolist()

    missing_df = all_data[all_data.isnull().any(axis=1)]
    complete_df = all_data.dropna()

    for column in columns_with_missing_values:
        X = complete_df[columns_complete_values]
        y = complete_df[column]
        
        model = RandomForestRegressor()
        model.fit(X, y)
        
        missing_X = missing_df[columns_complete_values]
        predictions = model.predict(missing_X)
        
        all_data.loc[missing_df.index, column] = predictions

    missing_values = all_data.isnull().sum()

    print(missing_values)

   


    left_skew_columns = ["surface_pressure"]
    for col in left_skew_columns:
        all_data[col] = np.square(all_data[col])

    right_skew_columns = ["rain", "precipitation_probability"]
    for col in right_skew_columns:
        all_data[col] = np.log(all_data[col]+1 )

    """ selected_features = information_gain(all_data)

    print("Selected Features:")
    print(selected_features)
 """
    selected_features = ['temperature',
        'apparent_temperature',
        'surface_pressure',
        'dew_point',
        'precipitation_probability',
        'relative_humidity', "rain"]

    learn_features = all_data[ ['available_bike_stands']+ list(selected_features)]
    learn_features = learn_features.values
    return learn_features, all_data