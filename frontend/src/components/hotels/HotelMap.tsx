import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in Leaflet with React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface Hotel {
    id: number;
    name: string;
    latitude: number;
    longitude: number;
    min_price: number;
    target_currency: string;
}

interface HotelMapProps {
    hotels: Hotel[];
    center?: [number, number];
    zoom?: number;
}

const HotelMap: React.FC<HotelMapProps> = ({ 
    hotels, 
    center = [-54.8019, -68.3030], // Ushuaia Center
    zoom = 13 
}) => {
    return (
        <div className="h-[400px] w-full rounded-xl overflow-hidden shadow-lg border border-gray-200">
            <MapContainer 
                center={center} 
                zoom={zoom} 
                scrollWheelZoom={false}
                className="h-full w-full"
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {hotels.map((hotel) => (
                    hotel.latitude && hotel.longitude && (
                        <Marker 
                            key={hotel.id} 
                            position={[hotel.latitude, hotel.longitude]}
                        >
                            <Popup>
                                <div className="p-1">
                                    <h3 className="font-bold text-sm">{hotel.name}</h3>
                                    <p className="text-xs text-blue-600 mt-1">
                                        Desde {hotel.target_currency} {hotel.min_price?.toLocaleString()}
                                    </p>
                                    <a 
                                        href={`/hotels/${hotel.id}`}
                                        className="text-[10px] text-gray-500 hover:underline mt-2 block"
                                    >
                                        Ver detalles
                                    </a>
                                </div>
                            </Popup>
                        </Marker>
                    )
                ))}
            </MapContainer>
        </div>
    );
};

export default HotelMap;
