
import mlflow
import dagshub.auth
import dagshub
import src.settings as settings

import src.database.connector as db
import os
import pandas as pd
from datetime import timedelta
from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score


def predictions_test(station_name, station_data):
    

    predictions_data = db.preditcions_today(station_name)

    if not predictions_data:
        print("No predictions for today for station ", station_name)
        mlflow.end_run()
        return
    mlflow.start_run(run_name=station_name, experiment_id="2")

    #station_data = station_data.set_index(['date'])
    mapped_predictions = []
    for pred_obj in predictions_data:
        predictions_hourly = pred_obj['predictions']
        date = pd.to_datetime(pred_obj['date'])
        station_data.reset_index(inplace=True)
        station_data = station_data.set_index(['date'])
        for i, pred in enumerate(predictions_hourly):
            target_time= date + timedelta(hours=i)
            nearest_timestamp_index = station_data.index.get_indexer(
                [target_time],
                method='nearest'
            )[0]

            
            row_with_nearest_timestamp = station_data.iloc[nearest_timestamp_index].to_dict()

            # Append the mapped prediction to the list
            mapped_predictions.append({
                'date': target_time,
                'prediction': pred,
                'true': row_with_nearest_timestamp['available_bike_stands']
            })


    y_true = [x['true'] for x in mapped_predictions]
    y_pred = [x['prediction'] for x in mapped_predictions]

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    evs = explained_variance_score(y_true, y_pred)

    # Save the result into mlflow as an experiment
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("evs", evs)

    mlflow.end_run()

def main():
    dagshub.auth.add_app_token(token=settings.mlflow_tracking_password)
    dagshub.init("RNNSistem", settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    
    
    for i in range(1,30):
        print("Testing model for station ", i, " ------------------------------------")  

        station_data = pd.read_csv(os.path.join(f"./data/processed/{i}/" f"station_{i}.csv"))

        station_data['date'] = pd.to_datetime(station_data['date'])
        station_data.sort_values(by='date', inplace=True)
        station_data.drop_duplicates('date', inplace=True)
        station_data.reset_index(inplace=True)
        station_data = station_data.set_index(['date'])

        predictions_test("station_"+str(i), station_data)

        

if __name__ == '__main__':
    main()