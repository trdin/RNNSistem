import React, { useState, useEffect } from "react";

const BikeStationList = () => {
  const [stations, setStations] = useState([]);
  const [selectedStation, setSelectedStation] = useState(null);

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

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-1/2 h-full overflow-y-auto p-4">
        <h1 className="text-3xl font-bold underline mb-4">Bike Stations in Maribor</h1>
        <div className="grid grid-cols-1 gap-4">
          {stations.map((station) => (
            <div key={station.number} className="bg-white p-4 rounded-md cursor-pointer shadow-md hover:shadow-lg" onClick={() => handleClick(station)}>
              <h2 className="text-lg font-semibold mb-2">{station.name}</h2>
              <p className="text-gray-600 mb-2">{station.address}</p>
              <p className="text-gray-600 mb-2">Available Bikes: {station.available_bikes}</p>
              <p className="text-gray-600 mb-2">Available Bike Stands: {station.available_bike_stands}</p>
              <p className="text-gray-600">Status: {station.status}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="w-1/2 bg-white p-4">
        {selectedStation && (
          <div>
            <h1 className="text-3xl font-bold underline mb-4">{selectedStation.name}</h1>
            <p className="text-gray-600 mb-2">{selectedStation.address}</p>
            <p className="text-gray-600 mb-2">Available Bikes: {selectedStation.available_bikes}</p>
            <p className="text-gray-600 mb-2">Available Bike Stands: {selectedStation.available_bike_stands}</p>
            <p className="text-gray-600">Status: {selectedStation.status}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BikeStationList;
