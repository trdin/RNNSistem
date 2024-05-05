import React, { useState, useEffect } from "react";

const BikeStationList = () => {
  const [stations, setStations] = useState([]);
  const [selectedStation, setSelectedStation] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [currentHour, setCurrentHour] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(
      "https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey=5e150537116dbc1786ce5bec6975a8603286526b"
    )
      .then((response) => response.json())
      .then((data) => setStations(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  const handleClick = (station) => {
    setSelectedStation(station);
  };

  const getCurrentHour = () => {
    const now = new Date();
    return now.getHours();
  };

  const generateHourLabels = () => {
    const labels = [];
    let hour = currentHour;
    for (let i = 0; i < predictions.length; i++) {
      hour++;
      labels.push((hour % 24) + ":00");
    }
    return labels;
  };

  useEffect(() => {
    if (selectedStation != null) {
      setLoading(true); // Set loading to true when fetching predictions
      fetch(`${process.env.REACT_APP_API_URL}/predict/${selectedStation.number}`)
        .then((response) => response.json())
        .then((data) => {
          const roundedPredictions = data.predictions.map((prediction) =>
            Math.round(prediction)
          );
          setPredictions(roundedPredictions);
        })
        .catch((error) => console.error("Error fetching data:", error))
        .finally(() => {
          setLoading(false); // Set loading to false after predictions are fetched
        });

      setCurrentHour(getCurrentHour());
    }
  }, [selectedStation]);

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-1/2 h-full overflow-y-auto p-4">
        <h1 className="text-3xl font-bold underline mb-4">
          Bike Stations in Maribor
        </h1>
        <div className="grid grid-cols-1 gap-4">
          {stations.map((station) => (
            <div
              key={station.number}
              className="bg-white p-4 rounded-md cursor-pointer shadow-md hover:shadow-lg"
              onClick={() => handleClick(station)}
            >
              <h2 className="text-lg font-semibold mb-2">{station.name}</h2>
              <p className="text-gray-600 mb-2">{station.address}</p>
              <p className="text-gray-600 mb-2">
                Available Bikes: {station.available_bikes}
              </p>
              <p className="text-gray-600 mb-2">
                Available Bike Stands: {station.available_bike_stands}
              </p>
              <p className="text-gray-600">Status: {station.status}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="w-1/2 bg-white p-4">
        {selectedStation && (
          <div>
            <h1 className="text-3xl font-bold underline mb-4">
              {selectedStation.name}
            </h1>
            <p className="text-gray-600 mb-2">{selectedStation.address}</p>
            <p className="text-gray-600 mb-2">
              Available Bikes: {selectedStation.available_bikes}
            </p>
            <p className="text-gray-600 mb-2">
              Available Bike Stands: {selectedStation.available_bike_stands}
            </p>
            <p className="text-gray-600">Status: {selectedStation.status}</p>
            <div>
              <p className="text-lg font-bold mb-2">Napovedi:</p>
              {loading ? ( // Render loading text and animation while predictions are loading
                <div className="animate-pulse text-gray-600">
                  Loading predictions...
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="table-auto border-collapse border border-gray-400">
                    <thead>
                      <tr>
                        {generateHourLabels().map((label, index) => (
                          <th
                            key={index}
                            className="p-2 border border-gray-400"
                          >
                            {label}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        {predictions.map((prediction, index) => (
                          <td
                            key={index}
                            className="p-2 border border-gray-400 text-gray-600"
                          >
                            {prediction}
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BikeStationList;
