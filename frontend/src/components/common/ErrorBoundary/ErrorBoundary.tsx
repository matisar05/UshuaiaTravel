import { Component, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';
import { ROUTES } from '@/constants/routes';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6">
          <div className="text-center max-w-md">
            <AlertTriangle className="w-16 h-16 text-amber-500 mx-auto mb-6" />
            <h1 className="text-3xl font-bold text-white mb-4">Algo salió mal</h1>
            <p className="text-slate-400 mb-8">
              Ocurrió un error inesperado. Por favor, intentá de nuevo.
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={this.handleReset}
                className="bg-glacier-500 text-white px-6 py-3 rounded-xl font-semibold hover:bg-glacier-600 transition"
              >
                Reintentar
              </button>
              <Link
                to={ROUTES.HOME}
                className="bg-white/10 text-white px-6 py-3 rounded-xl font-semibold hover:bg-white/20 transition"
              >
                Volver al inicio
              </Link>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
