import { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { ArrowLeft, MapPin, Star, Phone, Mail, Globe, Coffee, Dog, ExternalLink, Bell, TrendingDown, Zap, Clock } from 'lucide-react';
import { useHotel, usePriceComparison } from '@/hooks/useHotels';
import LoadingSpinner from '@/components/common/LoadingSpinner/LoadingSpinner';
import GoogleAdSense from '@/components/common/GoogleAdSense/GoogleAdSense';
import PriceComparisonWidget from '@/components/hotels/PriceComparisonWidget';
import type { Price } from '@/types';
import { ROUTES } from '@/constants/routes';

export default function HotelDetailPage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const { data: hotel, isLoading, isError } = useHotel(Number(id));
  const { data: priceComparison } = usePriceComparison(Number(id));

  const [alertEmail, setAlertEmail] = useState('');
  const [alertPrice, setAlertPrice] = useState('');
  const [alertSent, setAlertSent] = useState(false);
  const [alertError, setAlertError] = useState('');

  useEffect(() => {
    if (location.hash === '#precios') {
      setTimeout(() => {
        document.getElementById('precios')?.scrollIntoView({ behavior: 'smooth' });
      }, 300);
    }
  }, [location.hash, hotel]);

  const handleCreateAlert = async () => {
    if (!alertEmail || !alertPrice || !hotel) return;
    setAlertError('');
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/alerts/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hotel: hotel.id,
          user_email: alertEmail,
          target_price: Number(alertPrice),
          target_currency: 'ARS',
        }),
      });
      if (!res.ok) throw new Error('Error al crear la alerta');
      setAlertSent(true);
    } catch {
      setAlertError('No se pudo crear la alerta. Intentá de nuevo.');
    }
  };

  if (isLoading) return <LoadingSpinner size="lg" />;

  if (isError || !hotel) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Hotel no encontrado</h1>
          <Link to={ROUTES.HOTELES} className="btn-primary">
            <ArrowLeft className="w-5 h-5" />
            Volver a Hoteles
          </Link>
        </div>
      </div>
    );
  }

  const schemaOrg = {
    '@context': 'https://schema.org',
    '@type': 'Hotel',
    name: hotel.name,
    address: {
      '@type': 'PostalAddress',
      streetAddress: hotel.address,
      addressLocality: 'Ushuaia',
      addressCountry: 'AR',
    },
    starRating: hotel.stars > 0 ? { '@type': 'Rating', ratingValue: hotel.stars } : undefined,
    ...(hotel.min_price ? { priceRange: `ARS ${hotel.min_price}` } : {}),
    ...(hotel.latitude && hotel.longitude ? {
      geo: { '@type': 'GeoCoordinates', latitude: hotel.latitude, longitude: hotel.longitude },
    } : {}),
    ...(hotel.main_image ? { image: hotel.main_image } : {}),
    ...(hotel.description ? { description: hotel.description } : {}),
    petAllowed: hotel.pet_friendly || undefined,
  };

  const latestPrice = hotel.prices?.[0];
  const timeAgoText = latestPrice?.last_checked
    ? (() => {
        const diff = Date.now() - new Date(latestPrice.last_checked).getTime();
        const h = Math.floor(diff / 3600000);
        if (h < 1) return 'recién';
        if (h < 24) return `hace ${h}h`;
        return `hace ${Math.floor(h / 24)}d`;
      })()
    : null;

  return (
    <div className="min-h-screen bg-slate-900">
      <Helmet>
        <title>{hotel.name} — Ushuaia Travel | Compará Precios</title>
        <meta name="description" content={`${hotel.name} en ${hotel.address || 'Ushuaia'}. ${hotel.stars} estrellas. ${hotel.type_display}. Compará precios en Booking, Airbnb y más.${hotel.min_price ? ` Desde $${Math.round(hotel.min_price).toLocaleString('es-AR')} por noche.` : ''}`} />
        <script type="application/ld+json">{JSON.stringify(schemaOrg)}</script>
      </Helmet>

      {/* Back Button */}
      <div className="bg-slate-800 border-b border-slate-700">
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
              <img src={hotel.images[0]} alt={hotel.name} className="w-full h-full object-cover" />
            </div>
            <div className="hidden md:grid grid-rows-2 w-1/3 h-full border-l border-white/20">
              {hotel.images[1] && <div className="h-full border-b border-white/20"><img src={hotel.images[1]} alt={hotel.name} className="w-full h-full object-cover" /></div>}
              {hotel.images[2] && <div className="h-full"><img src={hotel.images[2]} alt={hotel.name} className="w-full h-full object-cover" /></div>}
            </div>
          </div>
        ) : hotel.main_image ? (
          <img src={hotel.main_image} alt={hotel.name} className="w-full h-full object-cover" />
        ) : (
          <div className="flex items-center justify-center h-full"><MapPin className="w-24 h-24 text-slate-600" /></div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent" />
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 -mt-32 relative z-10 pb-20">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Header Card */}
            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-8 shadow-xl">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h1 className="text-4xl font-bold text-white mb-3">{hotel.name}</h1>
                  <div className="flex items-center gap-4 text-slate-300">
                    <div className="flex items-center gap-2"><MapPin className="w-5 h-5" /><span>{hotel.address || hotel.location_display}</span></div>
                    {hotel.stars > 0 && <div className="flex items-center gap-1">{Array.from({ length: hotel.stars }).map((_, i) => <Star key={i} className="w-5 h-5 fill-amber-400 text-amber-400" />)}</div>}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  {hotel.type_display && <div className="badge bg-glacier-500/20 text-glacier-300 border border-glacier-500/30 text-lg px-4 py-2 rounded-full">{hotel.type_display}</div>}
                  {timeAgoText && (
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <Clock className="w-3 h-3" /> Actualizado {timeAgoText}
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-6 flex flex-wrap gap-4">
                <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${hotel.name} ${hotel.address} Ushuaia`)}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl font-medium transition border border-white/10">
                  <MapPin className="w-5 h-5" /> Ver en Google Maps
                </a>
              </div>
            </div>

            {/* Description */}
            {(hotel.description || hotel.description_short) && (
              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
                <h2 className="text-2xl font-bold text-white mb-4">Acerca del alojamiento</h2>
                <div className="text-slate-300 leading-relaxed space-y-4">
                  {hotel.description ? hotel.description.split('\n').map((p, i) => <p key={i}>{p}</p>) : <p>{hotel.description_short}</p>}
                </div>
              </div>
            )}

            {/* Amenities */}
            {((hotel.amenities && (Array.isArray(hotel.amenities) ? hotel.amenities.length > 0 : Object.keys(hotel.amenities).length > 0)) || hotel.pet_friendly) && (
              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
                <h2 className="text-2xl font-bold text-white mb-6">Comodidades</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Array.isArray(hotel.amenities) ? hotel.amenities.map((a, i) => (
                    <div key={i} className="flex items-center gap-3 text-slate-300">
                      <div className="w-10 h-10 bg-glacier-500/20 rounded-lg flex items-center justify-center"><Coffee className="w-5 h-5 text-glacier-400" /></div>
                      <span className="capitalize">{a}</span>
                    </div>
                  )) : Object.entries(hotel.amenities ?? {}).map(([k, v]) => {
                    if (!v) return null;
                    return (
                      <div key={k} className="flex items-center gap-3 text-slate-300">
                        <div className="w-10 h-10 bg-glacier-500/20 rounded-lg flex items-center justify-center"><Coffee className="w-5 h-5 text-glacier-400" /></div>
                        <span className="capitalize">{k.replace('_', ' ')}</span>
                      </div>
                    );
                  })}
                  {hotel.pet_friendly && (
                    <div className="flex items-center gap-3 text-slate-300"><div className="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center"><Dog className="w-5 h-5 text-emerald-400" /></div><span>Pet Friendly</span></div>
                  )}
                </div>
              </div>
            )}

            {/* Price Comparison */}
            <div id="precios">
              <PriceComparisonWidget
                comparison={priceComparison ?? undefined}
                prices={hotel.prices}
                hotelName={hotel.name}
              />
            </div>

            {/* Price Alert Form */}
            <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                <Bell className="w-6 h-6 text-wood-400" />
                Alerta de Precio
              </h2>
              <p className="text-slate-400 mb-6">Te avisamos cuando el precio baje de tu objetivo.</p>

              {alertSent ? (
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 text-emerald-400 font-semibold">
                  ¡Alerta creada! Te avisaremos cuando el precio baje.
                </div>
              ) : (
                <div className="flex flex-wrap gap-3 items-end">
                  <div className="flex-1 min-w-[200px]">
                    <label className="text-xs text-slate-400 mb-1 block">Tu email</label>
                    <input type="email" value={alertEmail} onChange={(e) => setAlertEmail(e.target.value)} placeholder="tu@email.com" className="w-full bg-white/10 text-white placeholder-white/40 px-4 py-3 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-wood-500" />
                  </div>
                  <div className="w-40">
                    <label className="text-xs text-slate-400 mb-1 block">Precio objetivo ($)</label>
                    <input type="number" value={alertPrice} onChange={(e) => setAlertPrice(e.target.value)} placeholder="50000" className="w-full bg-white/10 text-white placeholder-white/40 px-4 py-3 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-wood-500" />
                  </div>
                  <button onClick={handleCreateAlert} className="bg-gradient-to-r from-wood-500 to-wood-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-wood-500/50 transition">
                    Crear Alerta
                  </button>
                </div>
              )}
              {alertError && <p className="text-red-400 mt-3 text-sm">{alertError}</p>}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {hotel.contact_info && Object.keys(hotel.contact_info).length > 0 && (
              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 sticky top-24">
                <h3 className="text-xl font-bold text-white mb-4">Contacto</h3>
                <div className="space-y-4">
                  {hotel.contact_info.phone && <a href={`tel:${hotel.contact_info.phone}`} className="flex items-center gap-3 text-slate-300 hover:text-white transition"><Phone className="w-5 h-5" /><span>{hotel.contact_info.phone}</span></a>}
                  {hotel.contact_info.email && <a href={`mailto:${hotel.contact_info.email}`} className="flex items-center gap-3 text-slate-300 hover:text-white transition"><Mail className="w-5 h-5" /><span>{hotel.contact_info.email}</span></a>}
                  {hotel.contact_info.website && <a href={hotel.contact_info.website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 text-slate-300 hover:text-white transition"><Globe className="w-5 h-5" /><span>Sitio Web</span></a>}
                </div>
              </div>
            )}
            <GoogleAdSense slot="0987654321" format="vertical" />
          </div>
        </div>
      </div>
    </div>
  );
}
