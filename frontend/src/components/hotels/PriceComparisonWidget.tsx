import React from 'react';
import { ExternalLink, TrendingDown, Info } from 'lucide-react';
import type { Price } from '@/types';

interface PriceComparisonWidgetProps {
  prices: Price[];
  targetCurrency?: string;
}

const PriceComparisonWidget: React.FC<PriceComparisonWidgetProps> = ({ 
  prices,
  targetCurrency = 'ARS'
}) => {
  if (!prices || prices.length === 0) return null;

  // Sort by price_converted (or price_per_night if not available)
  const sortedPrices = [...prices].sort((a, b) => {
    const valA = a.price_converted ?? a.price_per_night;
    const valB = b.price_converted ?? b.price_per_night;
    return valA - valB;
  });

  const cheapest = sortedPrices[0];
  const expensive = sortedPrices[sortedPrices.length - 1];
  
  const valCheapest = cheapest.price_converted ?? cheapest.price_per_night;
  const valExpensive = expensive.price_converted ?? expensive.price_per_night;
  const savings = valExpensive - valCheapest;
  const savingsPercent = Math.round((savings / valExpensive) * 100);

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
      <div className="p-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
        <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          Comparativa de Precios
          <Info className="w-3.5 h-3.5 text-slate-400" />
        </h4>
        {savings > 0 && (
          <span className="flex items-center gap-1 text-[10px] font-black text-green-600 bg-green-50 px-2 py-0.5 rounded-full uppercase tracking-wider">
            <TrendingDown className="w-3 h-3" />
            Ahorrá {savingsPercent}%
          </span>
        )}
      </div>

      <div className="divide-y divide-slate-50">
        {sortedPrices.map((p) => (
          <div 
            key={p.id} 
            className={`p-4 flex items-center justify-between transition-colors hover:bg-slate-50/50 ${
              p.id === cheapest.id ? 'bg-blue-50/30' : ''
            }`}
          >
            <div className="flex flex-col gap-0.5">
              <span className="text-xs font-bold text-slate-700 capitalize">
                {p.platform_display}
              </span>
              <span className="text-[10px] text-slate-400 font-medium">
                {p.room_type || 'Habitación Standard'}
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-black text-slate-900">
                  {targetCurrency} {(p.price_converted ?? p.price_per_night).toLocaleString('es-AR')}
                </div>
                {p.currency !== targetCurrency && (
                  <div className="text-[9px] text-slate-400 font-medium">
                    Original: {p.currency} {p.price_per_night.toLocaleString('es-AR')}
                  </div>
                )}
              </div>

              <a 
                href={p.platform_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className={`p-2 rounded-lg transition-all ${
                  p.id === cheapest.id 
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-100 hover:bg-blue-700' 
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PriceComparisonWidget;
