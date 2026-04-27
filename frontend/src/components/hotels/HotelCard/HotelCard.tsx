import { Star, MapPin, PawPrint, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Hotel } from '@/types';

interface HotelCardProps {
  hotel: Hotel;
}

export default function HotelCard({ hotel }: HotelCardProps) {
  const { name, type_display, location_display, stars, pet_friendly, main_image, address, min_price } = hotel;

  return (
    <div className="card group overflow-hidden">
      {/* Image */}
      <div className="relative aspect-[16/10] bg-gradient-to-br from-slate-100 to-slate-200 overflow-hidden">
        {main_image ? (
          <img
            src={main_image}
            alt={name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            loading="lazy"
          />
        ) : (
          <div className="flex items-center justify-center w-full h-full">
            <MapPin className="w-12 h-12 text-slate-400" strokeWidth={1.5} />
          </div>
        )}
        
        {/* Pet Friendly Badge */}
        {pet_friendly && (
          <div className="absolute top-3 right-3 badge-success bg-white/95 backdrop-blur-sm shadow-sm">
            <PawPrint className="w-3 h-3" />
            <span>Pet friendly</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-6 space-y-4">
        {/* Header */}
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-slate-900 line-clamp-2">
            {name}
          </h3>
          
          {/* Stars */}
          {stars > 0 && (
            <div className="flex items-center gap-1">
              {Array.from({ length: stars }).map((_, i) => (
                <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
              ))}
            </div>
          )}
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2">
          <span className="badge badge-primary">{type_display}</span>
          <span className="badge bg-slate-100 text-slate-700">{location_display}</span>
        </div>

        {/* Address */}
        {address && (
          <p className="text-sm text-slate-600 line-clamp-2">{address}</p>
        )}

        {/* Footer: Price & CTA */}
        <div className="flex items-end justify-between pt-4 border-t border-slate-100 gap-4">
          <div className="flex flex-col">
            {min_price ? (
              <>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Desde
                </span>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-bold text-slate-900">
                    ${min_price.toLocaleString('es-AR')}
                  </span>
                  <span className="text-xs text-slate-500">/ noche</span>
                </div>
              </>
            ) : (
              <span className="text-sm text-slate-500 italic">Consultar precio</span>
            )}
          </div>

          <Link
            to={`/hotel/${hotel.id}`}
            className="flex items-center gap-2 bg-slate-900 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-800 transition shadow-sm hover:shadow-md active:scale-95"
          >
            Ver detalles
            <ExternalLink className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
