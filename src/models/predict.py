import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

model = tf.keras.models.load_model('./models/lstm_model_final.h5')
stands_scaler = joblib.load('./models/scalers/stands_scaler.joblib')
other_scaler = joblib.load('./models/scalers/other_scaler.joblib')

def predict(data):
    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values(by=['date'])


    left_skew_columns = ["surface_pressure"]
    for col in left_skew_columns:
        data[col] = np.square(data[col])

    right_skew_columns = ["precipitation_probability"]
    for col in right_skew_columns:
        data[col] = np.log(data[col]+1 )


    selected_features = ['temperature',
        'apparent_temperature',
        'surface_pressure',
        'dew_point',
        'precipitation_probability',
        'relative_humidity']

    learn_features = data[['available_bike_stands'] + list(selected_features) ]
    learn_features = learn_features.values

    

    stands = np.array(learn_features[:,0])

    print("stands scaler")


    stands_normalized = stands_scaler.transform(stands.reshape(-1, 1))

    print("other scaler")

    other = np.array(learn_features[:,1:])
    other_normalized = other_scaler.transform(other)


    normalized_data = np.column_stack([stands_normalized, other_normalized])

    X_predict = normalized_data   	
    
    X_predict = X_predict.reshape(1, X_predict.shape[1], X_predict.shape[0])
    

    prediction = model.predict(X_predict)
    prediction =  stands_scaler.inverse_transform(prediction)
    return prediction