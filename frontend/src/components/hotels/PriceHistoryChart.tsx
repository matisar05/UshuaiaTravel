import { useState, useMemo } from "react";
import { TrendingDown } from "lucide-react";
import type { PriceHistoryEntry } from "@/types";
import { getPlatformConfig } from "@/constants/platforms";

interface PriceHistoryChartProps {
  history: PriceHistoryEntry[];
}

export default function PriceHistoryChart({ history }: PriceHistoryChartProps) {
  const [selectedPlatform, setSelectedPlatform] = useState<string>("all");

  const platforms = useMemo(() => {
    const set = new Set(history.map((h) => h.platform));
    return Array.from(set);
  }, [history]);

  const filtered = useMemo(() => {
    if (selectedPlatform === "all") return history;
    return history.filter((h) => h.platform === selectedPlatform);
  }, [history, selectedPlatform]);

  const chartData = useMemo(() => {
    if (filtered.length === 0) return null;

    const sorted = [...filtered].sort(
      (a, b) =>
        new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
    );
    const prices = sorted.map((h) => h.price_per_night);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min || 1;

    const points = sorted.map((h, i) => ({
      x: (i / (sorted.length - 1 || 1)) * 100,
      y: 100 - ((h.price_per_night - min) / range) * 80,
      ...h,
    }));

    const dates = sorted.map((h) => {
      const d = new Date(h.recorded_at);
      return `${d.getDate()}/${d.getMonth() + 1}`;
    });

    return { points, min, max, dates };
  }, [filtered]);

  if (!chartData) return null;

  const { points, min, max } = chartData;

  const lowest = points.find((p) => p.is_lowest_30d);
  const hasLowest = !!lowest;

  const linePath = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");

  const areaPath = `${linePath} L ${points[points.length - 1].x} 100 L ${points[0].x} 100 Z`;

  const first = points[0];
  const last = points[points.length - 1];
  const trend = last.price_per_night - first.price_per_night;
  const trendPercent = first.price_per_night > 0
    ? Math.round((trend / first.price_per_night) * 100)
    : 0;
  const isTrendDown = trend < 0;

  return (
    <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Historial de Precios</h2>
        <div className="flex items-center gap-2">
          {trend !== 0 && (
            <span
              className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                isTrendDown
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "bg-red-500/20 text-red-400"
              }`}
            >
              <TrendingDown
                className={`w-3 h-3 inline mr-1 ${isTrendDown ? "" : "rotate-180"}`}
              />
              {isTrendDown ? "↓" : "↑"} {Math.abs(trendPercent)}%
            </span>
          )}
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="bg-white/10 text-white text-xs border border-white/20 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-glacier-500/50"
          >
            <option value="all">Todas las plataformas</option>
            {platforms.map((p) => (
              <option key={p} value={p}>
                {getPlatformConfig(p).label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="relative h-48 mb-4">
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="w-full h-full"
        >
          <defs>
            <linearGradient id="priceArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgb(59 130 246)" stopOpacity="0.3" />
              <stop offset="100%" stopColor="rgb(59 130 246)" stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {[25, 50, 75].map((y) => (
            <line
              key={y}
              x1="0"
              y1={y}
              x2="100"
              y2={y}
              stroke="rgb(255 255 255 / 0.05)"
              strokeWidth="0.5"
            />
          ))}

          <path
            d={areaPath}
            fill="url(#priceArea)"
          />
          <path
            d={linePath}
            fill="none"
            stroke="rgb(59 130 246)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {points.map((p, i) =>
            p.is_lowest_30d ? (
              <circle
                key={i}
                cx={p.x}
                cy={p.y}
                r="3"
                fill="#10b981"
                stroke="white"
                strokeWidth="1"
              />
            ) : null
          )}

          {hasLowest && lowest && (
            <>
              <text
                x={Math.min(lowest.x + 4, 95)}
                y={lowest.y - 4}
                fill="#10b981"
                fontSize="6"
                fontWeight="bold"
              >
                ${Math.round(lowest.price_per_night).toLocaleString("es-AR")}
              </text>
              <line
                x1={lowest.x}
                y1={lowest.y}
                x2={lowest.x}
                y2="100"
                stroke="#10b981"
                strokeWidth="0.5"
                strokeDasharray="1 1"
              />
            </>
          )}
        </svg>
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>
          {chartData.dates[0]}
        </span>
        <span className="flex items-center gap-3">
          <span>Min: ${Math.round(min).toLocaleString("es-AR")}</span>
          <span>Max: ${Math.round(max).toLocaleString("es-AR")}</span>
        </span>
        <span>
          {chartData.dates[chartData.dates.length - 1]}
        </span>
      </div>
    </div>
  );
}
