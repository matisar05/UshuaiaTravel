import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Link } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import type { Hotel } from '@/types';
import { buildHotelDetailRoute } from '@/constants/routes';

import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface HotelMapProps {
    hotels: Hotel[];
    center?: [number, number];
    zoom?: number;
}

const HotelMap = ({ 
    hotels, 
    center = [-54.8019, -68.3030],
    zoom = 13 
}: HotelMapProps) => {
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
                                        Desde {hotel.target_currency || 'ARS'} {hotel.min_price?.toLocaleString()}
                                    </p>
                                    <Link 
                                        to={buildHotelDetailRoute(hotel.id)}
                                        className="text-[10px] text-gray-500 hover:underline mt-2 block"
                                    >
                                        Ver detalles
                                    </Link>
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
