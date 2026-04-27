import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, MapPin, Star, ArrowRight, Sparkles, TrendingUp, Mail, Heart, ExternalLink, Map as MapIcon } from 'lucide-react';
import { useFeaturedHotels } from '@/hooks/useHotels';
import HotelCard from '@/components/hotels/HotelCard/HotelCard';
import HotelMap from '@/components/hotels/HotelMap';

export default function HomePage() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const { data: featuredHotels, isLoading, isError } = useFeaturedHotels();
  const [isScrolled, setIsScrolled] = useState(false);

  const handleSearch = () => {
    if (searchTerm.trim()) {
      navigate(`/hoteles?search=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="bg-slate-900">
      {/* HERO MASIVO */}
      <section 
        className="relative min-h-screen bg-cover bg-center flex items-center justify-center"
        style={{ backgroundImage: "url('https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?q=80&w=1920')" }}
      >
        {/* MINIMAL overlay - mountains clearly visible! */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-black/25 to-slate-900/40" />
        
        {/* Navbar Glassmorphism - Sticky */}
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled ? 'bg-slate-900/95 backdrop-blur-lg shadow-xl' : 'bg-transparent'
        }`}>
          <div className="container mx-auto px-6 py-6">
            <div className={`backdrop-blur-md border rounded-2xl px-8 py-4 flex items-center justify-between transition-all duration-300 ${
              isScrolled 
                ? 'bg-white/5 border-white/10' 
                : 'bg-white/10 border-white/20'
            }`}>
              <div className="flex items-center gap-3">
                <MapPin className="w-8 h-8 text-white" strokeWidth={2} />
                <span className="text-2xl font-bold text-white">Ushuaia Travel</span>
              </div>
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

        {/* Hero Content */}
        <div className="relative z-10 container mx-auto px-6 text-center">
          <h1 className="text-7xl md:text-8xl font-bold text-white mb-6 leading-tight">
            El Fin del Mundo<br />Te Espera
          </h1>
          <p className="text-2xl text-white/90 mb-12 max-w-3xl mx-auto font-light">
            Descubre los mejores hoteles de Ushuaia con precios comparados.<br />
            Vive la aventura invernal más exclusiva de Patagonia.
          </p>
          
          {/* Search Bar Glassmorphism */}
          <div className="max-w-3xl mx-auto backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-3">
            <div className="flex gap-3 items-center">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="¿Dónde quieres hospedarte?"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full bg-white/20 backdrop-blur-sm text-white placeholder-white/60 px-6 py-4 rounded-xl border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50 text-lg"
                />
              </div>
              <button 
                onClick={handleSearch}
                className="bg-gradient-to-r from-wood-500 to-wood-600 text-white px-8 py-4 rounded-xl font-bold hover:shadow-2xl hover:shadow-wood-500/50 transition flex items-center gap-2"
              >
                <Search className="w-6 h-6" />
                Buscar
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-xl p-6">
              <div className="text-4xl font-bold text-white mb-2">150+</div>
              <div className="text-white/80">Hoteles</div>
            </div>
            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-xl p-6">
              <div className="text-4xl font-bold text-white mb-2">5.0</div>
              <div className="text-white/80">Rating</div>
            </div>
            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-xl p-6">
              <div className="text-4xl font-bold text-white mb-2">24/7</div>
              <div className="text-white/80">Soporte</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gradient-to-b from-slate-900 to-slate-800">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold text-white mb-6">¿Por qué Ushuaia Travel?</h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              La forma más inteligente de encontrar tu hotel perfecto
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="group backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8 hover:bg-white/10 hover:border-white/20 transition-all hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-glacier-500 to-glacier-700 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
                <Search className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Comparación Inteligente</h3>
              <p className="text-slate-300 leading-relaxed">
                Comparamos Booking, Airbnb, TripAdvisor y sitios locales para garantizarte el mejor precio.
              </p>
            </div>

            <div className="group backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8 hover:bg-white/10 hover:border-white/20 transition-all hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-wood-500 to-wood-700 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Siempre Actualizado</h3>
              <p className="text-slate-300 leading-relaxed">
                Precios actualizados mensualmente para que tomes decisiones con información real.
              </p>
            </div>

            <div className="group backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8 hover:bg-white/10 hover:border-white/20 transition-all hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Expertos en Ushuaia</h3>
              <p className="text-slate-300 leading-relaxed">
                Nos especializamos en el Fin del Mundo para ofrecerte la información más precisa.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Hotels Section */}
      <section id="hoteles" className="py-24 bg-slate-800">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold text-white mb-6">Hoteles Destacados</h2>
            <p className="text-xl text-slate-300">Los alojamientos más premium de Ushuaia</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {isLoading && (
              <div className="col-span-3 text-center text-white py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-white/20 border-t-white"></div>
                <p className="mt-4">Cargando hoteles destacados...</p>
              </div>
            )}
            {isError && (
              <div className="col-span-3 text-center text-red-400 py-12 bg-red-400/10 rounded-xl border border-red-400/20">
                No se pudieron cargar los hoteles destacados en este momento.
              </div>
            )}
            {!isLoading && !isError && (!featuredHotels || featuredHotels.length === 0) && (
              <div className="col-span-3 text-center text-slate-300 py-12 bg-white/5 rounded-xl border border-white/10">
                Aún no hay hoteles destacados disponibles.
              </div>
            )}
            {!isLoading && !isError && featuredHotels?.slice(0, 3).map((hotel: any) => (
              <HotelCard key={hotel.id} hotel={hotel} />
            ))}
          </div>

          <div className="text-center mt-12">
            <Link to="/hoteles" className="backdrop-blur-md bg-white/10 border-2 border-white/20 text-white px-10 py-4 rounded-xl font-bold text-lg hover:bg-white/20 transition inline-block">
              Ver todos los hoteles
            </Link>
          </div>
        </div>
      </section>

      {/* Interactive Map Section */}
      <section className="py-24 bg-slate-900 border-t border-slate-800">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-end justify-between mb-12 gap-6">
            <div className="max-w-2xl">
              <div className="flex items-center gap-2 text-blue-400 mb-4">
                <MapIcon className="w-5 h-5" />
                <span className="text-sm font-bold uppercase tracking-widest">Mapa Interactivo</span>
              </div>
              <h2 className="text-5xl font-bold text-white mb-6">Explora Ushuaia</h2>
              <p className="text-xl text-slate-400">
                Encuentra tu hospedaje ideal navegando por el mapa de la ciudad más austral del mundo.
              </p>
            </div>
            <Link 
              to="/hoteles" 
              className="group flex items-center gap-2 text-white font-bold hover:text-blue-400 transition"
            >
              Ver todos en el mapa
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>
            <div className="relative">
              {!isLoading && featuredHotels && (
                <HotelMap hotels={featuredHotels} />
              )}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-glacier-900 via-slate-900 to-wood-900"></div>

        
        <div className="relative container mx-auto px-6 text-center">
          <h2 className="text-6xl font-bold text-white mb-6">
            ¿Listo para la Aventura?
          </h2>
          <p className="text-2xl text-white/80 mb-12 max-w-2xl mx-auto">
            Reserva ahora y vive la experiencia invernal más inolvidable en el Fin del Mundo
          </p>
          <Link
            to="/hoteles"
            className="inline-block bg-gradient-to-r from-wood-500 via-wood-600 to-wood-700 text-white px-12 py-6 rounded-2xl font-bold text-xl hover:shadow-2xl hover:shadow-wood-500/50 transition transform hover:scale-105"
          >
            Explorar Hoteles
          </Link>
        </div>
      </section>

      {/* Footer Integrado */}
      <footer className="bg-slate-950 text-slate-300">
        <div className="container mx-auto px-6">
          {/* Main Footer */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 py-16 border-b border-slate-800">
            {/* Brand */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <MapPin className="w-5 h-5 text-glacier-400" />
                <h3 className="text-lg font-semibold text-white">Ushuaia Travel</h3>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                Tu fuente confiable de información turística en Ushuaia, Argentina.
                Comparamos precios para que encuentres la mejor opción.
              </p>
            </div>

            {/* Links */}
            <div className="space-y-4">
              <h4 className="text-base font-semibold text-white">Enlaces</h4>
              <ul className="space-y-3">
                <li>
                  <Link to="/" className="text-sm text-slate-400 hover:text-white transition-colors">
                    Inicio
                  </Link>
                </li>
                <li>
                  <Link to="/hoteles" className="text-sm text-slate-400 hover:text-white transition-colors">
                    Hoteles
                  </Link>
                </li>
                <li>
                  <Link to="/donar" className="text-sm text-slate-400 hover:text-white transition-colors">
                    Apoyar el proyecto
                  </Link>
                </li>
              </ul>
            </div>

            {/* Contact */}
            <div className="space-y-4">
              <h4 className="text-base font-semibold text-white">Contacto & Apoyo</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Mail className="w-4 h-4" />
                  <span>Sugerencias y contacto</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Heart className="w-4 h-4 text-wood-500" />
                  <span>Hecho con pasión en Argentina</span>
                </div>
                <div className="pt-2">
                  <Link 
                    to="/donar"
                    className="inline-flex items-center gap-2 text-sm font-medium text-glacier-400 hover:text-glacier-300 transition-colors"
                  >
                    Apoya este proyecto
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Footer */}
          <div className="py-8 space-y-2 text-center">
            <p className="text-xs text-slate-500">
              © {new Date().getFullYear()} Ushuaia Travel. Información actualizada regularmente.
            </p>
            <p className="text-xs text-slate-600 italic">
              Los precios son referenciales. Te recomendamos confirmar en la plataforma oficial antes de reservar.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
