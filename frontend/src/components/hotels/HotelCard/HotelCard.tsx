import { Star, MapPin, PawPrint, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Hotel } from '@/types';

interface HotelCardProps {
  hotel: Hotel;
}

export default function HotelCard({ hotel }: HotelCardProps) {
  const { 
    id, 
    name, 
    type_display, 
    location_display, 
    stars, 
    pet_friendly, 
    main_image, 
    address, 
    min_price,
    target_currency = 'ARS'
  } = hotel;

  return (
    <div className="card group overflow-hidden bg-white hover:shadow-xl transition-all duration-300">
      {/* Image */}
      <div className="relative aspect-[16/10] bg-gradient-to-br from-slate-100 to-slate-200 overflow-hidden">
        {main_image ? (
          <img
            src={main_image}
            alt={name}
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
            loading="lazy"
          />
        ) : (
          <div className="flex items-center justify-center w-full h-full">
            <MapPin className="w-12 h-12 text-slate-400" strokeWidth={1.5} />
          </div>
        )}
        
        {/* Type Badge */}
        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-md px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider text-slate-700 shadow-sm">
          {type_display}
        </div>

        {/* Pet Friendly Badge */}
        {pet_friendly && (
          <div className="absolute top-3 right-3 bg-green-500/90 backdrop-blur-md p-1.5 rounded-full text-white shadow-sm" title="Pet Friendly">
            <PawPrint className="w-3.5 h-3.5" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5 space-y-4">
        {/* Header */}
        <div className="space-y-1.5">
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-lg font-bold text-slate-900 line-clamp-1 group-hover:text-blue-600 transition-colors">
              {name}
            </h3>
            {stars > 0 && (
              <div className="flex items-center gap-0.5 shrink-0 pt-1">
                {Array.from({ length: Math.min(stars, 5) }).map((_, i) => (
                  <Star key={i} className="w-3 h-3 fill-amber-400 text-amber-400" />
                ))}
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-1.5 text-slate-500">
            <MapPin className="w-3.5 h-3.5" />
            <span className="text-xs font-medium">{location_display}</span>
          </div>
        </div>

        {/* Address */}
        {address && (
          <p className="text-sm text-slate-600 line-clamp-2 min-h-[2.5rem] leading-relaxed">
            {address}
          </p>
        )}

        {/* Footer: Price & CTA */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-100 gap-4">
          <div className="flex flex-col">
            {min_price ? (
              <>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  Desde
                </span>
                <div className="flex items-baseline gap-1">
                  <span className="text-xl font-black text-slate-900">
                    {target_currency} {Math.round(min_price).toLocaleString('es-AR')}
                  </span>
                  <span className="text-[10px] font-medium text-slate-500 uppercase">/ noche</span>
                </div>
              </>
            ) : (
              <span className="text-sm text-slate-500 italic">Consultar</span>
            )}
          </div>

          <Link
            to={`/hotels/${id}`}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-bold hover:bg-blue-700 transition-all shadow-md shadow-blue-100 hover:shadow-blue-200 active:scale-95"
          >
            Explorar
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
