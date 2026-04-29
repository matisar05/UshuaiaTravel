import { Link } from 'react-router-dom';
import { MapPin, Menu, X } from 'lucide-react';
import { Disclosure } from '@headlessui/react';
import { ROUTES } from '@/constants/routes';

export default function Header() {
  return (
    <Disclosure as="nav" className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur-lg shadow-xl border-b border-slate-800">
      {({ open }) => (
        <>
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-18">
              <Link to={ROUTES.HOME} className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <MapPin className="w-8 h-8 text-glacier-400" strokeWidth={2} />
                <span className="text-2xl font-bold text-white">Ushuaia Travel</span>
              </Link>

              <div className="hidden md:flex items-center gap-6">
                <Link to={ROUTES.HOME} className="text-white/90 hover:text-white font-medium transition">
                  Inicio
                </Link>
                <Link to={ROUTES.HOTELES} className="text-white/90 hover:text-white font-medium transition">
                  Hoteles
                </Link>
                <Link to={ROUTES.GUIA} className="text-white/90 hover:text-white font-medium transition">
                  Guía
                </Link>
                <Link to={ROUTES.DONAR} className="bg-gradient-to-r from-wood-500 to-wood-600 text-white px-6 py-2 rounded-xl font-semibold hover:shadow-lg hover:shadow-wood-500/50 transition">
                  Apoyar
                </Link>
              </div>

              <Disclosure.Button className="md:hidden p-2 rounded-lg text-slate-400 hover:bg-white/10 focus:outline-none">
                {open ? (
                  <X className="w-6 h-6" />
                ) : (
                  <Menu className="w-6 h-6" />
                )}
              </Disclosure.Button>
            </div>
          </div>

          <Disclosure.Panel className="md:hidden border-t border-slate-800">
            <div className="px-4 py-4 space-y-2 bg-slate-900">
              <Link to={ROUTES.HOME} className="block px-4 py-3 text-sm font-medium text-white hover:bg-white/10 rounded-lg transition-colors">
                Inicio
              </Link>
              <Link to={ROUTES.HOTELES} className="block px-4 py-3 text-sm font-medium text-white hover:bg-white/10 rounded-lg transition-colors">
                Hoteles
              </Link>
              <Link to={ROUTES.GUIA} className="block px-4 py-3 text-sm font-medium text-white hover:bg-white/10 rounded-lg transition-colors">
                Guía
              </Link>
              <Link to={ROUTES.DONAR} className="block px-4 py-3 text-sm font-medium text-white bg-gradient-to-r from-wood-500 to-wood-600 rounded-lg transition">
                Apoyar
              </Link>
            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}
