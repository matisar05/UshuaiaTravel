import { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Heart, CreditCard, DollarSign, Users, Check, ArrowRight, AlertCircle } from 'lucide-react';
import { IMAGES } from '@/constants/images';

const MP_PUBLIC_KEY = import.meta.env.VITE_MERCADOPAGO_PUBLIC_KEY || '';
const PAYPAL_CLIENT_ID = import.meta.env.VITE_PAYPAL_CLIENT_ID || '';

const API_URL = '/api/v1';

const ARS_AMOUNTS = [500, 1000, 2000, 5000];
const USD_AMOUNTS = [5, 10, 20, 50];

export default function DonatePage() {
  const [customArs, setCustomArs] = useState('');
  const [customUsd, setCustomUsd] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleMercadoPago = async (amount: number) => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/donations/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount,
          description: `Donación Ushuaia Travel - ARS ${amount}`,
          platform: 'mercadopago',
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Error al crear el pago');
      }
      const data = await res.json();
      window.location.href = data.init_point;
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Error al conectar con MercadoPago';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleMercadoPagoCustom = () => {
    const amount = Number(customArs);
    if (amount > 0) handleMercadoPago(amount);
  };

  const handlePayPal = (amount: number) => {
    setError('');
    if (!PAYPAL_CLIENT_ID) {
      setError('PayPal no está configurado todavía. Pronto estará disponible.');
      return;
    }
    window.open(
      `https://www.paypal.com/donate?business=${PAYPAL_CLIENT_ID}&amount=${amount}&currency_code=USD&item_name=Donación+Ushuaia+Travel`,
      '_blank'
    );
    setSuccess(`Redirigiendo a PayPal para donar $${amount} USD...`);
  };

  const handlePayPalCustom = () => {
    const amount = Number(customUsd);
    if (amount > 0) handlePayPal(amount);
  };

  const hasMercadoPago = !!MP_PUBLIC_KEY;

  return (
    <div className="min-h-screen bg-slate-900">
      <Helmet>
        <title>Apoya Ushuaia Travel — Donaciones</title>
        <meta name="description" content="Apoya Ushuaia Travel con una donación. Tu aporte nos ayuda a mantener este servicio gratuito y actualizado de información turística en Ushuaia." />
      </Helmet>

      <section
        className="relative pt-16 pb-24 bg-cover bg-center min-h-[70vh] flex items-center"
        style={{ backgroundImage: `url('${IMAGES.HERO_BG}')` }}
      >
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

      <section className="py-20 bg-gradient-to-b from-slate-900 to-slate-800">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-white text-center mb-12">
            ¿Por qué donar?
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              { icon: Users, color: 'from-glacier-500 to-glacier-700', title: 'Servicio Gratuito', desc: 'Mantenemos la plataforma 100% gratuita para todos los viajeros' },
              { icon: DollarSign, color: 'from-wood-500 to-wood-700', title: 'Actualización Constante', desc: 'Tus aportes permiten actualizar los precios mensualmente' },
              { icon: Heart, color: 'from-emerald-500 to-emerald-700', title: 'Proyecto Independiente', desc: 'Somos un proyecto argentino independiente sin fines de lucro' },
            ].map(({ icon: Icon, color, title, desc }) => (
              <div key={title} className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8 text-center hover:bg-white/10 transition">
                <div className={`w-16 h-16 bg-gradient-to-br ${color} rounded-2xl flex items-center justify-center mx-auto mb-6`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">{title}</h3>
                <p className="text-slate-300">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-slate-800">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-white text-center mb-4">
            Elige tu método para donar
          </h2>
          <p className="text-xl text-slate-400 text-center mb-8">
            Cualquier aporte es bienvenido y valorado
          </p>

          {error && (
            <div className="max-w-2xl mx-auto mb-6 bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3 text-red-400">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          {success && (
            <div className="max-w-2xl mx-auto mb-6 bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 flex items-center gap-3 text-emerald-400">
              <Check className="w-5 h-5 shrink-0" />
              <span>{success}</span>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* MercadoPago */}
            <div className="backdrop-blur-md bg-gradient-to-br from-glacier-500/10 to-wood-500/10 border-2 border-white/20 rounded-3xl p-10 text-center hover:border-white/40 transition">
              <div className="w-20 h-20 bg-gradient-to-br from-glacier-500 to-glacier-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <CreditCard className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-4">MercadoPago</h3>
              <p className="text-slate-300 mb-8">
                Donación en pesos argentinos
              </p>

              {hasMercadoPago ? (
                <>
                  <div className="space-y-3 mb-8">
                    {ARS_AMOUNTS.map((amount) => (
                      <button
                        key={amount}
                        onClick={() => handleMercadoPago(amount)}
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-wood-500 to-wood-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-wood-500/50 transition disabled:opacity-50 flex items-center justify-center gap-2"
                      >
                        {loading ? 'Procesando...' : `$${amount.toLocaleString('es-AR')} ARS`}
                        <ArrowRight className="w-5 h-5" />
                      </button>
                    ))}
                  </div>
                  <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4">
                    <input
                      type="number"
                      placeholder="Otro monto en ARS"
                      value={customArs}
                      onChange={(e) => setCustomArs(e.target.value)}
                      className="w-full bg-white/10 text-white placeholder-white/40 px-4 py-3 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-wood-500 mb-3"
                    />
                    <button
                      onClick={handleMercadoPagoCustom}
                      disabled={loading || !customArs}
                      className="w-full bg-white/10 text-white py-3 px-6 rounded-lg font-semibold hover:bg-white/20 transition disabled:opacity-50"
                    >
                      Donar monto personalizado
                    </button>
                  </div>
                </>
              ) : (
                <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-slate-400">
                  <p>MercadoPago estará disponible pronto.</p>
                  <p className="text-sm mt-2">Configurá VITE_MERCADOPAGO_PUBLIC_KEY para activar.</p>
                </div>
              )}
            </div>

            {/* PayPal */}
            <div className="backdrop-blur-md bg-gradient-to-br from-emerald-500/10 to-blue-500/10 border-2 border-white/20 rounded-3xl p-10 text-center hover:border-white/40 transition">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-emerald-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <DollarSign className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-3xl font-bold text-white mb-4">PayPal</h3>
              <p className="text-slate-300 mb-8">
                Donación en dólares
              </p>

              <div className="space-y-3 mb-8">
                {USD_AMOUNTS.map((amount) => (
                  <button
                    key={amount}
                    onClick={() => handlePayPal(amount)}
                    className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-emerald-500/50 transition flex items-center justify-center gap-2"
                  >
                    ${amount} USD
                    <ArrowRight className="w-5 h-5" />
                  </button>
                ))}
              </div>

              <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4">
                <input
                  type="number"
                  placeholder="Otro monto en USD"
                  value={customUsd}
                  onChange={(e) => setCustomUsd(e.target.value)}
                  className="w-full bg-white/10 text-white placeholder-white/40 px-4 py-3 rounded-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-emerald-500 mb-3"
                />
                <button
                  onClick={handlePayPalCustom}
                  className="w-full bg-white/10 text-white py-3 px-6 rounded-lg font-semibold hover:bg-white/20 transition"
                >
                  Donar con PayPal
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

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
    </div>
  );
}
