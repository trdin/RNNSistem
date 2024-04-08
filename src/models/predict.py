import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import src.data.weather_data as w
import src.data.mbike_data as mbike_data
import json
from datetime import timedelta




def predict(data, station_name = "default"):

    model = tf.keras.models.load_model('./models/'+station_name+'/model.h5')
    stands_scaler = joblib.load('./models/'+station_name+'/stands_scaler.joblib')
    other_scaler = joblib.load('./models/'+station_name+'/other_scaler.joblib')

    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values(by=['date'])


    left_skew_columns = ["surface_pressure"]
    for col in left_skew_columns:
        data[col] = np.square(data[col])

    right_skew_columns = ["precipitation_probability", "rain"]
    for col in right_skew_columns:
        data[col] = np.log(data[col]+1 )


    selected_features = ['temperature',
        'apparent_temperature',
        'surface_pressure',
        'dew_point',
        'precipitation_probability',
        'relative_humidity', "rain"]

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




def only_predict(data, model, stands_scaler, other_scaler):
    selected_features = ['temperature',
        'apparent_temperature',
        'surface_pressure',
        'dew_point',
        'precipitation_probability',
        'relative_humidity', "rain"]

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

def predict_station(station_name, station_number):

    model = tf.keras.models.load_model('./models/'+station_name+'/model.h5')
    stands_scaler = joblib.load('./models/'+station_name+'/stands_scaler.joblib')
    other_scaler = joblib.load('./models/'+station_name+'/other_scaler.joblib')

    


    data = pd.read_csv('./data/processed/'+station_name+'.csv')
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values(by=['date'])

    data = data.tail(24)


    left_skew_columns = ["surface_pressure"]
    for col in left_skew_columns:
        data[col] = np.square(data[col])

    right_skew_columns = ["precipitation_probability", "rain"]
    for col in right_skew_columns:
        data[col] = np.log(data[col]+1 )



    prediction = only_predict(data, model, stands_scaler, other_scaler)

    last_data = data.tail(1)

    

    latitude , longitude = get_station_location(station_number)


    new_datetime = last_data['date'].values[0] #add the correnct time 
    weather_data = w.fetch_and_write_weather_data(latitude, longitude, station_number, new_datetime)

    weather_data = json.loads(weather_data)

    print(weather_data)

    station_data = {
        "date": new_datetime,
        "temperature": weather_data["temperature"], 
        "relative_humidity": weather_data["relative_humidity"],
        "dew_point": weather_data["dew_point"],
        "apparent_temperature": weather_data["apparent_temperature"],
        "precipitation_probability":  np.log(weather_data["precipitation_probability"]+1 ),
        "rain": np.log( weather_data["rain"]+1 ),
        "surface_pressure": np.square(weather_data["surface_pressure"]),
        "bike_stands": last_data["bike_stands"].values[0],
        "available_bike_stands": prediction[0][0]
    }

    # Append the new row to the data DataFrame



    data = data.append(station_data, ignore_index=True)

    if len(data) > 24:
        data = data.iloc[1:]






    




def get_station_location(station_number):
    api_url = "https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey=5e150537116dbc1786ce5bec6975a8603286526b"
    station_data = mbike_data.fetch_data(api_url)
   

    for station in station_data:
        if station["number"] == station_number:
            return station["position"]["lat"], station["position"]["lng"]
    return None, None


predict_station("station_3", 3)



    