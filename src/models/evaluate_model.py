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
from mlflow import MlflowClient
import src.models.train as tm
import src.models.mlflow_client as mc

import src.settings as settings





def evaluate_model(data_path, station_name,windowsize = 24):

   

    dagshub.auth.add_app_token(token=settings.mlflow_tracking_password)
    dagshub.init("RNNSistem", settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    
    mlflow.start_run(run_name=station_name, experiment_id="1", nested=True)
    
    mlflow.tensorflow.autolog()


    """ model = tf.keras.models.load_model('./models/'+station_name+'/model.h5')
    stands_scaler = joblib.load('./models/'+station_name+'/stands_scaler.joblib')
    other_scaler = joblib.load('./models/'+station_name+'/other_scaler.joblib') """

    model = mc.download_model(station_name, "staging")
    stands_scaler = mc.download_scaler(station_name, "stands_scaler", "staging")
    other_scaler = mc.download_scaler(station_name, "other_scaler", "staging")

    #dowload for produciton 
    prod_model = mc.download_model(station_name, "production")
    prod_stands_scaler = mc.download_scaler(station_name, "stands_scaler", "production")
    prod_other_scaler = mc.download_scaler(station_name, "other_scaler", "production")

    
    if model is None or stands_scaler is None or other_scaler is None:
        print(f"Model or scaler was not downloaded properly. Skipping {station_name}")
        mlflow.end_run()
        return

    if prod_model is None or prod_stands_scaler is None or prod_other_scaler is None:
        mc.prod_model_save(station_name)
        print(f"Production model does not exist. Replacing with latest staging model. Skipping evaluation.")
        mlflow.end_run()
        return

    learn_features, all_data, pipeline = pld.prepare_data(data_path)
    mc.save_pipline(pipeline, station_name)


    stands_data = np.array(learn_features[:, 0])
    stands_normalized = stands_scaler.transform(stands_data.reshape(-1, 1))
    prod_stands_normalized = prod_stands_scaler.transform(stands_data.reshape(-1, 1))



    other_data = np.array(learn_features[:, 1:])
    other_normalized = other_scaler.transform(other_data)
    prod_other_normalized = prod_other_scaler.transform(other_data)



    data_normalized = np.column_stack([stands_normalized, other_normalized])
    prod_data_normalized = np.column_stack([prod_stands_normalized, prod_other_normalized])

    
    look_back = windowsize
    step = 1


    X_final, y_final = tm.create_multivariate_dataset_with_steps(data_normalized, look_back, step)
    prod_X_final, prod_y_final = tm.create_multivariate_dataset_with_steps(prod_data_normalized, look_back, step)


    X_final = X_final.reshape(X_final.shape[0], X_final.shape[2], X_final.shape[1])
    prod_X_final = prod_X_final.reshape(prod_X_final.shape[0], prod_X_final.shape[2], prod_X_final.shape[1])
    
    y_test_predicitons = model.predict(X_final)
    prod_y_test_predicitons = prod_model.predict(X_final)
    

    y_test_true = stands_scaler.inverse_transform(y_final.reshape(-1, 1))
    prod_y_test_true = prod_stands_scaler.inverse_transform(prod_y_final.reshape(-1, 1))

    y_test_predicitons = stands_scaler.inverse_transform(y_test_predicitons)
    prod_y_test_predicitons = prod_stands_scaler.inverse_transform(prod_y_test_predicitons)

    
    lstm_mae_adv, lstm_mse_adv, lstm_evs_adv = calc.calculate_metrics(y_test_true, y_test_predicitons)
    prod_lstm_mae_adv, prod_lstm_mse_adv, prod_lstm_evs_adv = calc.calculate_metrics(prod_y_test_true, prod_y_test_predicitons)
    print(f"Staging Model Metrics: MAE={lstm_mae_adv}, MSE={lstm_mse_adv}, EVS={lstm_evs_adv}")
    print(f"Prod Model Metrics: MAE={prod_lstm_mae_adv}, MSE={prod_lstm_mse_adv}, EVS={prod_lstm_evs_adv}")

    mlflow.log_metric("MSE_staging", lstm_mse_adv)
    mlflow.log_metric("MAE_staging", lstm_mae_adv)
    mlflow.log_metric("EVS_staging", lstm_evs_adv)

    mlflow.log_metric("MSE_production", prod_lstm_mse_adv)
    mlflow.log_metric("MAE_production", prod_lstm_mae_adv)
    mlflow.log_metric("EVS_production", prod_lstm_evs_adv)

    tm.ensure_directory_exists('./reports/'+station_name)
    tm.save_test_metrics(lstm_mae_adv, lstm_mse_adv, lstm_evs_adv, './reports/'+station_name+'/metrics.txt')


    if prod_lstm_mse_adv > lstm_mse_adv and prod_lstm_mae_adv > lstm_mae_adv and prod_lstm_evs_adv > lstm_evs_adv:
        print("REPLACING THE MODEL")
        mc.prod_model_save(station_name)
        
    mlflow.end_run()


def main():

    for i in range(1,2):
        print("Evaluating the model for station ", i, " ------------------------------------")  
        evaluate_model("./data/processed/"+str(i)+"/station_"+str(i)+"_test.csv", "station_"+str(i), windowsize=8)

if __name__ == '__main__':
    main()