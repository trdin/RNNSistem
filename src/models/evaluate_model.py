import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense 
from tensorflow.keras.models import Sequential
import tensorflow as tf
import joblib
import src.data.prepare_learn_data as pld
import src.helpers.calculate as calc
import src.visualization.visualization as vis
import os
import mlflow
import dagshub.auth
import dagshub
import src.models.train as tm

import src.settings as settings


def evaluate_model(data_path, station_name,windowsize = 24):

   

    dagshub.auth.add_app_token(token=settings.mlflow_tracking_password)
    dagshub.init("RNNSistem", settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    
    mlflow.start_run(run_name=station_name, experiment_id="1", nested=True)
    
    mlflow.tensorflow.autolog()


    model = tf.keras.models.load_model('./models/'+station_name+'/model.h5')
    stands_scaler = joblib.load('./models/'+station_name+'/stands_scaler.joblib')
    other_scaler = joblib.load('./models/'+station_name+'/other_scaler.joblib')


    learn_features, all_data = pld.prepare_data(data_path)


    stands_data = np.array(learn_features[:, 0])
    stands_normalized = stands_scaler.transform(stands_data.reshape(-1, 1))


    other_data = np.array(learn_features[:, 1:])
    other_normalized = other_scaler.transform(other_data)



    data_normalized = np.column_stack([stands_normalized, other_normalized])

    
    look_back = windowsize
    step = 1


    X_final, y_final = tm.create_multivariate_dataset_with_steps(data_normalized, look_back, step)


    X_final = X_final.reshape(X_final.shape[0], X_final.shape[2], X_final.shape[1])


    
    y_test_predicitons = model.predict(X_final)

    y_test_true = stands_scaler.inverse_transform(y_final.reshape(-1, 1))

    y_test_predicitons = stands_scaler.inverse_transform(y_test_predicitons)

    
    lstm_mae_adv, lstm_mse_adv, lstm_evs_adv = calc.calculate_metrics(y_test_true, y_test_predicitons)
    print("\nLSTM Model Metrics:")
    print(f"MAE: {lstm_mae_adv}, MSE: {lstm_mse_adv}, EVS: {lstm_evs_adv}")
    mlflow.log_metric("MSE", lstm_mse_adv)
    mlflow.log_metric("MAE", lstm_mae_adv)
    mlflow.log_metric("EVS", lstm_evs_adv)
    tm.ensure_directory_exists('./reports/'+station_name)
    tm.save_test_metrics(lstm_mae_adv, lstm_mse_adv, lstm_evs_adv, './reports/'+station_name+'/metrics.txt')
        

    mlflow.end_run()




def main():

    for i in range(1,2):
        print("Evaluating the model for station ", i, " ------------------------------------")  
        evaluate_model("./data/processed/"+str(i)+"/station_"+str(i)+"_test.csv", "station_"+str(i), windowsize=8)

if __name__ == '__main__':
    main()