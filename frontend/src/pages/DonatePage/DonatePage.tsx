import { Link } from 'react-router-dom';
import { Heart, CreditCard, DollarSign, Users, MapPin } from 'lucide-react';

export default function DonatePage() {
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
                className="bg-gradient-to-r from-wood-500 to-wood-600 text-white px-6 py-2 rounded-xl font-semibold hover:shadow-lg hover:shadow-wood-500/50 transition border-b-2 border-wood-400"
              >
                Apoyar
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section 
        className="relative pt-32 pb-24 bg-cover bg-center min-h-[70vh] flex items-center"
        style={{ backgroundImage: "url('https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?q=80&w=1920')" }}
      >
        {/* Gradient overlay for readability */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900/60 via-slate-900/70 to-slate-900/80"></div>
        
        <div className="relative container mx-auto px-6 text-center">
          <Heart className="w-20 h-20 text-wood-500 mx-auto mb-6" />
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Apoya Ushuaia Travel
          </h1>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-8">
            Tu donación nos ayuda a mantener este servicio gratuito y actualizado para todos los viajeros que visitan Ushuaia.
          </p>
        </div>
      </section>

      {/* Why Donate */}
      <section className="py-20 bg-gradient-to-b from-slate-900 to-slate-800">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-white text-center mb-12">
            ¿Por qué donar?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8 text-center hover:bg-white/10 transition">
              <div className="w-16 h-16 bg-gradient-to-br from-glacier-500 to-glacier-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Servicio Gratuito</h3>
              <p className="text-slate-300">
                Mantenemos la plataforma 100% gratuita para todos los viajeros
              </p>
            </div>

            <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8 text-center hover:bg-white/10 transition">
              <div className="w-16 h-16 bg-gradient-to-br from-wood-500 to-wood-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <DollarSign className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Actualización Constante</h3>
              <p className="text-slate-300">
                Tus aportes permiten actualizar los precios mensualmente
              </p>
            </div>

            <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8 text-center hover:bg-white/10 transition">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Heart className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Proyecto Independiente</h3>
              <p className="text-slate-300">
                Somos un proyecto argentino independiente sin fines de lucro
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Donation Options */}
      <section className="py-20 bg-slate-800">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-white text-center mb-4">
            Elige tu método para donar
          </h2>
          <p className="text-xl text-slate-400 text-center mb-16">
            Cualquier aporte es bienvenido y valorado
          </p>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* MercadoPago */}
            <div className="backdrop-blur-md bg-gradient-to-br from-glacier-500/10 to-wood-500/10 border-2 border-white/20 rounded-3xl p-10 text-center hover:border-white/40 transition">
              <div className="w-20 h-20 bg-gradient-to-br from-glacier-500 to-glacier-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <CreditCard className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-4">MercadoPago</h3>
              <p className="text-slate-300 mb-8">
                Donación rápida y segura en pesos argentinos
              </p>
              
              <div className="space-y-3 mb-8">
                <button 
                  onClick={() => alert('🚧 Integración de MercadoPago próximamente. Esta es una demo del diseño.')}
                  className="w-full bg-gradient-to-r from-wood-500 to-wood-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-wood-500/50 transition transform hover:scale-105"
                >
                  $500 ARS
                </button>
                <button 
                  onClick={() => alert('🚧 Integración de MercadoPago próximamente. Esta es una demo del diseño.')}
                  className="w-full bg-gradient-to-r from-wood-500 to-wood-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-wood-500/50 transition transform hover:scale-105"
                >
                  $1000 ARS
                </button>
                <button 
                  onClick={() => alert('🚧 Integración de MercadoPago próximamente. Esta es una demo del diseño.')}
                  className="w-full bg-gradient-to-r from-wood-500 to-wood-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-wood-500/50 transition transform hover:scale-105"
                >
                  $2000 ARS
                </button>
              </div>

              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4">
                <input
                  type="number"
                  placeholder="Otro monto en ARS"
                  id="custom-ars"
                  className="w-full bg-white/10 text-white placeholder-white/40 px-4 py-3 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-wood-500 mb-3"
                />
                <button 
                  onClick={() => {
                    const input = document.getElementById('custom-ars') as HTMLInputElement;
                    const amount = input?.value;
                    alert(`🚧 Integración de MercadoPago próximamente.\n\nMonto seleccionado: $${amount || '0'} ARS`);
                  }}
                  className="w-full bg-white/10 text-white py-3 px-6 rounded-lg font-semibold hover:bg-white/20 transition"
                >
                  Donar monto personalizado
                </button>
              </div>
            </div>

            {/* PayPal */}
            <div className="backdrop-blur-md bg-gradient-to-br from-glacier-500/10 to-emerald-500/10 border-2 border-white/20 rounded-3xl p-10 text-center hover:border-white/40 transition">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <DollarSign className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-4">PayPal</h3>
              <p className="text-slate-300 mb-8">
                Donación internacional en dólares
              </p>
              
              <div className="space-y-3 mb-8">
                <button 
                  onClick={() => alert('🚧 Integración de PayPal próximamente. Esta es una demo del diseño.')}
                  className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-emerald-500/50 transition transform hover:scale-105"
                >
                  $5 USD
                </button>
                <button 
                  onClick={() => alert('🚧 Integración de PayPal próximamente. Esta es una demo del diseño.')}
                  className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-emerald-500/50 transition transform hover:scale-105"
                >
                  $10 USD
                </button>
                <button 
                  onClick={() => alert('🚧 Integración de PayPal próximamente. Esta es una demo del diseño.')}
                  className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-emerald-500/50 transition transform hover:scale-105"
                >
                  $20 USD
                </button>
              </div>

              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4">
                <input
                  type="number"
                  placeholder="Otro monto en USD"
                  id="custom-usd"
                  className="w-full bg-white/10 text-white placeholder-white/40 px-4 py-3 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-emerald-500 mb-3"
                />
                <button 
                  onClick={() => {
                    const input = document.getElementById('custom-usd') as HTMLInputElement;
                    const amount = input?.value;
                    alert(`🚧 Integración de PayPal próximamente.\n\nMonto seleccionado: $${amount || '0'} USD`);
                  }}
                  className="w-full bg-white/10 text-white py-3 px-6 rounded-lg font-semibold hover:bg-white/20 transition"
                >
                  Donar con PayPal
                </button>
              </div>
            </div>
          </div>

          <div className="mt-16 text-center">
            <p className="text-slate-400 mb-4">
              Esta es una página de muestra. La integración de pagos se activará próximamente.
            </p>
            <div className="inline-flex items-center gap-2 text-emerald-400">
              <Heart className="w-5 h-5 fill-current" />
              <span className="font-semibold">¡Gracias por tu apoyo!</span>
            </div>
          </div>
        </div>
      </section>

      {/* Thank You */}
      <section className="py-16 bg-gradient-to-r from-glacier-900 to-wood-900">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Cada donación cuenta
          </h2>
          <p className="text-xl text-white/80 max-w-2xl mx-auto">
            Gracias a personas como tú, podemos seguir ofreciendo información de calidad de forma gratuita a todos los viajeros.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 text-slate-300 py-12">
        <div className="container mx-auto px-6 text-center">
          <p className="text-sm text-slate-500">
            © {new Date().getFullYear()} Ushuaia Travel. Información actualizada regularmente.
          </p>
          <p className="text-xs text-slate-600 italic mt-2">
            Proyecto argentino independiente sin fines de lucro
          </p>
        </div>
      </footer>
    </div>
  );
}
