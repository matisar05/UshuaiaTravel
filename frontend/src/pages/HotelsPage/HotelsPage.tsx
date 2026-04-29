import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Search, Filter, Star, MapPin, DollarSign, Home, ArrowLeft } from 'lucide-react';
import { useHotels } from '@/hooks/useHotels';
import HotelCard from '@/components/hotels/HotelCard/HotelCard';
import { HotelGridSkeleton } from '@/components/common/Skeleton/Skeleton';
import type { HotelFilters } from '@/types';
import { ROUTES } from '@/constants/routes';
import { IMAGES } from '@/constants/images';
import GoogleAdSense from '@/components/common/GoogleAdSense/GoogleAdSense';

export default function HotelsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Parse initial filters from URL
  const initialFilters: HotelFilters = {
    search: searchParams.get('search') || '',
    min_price: searchParams.get('min_price') ? Number(searchParams.get('min_price')) : undefined,
    max_price: searchParams.get('max_price') ? Number(searchParams.get('max_price')) : undefined,
    min_stars: searchParams.get('min_stars') ? Number(searchParams.get('min_stars')) : undefined,
    location_type: searchParams.get('location_type') as HotelFilters['location_type'] || undefined,
    hotel_type: searchParams.get('hotel_type') as HotelFilters['hotel_type'] || undefined,
    pet_friendly: searchParams.get('pet_friendly') === 'true' ? true : undefined,
    page: searchParams.get('page') ? Number(searchParams.get('page')) : 1,
    checkin: searchParams.get('checkin') || undefined,
    checkout: searchParams.get('checkout') || undefined,
    guests: searchParams.get('guests') ? Number(searchParams.get('guests')) : undefined,
  };

  const [showFilters, setShowFilters] = useState(true);
  const [filters, setFilters] = useState<HotelFilters>(initialFilters);
  
  const [searchTerm, setSearchTerm] = useState(initialFilters.search || '');
  const [checkin, setCheckin] = useState(initialFilters.checkin || '');
  const [checkout, setCheckout] = useState(initialFilters.checkout || '');
  const [guests, setGuests] = useState<number | undefined>(initialFilters.guests);

  const updateUrl = (newFilters: HotelFilters) => {
    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== false && value !== null) {
        params.set(key, String(value));
      }
    });
    setSearchParams(params);
  };

  const { data, isLoading, isError } = useHotels(filters);

  const handleFilterChange = (key: keyof HotelFilters, value: string | number | boolean | undefined) => {
    const newFilters = { ...filters, [key]: value, page: 1 };
    setFilters(newFilters);
    updateUrl(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters: HotelFilters = { search: '', checkin: '', checkout: '' };
    setFilters(emptyFilters);
    setSearchTerm('');
    setCheckin('');
    setCheckout('');
    setGuests(undefined);
    setSearchParams({});
  };

  const handleSearch = () => {
    const newFilters: HotelFilters = {
      ...filters,
      search: searchTerm,
      checkin: checkin || undefined,
      checkout: checkout || undefined,
      guests: guests || undefined,
      page: 1,
    };
    setFilters(newFilters);
    updateUrl(newFilters);
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <Helmet>
        <title>Hoteles en Ushuaia — Compará Precios y Encontrá el Mejor</title>
        <meta name="description" content="Explorá +150 hoteles en Ushuaia. Filtrá por precio, estrellas, ubicación y tipo de alojamiento. Precios actualizados de múltiples plataformas." />
      </Helmet>
      {/* Premium Dark Header */}
      <section className="relative bg-gradient-to-br from-slate-800 via-slate-900 to-slate-950 pb-16 border-b border-slate-700">
        <div className="absolute inset-0 bg-[url('${IMAGES.HERO_BG}')] bg-cover bg-center opacity-5"></div>
        
        <div className="relative container mx-auto px-6">
          <Link 
            to={ROUTES.HOME}
            className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition mb-8 pt-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Volver al inicio
          </Link>
          
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">Encuentra tu Hotel Perfecto</h1>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl">Comparamos precios de +150 hoteles en Ushuaia para que encuentres la mejor opción</p>
          
          {/* Search Bar with Dates and Guests */}
          <div className="max-w-5xl backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-xs font-semibold text-white/80 mb-1 ml-1">Destino / Nombre</label>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Buscar hotel..."
                  className="w-full bg-white/20 backdrop-blur-sm text-white placeholder-white/60 px-4 py-3 rounded-xl border border-white/30 focus:outline-none focus:ring-2 focus:ring-glacier-500"
                />
              </div>
              
              <div className="w-full md:w-40">
                <label className="block text-xs font-semibold text-white/80 mb-1 ml-1">Entrada</label>
                <input
                  type="date"
                  value={checkin}
                  onChange={(e) => setCheckin(e.target.value)}
                  className="w-full bg-white/20 backdrop-blur-sm text-white px-4 py-3 rounded-xl border border-white/30 focus:outline-none focus:ring-2 focus:ring-glacier-500 [color-scheme:dark]"
                />
              </div>

              <div className="w-full md:w-40">
                 <label className="block text-xs font-semibold text-white/80 mb-1 ml-1">Salida</label>
                <input
                  type="date"
                  value={checkout}
                  onChange={(e) => setCheckout(e.target.value)}
                  className="w-full bg-white/20 backdrop-blur-sm text-white px-4 py-3 rounded-xl border border-white/30 focus:outline-none focus:ring-2 focus:ring-glacier-500 [color-scheme:dark]"
                />
              </div>

              <div className="w-full md:w-32">
                 <label className="block text-xs font-semibold text-white/80 mb-1 ml-1">Huéspedes</label>
                <input
                  type="number"
                  min="1"
                  value={guests ?? ''}
                  onChange={(e) => setGuests(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full bg-white/20 backdrop-blur-sm text-white px-4 py-3 rounded-xl border border-white/30 focus:outline-none focus:ring-2 focus:ring-glacier-500"
                />
              </div>

              <div className="flex items-end">
                <button 
                  onClick={handleSearch}
                  className="w-full md:w-auto bg-gradient-to-r from-wood-500 to-wood-600 text-white px-8 py-3 rounded-xl font-bold hover:shadow-lg hover:shadow-wood-500/50 transition flex items-center justify-center gap-2 h-[50px]"
                >
                  <Search className="w-5 h-5" />
                  Buscar
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-12">
        <div className="flex gap-8">
          {/* Filters Sidebar */}
          <aside className={`${showFilters ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden`}>
            <div className="sticky top-24 backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <Filter className="w-6 h-6" />
                  Filtros
                </h2>
                <button
                  onClick={clearFilters}
                  className="text-sm text-slate-400 hover:text-white transition"
                >
                  Limpiar
                </button>
              </div>

              {/* Filters */}
              <div className="space-y-6">
                {/* Price Range */}
                <div>
                  <label className="block text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    Rango de Precio (por noche)
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <input
                      type="number"
                      placeholder="Mín"
                      value={filters.min_price || ''}
                      onChange={(e) => handleFilterChange('min_price', e.target.value ? Number(e.target.value) : undefined)}
                      className="bg-white/10 text-white placeholder-white/40 px-4 py-3 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-glacier-500"
                    />
                    <input
                      type="number"
                      placeholder="Máx"
                      value={filters.max_price || ''}
                      onChange={(e) => handleFilterChange('max_price', e.target.value ? Number(e.target.value) : undefined)}
                      className="bg-white/10 text-white placeholder-white/40 px-4 py-3 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-glacier-500"
                    />
                  </div>
                </div>

                {/* Stars */}
                <div>
                  <label className="block text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <Star className="w-4 h-4" />
                    Estrellas Mínimas
                  </label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map(stars => (
                      <button
                        key={stars}
                        onClick={() => handleFilterChange('min_stars', filters.min_stars === stars ? undefined : stars)}
                        className={`flex-1 py-2 rounded-lg font-medium transition ${
                          filters.min_stars === stars
                            ? 'bg-wood-500 text-white'
                            : 'bg-white/10 text-white/70 hover:bg-white/20'
                        }`}
                      >
                        {stars}+
                      </button>
                    ))}
                  </div>
                </div>

                {/* Location */}
                <div>
                  <label className="block text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    Ubicación
                  </label>
                  <div className="space-y-2">
                    {[
                      { value: 'centro', label: 'Centro' },
                      { value: 'afueras', label: 'Afueras' },
                      { value: 'montaña', label: 'Montaña' }
                    ].map(location => (
                      <button
                        key={location.value}
                        onClick={() => handleFilterChange('location_type', filters.location_type === location.value ? undefined : location.value)}
                        className={`w-full py-3 px-4 rounded-lg font-medium text-left transition ${
                          filters.location_type === location.value
                            ? 'bg-glacier-500 text-white'
                            : 'bg-white/10 text-white/70 hover:bg-white/20'
                        }`}
                      >
                        {location.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Type */}
                <div>
                  <label className="block text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <Home className="w-4 h-4" />
                    Tipo de Alojamiento
                  </label>
                  <div className="space-y-2">
                    {[
                      { value: 'hotel', label: 'Hotel' },
                      { value: 'hostel', label: 'Hostel' },
                      { value: 'apart', label: 'Apart Hotel' },
                      { value: 'cabaña', label: 'Cabaña' },
                      { value: 'casa', label: 'Casa' }
                    ].map(type => (
                      <button
                        key={type.value}
                        onClick={() => handleFilterChange('hotel_type', filters.hotel_type === type.value ? undefined : type.value)}
                        className={`w-full py-3 px-4 rounded-lg font-medium text-left transition ${
                          filters.hotel_type === type.value
                            ? 'bg-wood-500 text-white'
                            : 'bg-white/10 text-white/70 hover:bg-white/20'
                        }`}
                      >
                        {type.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Pet Friendly */}
                <div>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.pet_friendly || false}
                      onChange={(e) => handleFilterChange('pet_friendly', e.target.checked || undefined)}
                      className="w-5 h-5 rounded border-white/20 bg-white/10 text-wood-500 focus:ring-2 focus:ring-wood-500"
                    />
                    <span className="text-white font-medium">Pet Friendly</span>
                  </label>
                </div>
              </div>
            </div>
          </aside>

            {/* Results */}
          <main className="flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
              <div className="text-white">
                <h2 className="text-2xl font-bold">
                  {data?.count || 0} Hoteles Encontrados
                </h2>
                <p className="text-slate-400">
                  {(() => {
                    const activeFilters = Object.entries(filters).filter(([key, value]) => 
                      value !== undefined && 
                      value !== '' && 
                      value !== false &&
                      key !== 'search' &&
                      key !== 'page' &&
                      key !== 'ordering'
                    ).length;
                    return activeFilters > 0 ? `${activeFilters} filtros activos` : 'Sin filtros aplicados';
                  })()}
                </p>
              </div>
              
              <div className="flex items-center gap-3">
                  <select
                    value={filters.ordering || 'name'}
                    onChange={(e) => handleFilterChange('ordering', e.target.value)}
                    className="bg-white/10 text-white border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-glacier-500 appearance-none cursor-pointer"
                  >
                    <option value="name" className="bg-slate-800">Alfabético (A-Z)</option>
                    <option value="min_price" className="bg-slate-800">Precio (Menor a Mayor)</option>
                    <option value="-min_price" className="bg-slate-800">Precio (Mayor a Menor)</option>
                    <option value="-stars" className="bg-slate-800">Estrellas (Mayor a Menor)</option>
                  </select>

                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className="lg:hidden bg-white/10 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-white/20 transition"
                  >
                    <Filter className="w-5 h-5" />
                    {showFilters ? 'Ocultar' : 'Mostrar'}
                  </button>
              </div>
            </div>

            {isLoading && <HotelGridSkeleton count={6} />}
            
            {isError && (
              <div className="text-center py-12 backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl">
                <p className="text-slate-300">Error al cargar los hoteles</p>
              </div>
            )}

            {!isLoading && !isError && data && (
              <>
                {data.results.length > 0 ? (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                      {data.results.map(hotel => (
                        <HotelCard key={hotel.id} hotel={hotel} />
                      ))}
                    </div>
                    <GoogleAdSense slot="1234567890" format="horizontal" className="mt-8" />
                  </>
                ) : (
                  <div className="text-center py-20 backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl">
                    <Search className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                    <h3 className="text-2xl font-semibold text-white mb-2">No se encontraron hoteles</h3>
                    <p className="text-slate-400 mb-6">Intenta ajustar tus filtros de búsqueda</p>
                    <button
                      onClick={clearFilters}
                      className="inline-block bg-white/10 text-white px-6 py-3 rounded-lg hover:bg-white/20 transition"
                    >
                      Limpiar Filtros
                    </button>
                  </div>
                )}

                {/* Pagination */}
                {data.results.length > 0 && data.count > 20 && (
                  <div className="mt-12 flex justify-center gap-2">
                    <button
                      onClick={() => handleFilterChange('page', (filters.page || 1) - 1)}
                      disabled={!data.previous}
                      className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    <span className="px-4 py-3 text-white flex items-center">
                        Página {filters.page || 1}
                    </span>
                    <button
                      onClick={() => handleFilterChange('page', (filters.page || 1) + 1)}
                      disabled={!data.next}
                      className="px-6 py-3 bg-wood-500 text-white rounded-lg hover:bg-wood-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Siguiente
                    </button>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
