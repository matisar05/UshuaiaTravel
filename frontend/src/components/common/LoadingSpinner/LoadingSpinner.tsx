import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function LoadingSpinner({ 
  message = 'Cargando información...', 
  size = 'md' 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  };

  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <Loader2 
        className={`${sizeClasses[size]} text-glacier-600 animate-spin`} 
        strokeWidth={2}
      />
      {message && (
        <p className="text-base font-medium text-slate-600">{message}</p>
      )}
    </div>
  );
}
