from flask import Flask, request, jsonify
from flask_cors import CORS
import src.models.predict as pred


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
    return jsonify({'predictions': pred.predict_station(station_name="station_"+str(station_id), station_number=station_id, windowsize=8)})

    
    


def main():
    app.run(host='0.0.0.0', port=3001)

if __name__ == '__main__':
    main()
    


