# %%
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense 
from tensorflow.keras.models import Sequential
import joblib
import src.data.prepare_learn_data as pld
import src.helpers.calculate as calc
import src.visualization.visualization as vis

def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(units=32, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(units=32))
    model.add(Dense(units=16, activation='relu'))
    model.add(Dense(units=1))
    return model

def train_model(model, X_train, y_train, epochs=50):
    model.compile(optimizer='adam', loss='mean_squared_error')
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=32, validation_split=0.2, verbose=1)
    vis.plot_model_history(history)
    # Izris zgodovine učenja

def create_multivariate_dataset_with_steps(time_series, look_back=1, step=1):
    X, y = [], []
    for i in range(0, len(time_series) - look_back, step):
        X.append(time_series[i:(i + look_back), :])
        y.append(time_series[i + look_back, 0]) 
    return np.array(X), np.array(y)

   

def main():

    learn_features, all_data = pld.prepare_data()

    train_size = len(learn_features) - 384 - 48
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

    
    look_back = 48
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

    lstm_model_adv = build_lstm_model(input_shape)
    train_model(lstm_model_adv, X_train, y_train, epochs=30)

    y_test_pred_lstm_adv = lstm_model_adv.predict(X_test)

    y_test_true = stands_scaler.inverse_transform(y_test.reshape(-1, 1))

    y_test_pred_lstm_adv = stands_scaler.inverse_transform(y_test_pred_lstm_adv)

    
    lstm_mae_adv, lstm_mse_adv, lstm_evs_adv = calc.calculate_metrics(y_test_true, y_test_pred_lstm_adv)
    print("\nLSTM Model Metrics:")
    print(f"MAE: {lstm_mae_adv}, MSE: {lstm_mse_adv}, EVS: {lstm_evs_adv}")

    dates = all_data['date'][:-look_back][-len(y_test):]
    train_dates =  all_data['date'][:len(train_data)]


    print(dates.shape)
    # Function to plot a comparison between actual values and predictions for a given model
    
    vis.plot_comparison(
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
    )

    lstm_model_final = build_lstm_model(input_shape)
    train_model(lstm_model_final, X_final, y_final, epochs=30)

    lstm_model_final.save("./models/lstm_model_final.h5")

    joblib.dump(stands_scaler, './models/scalers/stands_scaler.joblib')
    joblib.dump(other_scaler, './models/scalers/other_scaler.joblib')


if __name__ == '__main__':
    main()