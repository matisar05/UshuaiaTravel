import { Link } from 'react-router-dom';
import { MapPin, Menu, X } from 'lucide-react';
import { Disclosure } from '@headlessui/react';

export default function Header() {
  return (
    <Disclosure as="nav" className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200">
      {({ open }) => (
        <>
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-18">
              {/* Logo */}
              <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <MapPin className="w-6 h-6 text-glacier-600" strokeWidth={2.5} />
                <span className="text-xl font-bold text-slate-900">Ushuaia Travel</span>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center gap-2">
                <Link
                  to="/"
                  className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  Inicio
                </Link>
                <Link
                  to="/hoteles"
                  className="px-4 py-2 text-sm font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  Hoteles
                </Link>
                <Link
                  to="/donar"
                  className="btn-primary ml-4"
                >
                  Apoyar
                </Link>
              </div>

              {/* Mobile menu button */}
              <Disclosure.Button className="md:hidden p-2 rounded-lg text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-glacier-500">
                {open ? (
                  <X className="w-6 h-6" />
                ) : (
                  <Menu className="w-6 h-6" />
                )}
              </Disclosure.Button>
            </div>
          </div>

          {/* Mobile Navigation */}
          <Disclosure.Panel className="md:hidden border-t border-slate-200">
            <div className="px-4 py-4 space-y-2">
              <Link
                to="/"
                className="block px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Inicio
              </Link>
              <Link
                to="/hoteles"
                className="block px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              >
                Hoteles
              </Link>
              <Link
                to="/donar"
                className="block w-full btn-primary mt-2"
              >
                Apoyar
              </Link>
            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}
