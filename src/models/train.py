# %%
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow
from tensorflow.keras.layers import LSTM, Dense 
from tensorflow.keras.models import Sequential
import joblib
import src.data.prepare_learn_data as pld
import src.helpers.calculate as calc
import src.visualization.visualization as vis
import os
import mlflow
import dagshub.auth
import dagshub
from mlflow import MlflowClient
from mlflow.onnx import log_model as log_onnx_model
import src.models.mlflow_client as mc


import src.settings as settings


def save_train_metrics(history, file_path):
    with open(file_path, 'w') as file:
        file.write("Epoch\tTrain Loss\tValidation Loss\n")
        for epoch, (train_loss, val_loss) in enumerate(zip(history.history['loss'], history.history['val_loss']), start=1):
            file.write(f"{epoch}\t{train_loss}\t{val_loss}\n")

def save_test_metrics(mae, mse, evs, file_path):
    with open(file_path, 'w') as file:
        file.write("Model Metrics\n")
        file.write(f"MAE: {mae}\n")
        file.write(f"MSE: {mse}\n")
        file.write(f"EVS: {evs}\n")

def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=32, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(units=32))
    model.add(Dense(units=16, activation='relu'))
    model.add(Dense(units=1))

    return model

def train_model(model, X_train, y_train, epochs=50, station_name = "default", batch_size=32):
    model.compile(optimizer='adam', loss='mean_squared_error')
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.2, verbose=1)
    vis.plot_model_history(history)
    save_train_metrics(history, "./reports/"+station_name+"/train_metrics.txt")

def create_multivariate_dataset_with_steps(time_series, look_back=1, step=1):
    X, y = [], []
    for i in range(0, len(time_series) - look_back, step):
        X.append(time_series[i:(i + look_back), :])
        y.append(time_series[i + look_back, 0]) 
    return np.array(X), np.array(y)


def copy_station_names_to_file(data):
    try:
        for station in data:
            source_filename = 'data/processed/' + station['name'] + '.csv'
            destination_filename = 'data/processed/' + station['number'] + '.csv'
            if os.path.exists(source_filename):
                os.rename(source_filename, destination_filename)
            else:
                print(f"Source file {source_filename} does not exist.")
    except Exception as e:
        print(f"An error occurred while copying station files: {e}")





    
   
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def train(data_path, station_name, test = False,windowsize = 24, test_size_multiplier = 10):

    dagshub.auth.add_app_token(token=settings.mlflow_tracking_password)
    dagshub.init("RNNSistem", settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    client = MlflowClient()
    
    mlflow.start_run(run_name=station_name, experiment_id="1")
    
    mlflow.tensorflow.autolog()

    learn_features, all_data, pipeline = pld.prepare_data(data_path)

    mc.save_pipline(pipeline, station_name, client)
    train_size = len(learn_features) - windowsize * test_size_multiplier
    train_data, test_data = learn_features[:train_size], learn_features[train_size:]


    print(train_data.shape, test_data.shape)

    train_stands = np.array(train_data[:,0])
    test_stands = np.array(test_data[:,0])
    
    stands_scaler = MinMaxScaler()
    train_stands_normalized = stands_scaler.fit_transform(train_stands.reshape(-1, 1))
    test_stands_normalized = stands_scaler.transform(test_stands.reshape(-1, 1))

    train_final_stands = np.array(learn_features[:, 0])
    train_final_stands_normalized = stands_scaler.fit_transform(train_final_stands.reshape(-1, 1))

    train_other = np.array(train_data[:,1:])
    test_other = np.array(test_data[:,1:])
    other_scaler = MinMaxScaler()
    train_other_normalized = other_scaler.fit_transform(train_other)
    test_other_normalized = other_scaler.transform(test_other)

    train_final_other = np.array(learn_features[:, 1:])
    train_final_other_normalized = other_scaler.fit_transform(train_final_other)


    train_normalized = np.column_stack([train_stands_normalized, train_other_normalized])
    test_normalized = np.column_stack([test_stands_normalized, test_other_normalized])

    train_final_normalized = np.column_stack([train_final_stands_normalized, train_final_other_normalized])

    
    look_back = windowsize
    step = 1

    X_train, y_train = create_multivariate_dataset_with_steps(train_normalized, look_back, step)
    X_test, y_test = create_multivariate_dataset_with_steps(test_normalized, look_back, step)

    X_final, y_final = create_multivariate_dataset_with_steps(train_final_normalized, look_back, step)

    X_train = X_train.reshape(X_train.shape[0], X_train.shape[2], X_train.shape[1])
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[2], X_test.shape[1])

    X_final = X_final.reshape(X_final.shape[0], X_final.shape[2], X_final.shape[1])


    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    

    input_shape = (X_train.shape[1], X_train.shape[2])

    if(test):
        lstm_model_adv = build_lstm_model(input_shape)
        train_model(lstm_model_adv, X_train, y_train, epochs=30)




        y_test_pred_lstm_adv = lstm_model_adv.predict(X_test)

        y_test_true = stands_scaler.inverse_transform(y_test.reshape(-1, 1))

        y_test_pred_lstm_adv = stands_scaler.inverse_transform(y_test_pred_lstm_adv)

        
        lstm_mae_adv, lstm_mse_adv, lstm_evs_adv = calc.calculate_metrics(y_test_true, y_test_pred_lstm_adv)
        print("\nLSTM Model Metrics:")
        print(f"MAE: {lstm_mae_adv}, MSE: {lstm_mse_adv}, EVS: {lstm_evs_adv}")
        ensure_directory_exists('./reports/'+station_name)
        save_test_metrics(lstm_mae_adv, lstm_mse_adv, lstm_evs_adv, './reports/'+station_name+'/metrics.txt')
        dates = all_data['date'][:-look_back][-len(y_test):]
        train_dates =  all_data['date'][:len(train_data)]


        print(dates.shape)
    
    # Function to plot a comparison between actual values and predictions for a given model
    
    """ vis.plot_comparison(
        train_dates,
        train_data[:,0],
        dates,
        y_test_true,
        y_test_pred_lstm_adv,
        'LSTM',
        'blue',
        'orange',
        lstm_mae_adv,
        lstm_mse_adv,
        lstm_evs_adv
    ) """


    lstm_model_final = build_lstm_model(input_shape)

    epochs = 10
    batch_size = 32


    train_model(lstm_model_final, X_final, y_final, epochs=10, batch_size=32)

    mc.mlflow_save_scaler(client, "stands_scaler", stands_scaler, station_name)
    mc.mlflow_save_scaler(client, "other_scaler", other_scaler, station_name)


    mlflow.log_param("epochs", epochs)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("train_dataset_size", len(train_data))
    mc.mlflow_save_model(lstm_model_final, station_name, client)



    
    



    station_directory = './models/' + station_name
    ensure_directory_exists(station_directory)

    """ lstm_model_final.save(os.path.join(station_directory, 'model.h5'))

    joblib.dump(stands_scaler, os.path.join(station_directory, 'stands_scaler.joblib'))
    joblib.dump(other_scaler, os.path.join(station_directory, 'other_scaler.joblib')) """

    mlflow.end_run()



def main():
    train("./data/raw/mbajk_dataset.csv", "default", True)

if __name__ == '__main__':
    main()