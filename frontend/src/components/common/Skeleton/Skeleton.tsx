export function HotelCardSkeleton() {
  return (
    <div className="card bg-white animate-pulse">
      <div className="aspect-[16/10] bg-slate-200" />
      <div className="p-5 space-y-4">
        <div className="space-y-2">
          <div className="h-5 bg-slate-200 rounded w-3/4" />
          <div className="h-3 bg-slate-100 rounded w-1/2" />
        </div>
        <div className="h-8 bg-slate-100 rounded w-full" />
        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <div className="space-y-1.5">
            <div className="h-3 bg-slate-100 rounded w-12" />
            <div className="h-6 bg-slate-200 rounded w-24" />
          </div>
          <div className="h-10 bg-slate-200 rounded-xl w-28" />
        </div>
      </div>
    </div>
  );
}

export function HotelGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <HotelCardSkeleton key={i} />
      ))}
    </div>
  );
}
