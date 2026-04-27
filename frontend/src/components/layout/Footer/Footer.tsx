import { Link } from 'react-router-dom';
import { MapPin, Mail, Heart, ExternalLink } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900 text-slate-300 mt-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 py-16 border-b border-slate-800">
          {/* Brand Section */}
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

          {/* Links Section */}
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

          {/* Contact Section */}
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
              {/* Donation Placeholder */}
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
            © {currentYear} Ushuaia Travel. Información actualizada regularmente.
          </p>
          <p className="text-xs text-slate-600 italic">
            Los precios son referenciales. Te recomendamos confirmar en la plataforma oficial antes de reservar.
          </p>
        </div>
      </div>
    </footer>
  );
}
