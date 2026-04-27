import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, MapPin, Star, Phone, Mail, Globe, Wifi, Car, Coffee, Wind, Dog, ExternalLink } from 'lucide-react';
import { useHotel, usePriceComparison } from '@/hooks/useHotels';
import LoadingSpinner from '@/components/common/LoadingSpinner/LoadingSpinner';

export default function HotelDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: hotel, isLoading, isError } = useHotel(Number(id));
  const { data: priceComparison } = usePriceComparison(Number(id));

  if (isLoading) return <LoadingSpinner />;
  
  if (isError || !hotel) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Hotel no encontrado</h1>
          <Link to="/hoteles" className="btn-primary">
            <ArrowLeft className="w-5 h-5" />
            Volver a Hoteles
          </Link>
        </div>
      </div>
    );
  }

  const amenityIcons: Record<string, any> = {
    wifi: Wifi,
    estacionamiento: Car,
    desayuno: Coffee,
    aire_acondicionado: Wind,
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Sticky Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-lg shadow-xl border-b border-slate-800">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-3">
              <MapPin className="w-8 h-8 text-glacier-400" strokeWidth={2} />
              <span className="text-2xl font-bold text-white">Ushuaia Travel</span>
            </Link>
            <div className="hidden md:flex items-center gap-6">
              <Link to="/" className="text-white/90 hover:text-white font-medium transition">Inicio</Link>
              <Link to="/hoteles" className="text-white/90 hover:text-white font-medium transition">Hoteles</Link>
              <Link 
                to="/donar"
                className="bg-gradient-to-r from-wood-500 to-wood-600 text-white px-6 py-2 rounded-xl font-semibold hover:shadow-lg hover:shadow-wood-500/50 transition"
              >
                Apoyar
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Back Button Section */}
      <div className="bg-slate-800 border-b border-slate-700 pt-20">
        <div className="container mx-auto px-6 py-4">
          <button 
            onClick={() => window.history.back()}
            className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition"
          >
            <ArrowLeft className="w-5 h-5" />
            Volver a resultados
          </button>
        </div>
      </div>

      {/* Hero Gallery */}
      <div className="relative h-96 bg-gradient-to-br from-slate-700 to-slate-800 overflow-hidden">
        {hotel.images && hotel.images.length > 0 ? (
          <div className="flex h-full">
            <div className="w-full md:w-2/3 h-full">
              <img 
                src={hotel.images[0]} 
                alt={hotel.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="hidden md:grid grid-rows-2 w-1/3 h-full border-l border-white/20">
              {hotel.images[1] && (
                <div className="h-full border-b border-white/20">
                    <img src={hotel.images[1]} alt={hotel.name} className="w-full h-full object-cover" />
                </div>
              )}
              {hotel.images[2] && (
                <div className="h-full">
                    <img src={hotel.images[2]} alt={hotel.name} className="w-full h-full object-cover" />
                </div>
              )}
            </div>
          </div>
        ) : hotel.main_image ? (
          <img 
            src={hotel.main_image} 
            alt={hotel.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <MapPin className="w-24 h-24 text-slate-600" />
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 -mt-32 relative z-10 pb-20">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-8">
            {/* Header Card */}
            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-8 shadow-xl">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-4xl font-bold text-white mb-3">{hotel.name}</h1>
                  <div className="flex items-center gap-4 text-slate-300">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-5 h-5" />
                      <span>{hotel.address || hotel.location_display}</span>
                    </div>
                    {hotel.stars > 0 && (
                      <div className="flex items-center gap-1">
                        {Array.from({ length: hotel.stars }).map((_, i) => (
                          <Star key={i} className="w-5 h-5 fill-amber-400 text-amber-400" />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                {hotel.type_display && (
                    <div className="badge bg-glacier-500/20 text-glacier-300 border border-glacier-500/30 text-lg px-4 py-2 rounded-full">
                    {hotel.type_display}
                    </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-6 flex flex-wrap gap-4">
                 <a 
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${hotel.name} ${hotel.address} Ushuaia`)}`}
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl font-medium transition border border-white/10"
                  >
                    <MapPin className="w-5 h-5" />
                    Ver en Google Maps
                 </a>
              </div>
            </div>

            {/* Description */}
            {(hotel.description || hotel.description_short) && (
              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
                <h2 className="text-2xl font-bold text-white mb-4">Acerca del alojamiento</h2>
                <div className="text-slate-300 leading-relaxed space-y-4">
                    {hotel.description ? (
                         hotel.description.split('\n').map((paragraph: string, i: number) => (
                            <p key={i}>{paragraph}</p>
                        ))
                    ) : (
                        <p>{hotel.description_short}</p>
                    )}
                </div>
              </div>
            )}

            {/* Amenities */}
            {((hotel.amenities && (Array.isArray(hotel.amenities) ? hotel.amenities.length > 0 : Object.keys(hotel.amenities).length > 0)) || hotel.pet_friendly) && (
              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
                <h2 className="text-2xl font-bold text-white mb-6">Comodidades</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {/* Handle both array (new scraper) and object (legacy) formats */}
                  {Array.isArray(hotel.amenities) ? (
                      hotel.amenities.map((amenity: string, i: number) => (
                        <div key={i} className="flex items-center gap-3 text-slate-300">
                            <div className="w-10 h-10 bg-glacier-500/20 rounded-lg flex items-center justify-center">
                                <Coffee className="w-5 h-5 text-glacier-400" />
                            </div>
                            <span className="capitalize">{amenity}</span>
                        </div>
                      ))
                  ) : (
                      Object.entries(hotel.amenities || {}).map(([key, value]) => {
                        if (!value) return null;
                        const Icon = amenityIcons[key] || Coffee;
                        return (
                          <div key={key} className="flex items-center gap-3 text-slate-300">
                            <div className="w-10 h-10 bg-glacier-500/20 rounded-lg flex items-center justify-center">
                              <Icon className="w-5 h-5 text-glacier-400" />
                            </div>
                            <span className="capitalize">{key.replace('_', ' ')}</span>
                          </div>
                        );
                      })
                  )}
                  
                  {hotel.pet_friendly && (
                    <div className="flex items-center gap-3 text-slate-300">
                      <div className="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
                        <Dog className="w-5 h-5 text-emerald-400" />
                      </div>
                      <span>Pet Friendly</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Price Comparison */}
            {priceComparison && (
              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
                <h2 className="text-2xl font-bold text-white mb-6">Comparación de Precios</h2>
                <div className="space-y-4">
                  {Object.entries(priceComparison.comparison).map(([platform, prices]) => (
                    prices.map((price: any) => (
                      <div key={price.id} className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="text-xl font-semibold text-white mb-1 capitalize">{platform}</h3>
                            {price.room_type && (
                              <p className="text-slate-400 text-sm">{price.room_type} · {price.max_guests} huéspedes</p>
                            )}
                          </div>
                          <div className="text-right">
                            <div className="text-3xl font-bold text-white">
                              ${price.price_per_night.toLocaleString('es-AR')}
                            </div>
                            <div className="text-sm text-slate-400">{price.currency} / noche</div>
                          </div>
                        </div>
                        {price.platform_url && (
                          <a
                            href={price.platform_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-4 inline-flex items-center gap-2 text-glacier-400 hover:text-glacier-300 transition"
                          >
                            Ver en {platform}
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    ))
                  ))}
                  {priceComparison.cheapest && (
                    <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
                      <p className="text-emerald-400 font-semibold">
                        💡 Mejor precio: ${priceComparison.cheapest.price_per_night.toLocaleString('es-AR')} en {priceComparison.cheapest.platform}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Contact Card */}
            {hotel.contact_info && Object.keys(hotel.contact_info).length > 0 && (
              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 sticky top-24">
                <h3 className="text-xl font-bold text-white mb-4">Contacto</h3>
                <div className="space-y-4">
                  {hotel.contact_info.phone && (
                    <a href={`tel:${hotel.contact_info.phone}`} className="flex items-center gap-3 text-slate-300 hover:text-white transition">
                      <Phone className="w-5 h-5" />
                      <span>{hotel.contact_info.phone}</span>
                    </a>
                  )}
                  {hotel.contact_info.email && (
                    <a href={`mailto:${hotel.contact_info.email}`} className="flex items-center gap-3 text-slate-300 hover:text-white transition">
                      <Mail className="w-5 h-5" />
                      <span>{hotel.contact_info.email}</span>
                    </a>
                  )}
                  {hotel.contact_info.website && (
                    <a href={hotel.contact_info.website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 text-slate-300 hover:text-white transition">
                      <Globe className="w-5 h-5" />
                      <span>Sitio Web</span>
                    </a>
                  )}
                </div>
              </div>
            )}


          </div>
        </div>
      </div>
    </div>
  );
}
