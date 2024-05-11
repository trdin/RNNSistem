print("################--STARTING THE SERVE SCRIPT--#################")


print("Importing Flask, request, jsonify from flask")
from flask import Flask, request, jsonify
print("Importing CORS from flask_cors")
from flask_cors import CORS
print("Importing os")
import os
print("Importing predict from src.models")
import src.models.predict as pred
print("Importing mlflow_client from src.models")
import src.models.mlflow_client as mc
print("Importing joblib")
import joblib
print("Importing settings from src")
import src.settings as settings
print("Importing mlflow")
import mlflow
print("Importing auth and dagshub from dagshub")
import dagshub.auth
import dagshub
print("Importing connector from src.database")
import src.database.connector as db
print("Importing datetime")
import datetime



def dowload_models():
    print("###############--Downloading models--##############")
    for i in range(1, 2):
        station_dir = f"models/station_{i}/"
        os.makedirs(station_dir, exist_ok=True)
        model = mc.download_model_onnx("station_" + str(i), "production")
        stands_scaler = mc.download_scaler("station_" + str(i), "stands_scaler", "production")
        other_scaler = mc.download_scaler("station_" + str(i), "other_scaler", "production")

        joblib.dump(stands_scaler, os.path.join(station_dir, 'stands_scaler.joblib'))
        joblib.dump(other_scaler, os.path.join(station_dir, 'other_scaler.joblib'))
        

def predict(data):
    try:
        required_features = ['date','available_bike_stands', 'temperature', 'relative_humidity',
             'apparent_temperature', 'dew_point', 'precipitation_probability',
               'surface_pressure']
        for obj in data:
            for feature in required_features:
                if feature not in obj:
                    return {'error': f'Missing feature: {feature}'}, 400

        prediction = pred.predict(data)

        return {'prediction': prediction.tolist()}
    except Exception as e:
        return {'error': str(e)}, 400

app = Flask(__name__)
CORS(app) 

@app.route('/predict', methods=['POST'])
def predict_air():
    data = request.get_json()
    result = predict(data)
    return jsonify(result)

@app.route('/predict/<int:station_id>', methods=['GET'])
def get_model(station_id):

    predictions = pred.predict_station(station_name="station_"+str(station_id), station_number=station_id, windowsize=8)
    db.insert_prediciton(f"station_{station_id}", {'predictions': predictions, "date": datetime.datetime.now()})
    return jsonify({'predictions': predictions})

    
    


def main():
    print("###############--Starting server--##############")
    dagshub.auth.add_app_token(token=settings.mlflow_tracking_password)
    dagshub.init("RNNSistem", settings.mlflow_tracking_username, mlflow=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    dowload_models()

    app.run(host='0.0.0.0', port=3001)

if __name__ == '__main__':
    main()
    


