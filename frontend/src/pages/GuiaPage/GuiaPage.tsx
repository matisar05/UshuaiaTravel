import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { Calendar, MapPin, Snowflake, Sun, Anchor } from 'lucide-react';
import { ROUTES } from '@/constants/routes';

export default function GuiaPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-300">
      <Helmet>
        <title>Guía de Ushuaia 2026 — Cuándo Ir, Qué Hacer, Dónde Alojarse</title>
        <meta name="description" content="Guía completa de Ushuaia: mejor época para visitar, qué hacer en invierno y verano, dónde alojarse cerca del Parque Nacional, Cerro Castor y el Canal Beagle." />
      </Helmet>

      <div className="container mx-auto px-6 py-20 max-w-4xl">
        <Link to={ROUTES.HOME} className="text-glacier-400 hover:text-glacier-300 mb-8 inline-block">← Volver al inicio</Link>
        
        <h1 className="text-5xl font-bold text-white mb-6">Guía de Ushuaia 2026</h1>
        <p className="text-xl text-slate-400 mb-16">Todo lo que necesitás saber para planificar tu viaje al Fin del Mundo.</p>

        {/* Cuándo ir */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 flex items-center gap-3">
            <Calendar className="w-8 h-8 text-glacier-400" />
            ¿Cuándo ir a Ushuaia?
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
              <div className="w-12 h-12 bg-gradient-to-br from-glacier-500 to-glacier-700 rounded-xl flex items-center justify-center mb-4">
                <Snowflake className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Invierno (jun-ago)</h3>
              <p className="text-slate-400 leading-relaxed mb-4">
                Temporada alta de esquí. Cerro Castor abre sus pistas con la nieve en su punto máximo. 
                Las temperaturas oscilan entre -5°C y 5°C. Ideal para esquí, snowboard, trineos con perros 
                y caminatas con raquetas.
              </p>
              <span className="text-xs bg-glacier-500/20 text-glacier-300 px-3 py-1 rounded-full">🥇 Mejor para esquí</span>
            </div>
            <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
              <div className="w-12 h-12 bg-gradient-to-br from-wood-500 to-wood-700 rounded-xl flex items-center justify-center mb-4">
                <Sun className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Verano (dic-feb)</h3>
              <p className="text-slate-400 leading-relaxed mb-4">
                Días largos con hasta 18 horas de luz. Temperaturas entre 5°C y 15°C. 
                Perfecto para trekking en el Parque Nacional Tierra del Fuego, navegación 
                por el Canal Beagle y observación de fauna.
              </p>
              <span className="text-xs bg-wood-500/20 text-wood-300 px-3 py-1 rounded-full">🥇 Mejor para trekking</span>
            </div>
          </div>
        </section>

        {/* Dónde alojarse */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 flex items-center gap-3">
            <MapPin className="w-8 h-8 text-wood-400" />
            ¿Dónde alojarse?
          </h2>
          <div className="space-y-6">
            {[
              {
                zone: 'Centro',
                desc: 'Ideal para primera visita. Cerca de restaurantes, agencias de turismo y el puerto. Perfecto si venís en crucero o querés estar cerca de todo.',
                icon: '🏙️',
              },
              {
                zone: 'Montaña / Cerro Castor',
                desc: 'La mejor zona para esquiadores. A 26 km del centro, rodeado de bosques y nieve. Hoteles con servicio de traslado a las pistas.',
                icon: '⛷️',
              },
              {
                zone: 'Afueras / Parque Nacional',
                desc: 'Tranquilidad absoluta. Cerca del Parque Nacional Tierra del Fuego. Ideal para los que buscan naturaleza y desconexión.',
                icon: '🌲',
              },
            ].map((z) => (
              <div key={z.zone} className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-2">{z.icon} {z.zone}</h3>
                <p className="text-slate-400 leading-relaxed">{z.desc}</p>
              </div>
            ))}
          </div>
          <div className="mt-8 text-center">
            <Link to={ROUTES.HOTELES} className="bg-gradient-to-r from-wood-500 to-wood-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-wood-500/50 transition inline-block">
              Buscar hoteles en Ushuaia
            </Link>
          </div>
        </section>

        {/* Imperdibles */}
        <section>
          <h2 className="text-3xl font-bold text-white mb-8 flex items-center gap-3">
            <Anchor className="w-8 h-8 text-emerald-400" />
            Imperdibles de Ushuaia
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              'Parque Nacional Tierra del Fuego',
              'Cerro Castor (esquí)',
              'Navegación Canal Beagle',
              'Tren del Fin del Mundo',
              'Lago Escondido y Fagnano',
              'Museo del Fin del Mundo',
              'Laguna Esmeralda (trekking)',
              'Isla Martillo (pingüinos)',
            ].map((item) => (
              <div key={item} className="flex items-center gap-3 bg-white/5 rounded-xl p-4">
                <div className="w-2 h-2 bg-glacier-400 rounded-full shrink-0" />
                <span className="text-slate-300">{item}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
