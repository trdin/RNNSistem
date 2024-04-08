import React, { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css'; // Import Leaflet CSS
import L from 'leaflet'; // Import Leaflet library

const MapWithMarkers = ({ stations }) => {


  const [map, setMap] = useState(null);

  useEffect(() => { 
    const map = L.map('map').setView([46.5547, 15.6459], 12); // Centered around Maribor


    // Add tile layer (using OpenStreetMap tiles)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
    }).addTo(map);
    setMap(map);


  }, []);

  useEffect(() => {

    
    if (!stations) return console.error('No stations data');
    stations.forEach(station => {
      L.marker([station.position.lat, station.position.lng]).addTo(map).bindPopup(station.name);
    });
  }, [stations]);

  return <div id='map' style={{ height: '400px' }}></div>;
};

export default MapWithMarkers;