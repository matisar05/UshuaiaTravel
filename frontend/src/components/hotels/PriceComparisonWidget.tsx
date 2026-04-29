import { ExternalLink, TrendingDown, Zap, ArrowRight } from "lucide-react";
import type { Price, PriceComparison } from "@/types";
import { getPlatformConfig } from "@/constants/platforms";

interface PriceComparisonWidgetProps {
  comparison?: PriceComparison;
  prices?: Price[];
  hotelName?: string;
}

export default function PriceComparisonWidget({
  comparison,
  prices: directPrices,
  hotelName,
}: PriceComparisonWidgetProps) {
  const allPrices: Price[] =
    comparison
      ? Object.values(comparison.comparison).flat()
      : directPrices ?? [];

  if (allPrices.length === 0) return null;

  const sorted = [...allPrices].sort(
    (a, b) => (a.price_converted ?? a.price_per_night) - (b.price_converted ?? b.price_per_night)
  );
  const cheapest = sorted[0];
  const mostExpensive = sorted[sorted.length - 1];
  const cheapestVal = cheapest.price_converted ?? cheapest.price_per_night;
  const expensiveVal = mostExpensive.price_converted ?? mostExpensive.price_per_night;
  const savings = expensiveVal - cheapestVal;
  const savingsPercent =
    expensiveVal > 0 ? Math.round((savings / expensiveVal) * 100) : 0;

  return (
    <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Comparación de Precios</h2>
        {savings > 0 && savingsPercent > 0 && (
          <div className="flex items-center gap-1.5 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-bold px-3 py-1.5 rounded-full">
            <TrendingDown className="w-3.5 h-3.5" />
            Ahorrá hasta {savingsPercent}%
          </div>
        )}
      </div>

      <div className="space-y-3">
        {sorted.map((price) => {
          const config = getPlatformConfig(price.platform);
          const Icon = config.icon;
          const priceVal = price.price_converted ?? price.price_per_night;
          const isCheapest = price.id === cheapest.id;

          return (
            <a
              key={price.id}
              href={price.platform_url || "#"}
              target="_blank"
              rel="noopener noreferrer"
              className={`block rounded-xl p-5 transition-all group ${
                isCheapest
                  ? "bg-emerald-500/10 border-2 border-emerald-500/40"
                  : "bg-white/5 border border-white/10 hover:bg-white/10"
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-4 min-w-0">
                  <div
                    className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${config.bg}`}
                  >
                    <Icon className="w-5 h-5" style={{ color: config.color }} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold text-white capitalize">
                        {config.label}
                      </span>
                      {isCheapest && (
                        <span className="flex items-center gap-1 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded-full">
                          <Zap className="w-3 h-3" /> Mejor Precio
                        </span>
                      )}
                    </div>
                    {(price.room_type || price.max_guests > 1) && (
                      <p className="text-xs text-slate-400 mt-0.5">
                        {[price.room_type, price.max_guests > 1 ? `${price.max_guests} huéspedes` : ""]
                          .filter(Boolean)
                          .join(" · ")}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-4 shrink-0">
                  <div className="text-right">
                    <div className="text-2xl font-black text-white">
                      ${Math.round(priceVal).toLocaleString("es-AR")}
                    </div>
                    <div className="text-xs text-slate-400">
                      {price.currency} / noche
                    </div>
                  </div>

                  <div
                    className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
                      isCheapest
                        ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30 group-hover:bg-emerald-400"
                        : "bg-white/10 text-white border border-white/20 group-hover:bg-white/20 group-hover:border-white/30"
                    }`}
                  >
                    {isCheapest ? "Reservar" : "Ver"}
                    {isCheapest ? (
                      <ArrowRight className="w-4 h-4" />
                    ) : (
                      <ExternalLink className="w-3.5 h-3.5" />
                    )}
                  </div>
                </div>
              </div>

              {isCheapest && savings > 0 && (
                <div className="mt-3 pt-3 border-t border-emerald-500/20 flex items-center gap-2 text-xs text-emerald-400">
                  <TrendingDown className="w-3.5 h-3.5" />
                  Ahorrás ${Math.round(savings).toLocaleString("es-AR")} por noche respecto a otras plataformas
                </div>
              )}
            </a>
          );
        })}
      </div>
    </div>
  );
}
