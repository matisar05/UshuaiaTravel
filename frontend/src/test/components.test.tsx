import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HelmetProvider } from 'react-helmet-async';
import type { Hotel } from '@/types';
import HotelCard from '@/components/hotels/HotelCard/HotelCard';
import LoadingSpinner from '@/components/common/LoadingSpinner/LoadingSpinner';
import { HotelCardSkeleton } from '@/components/common/Skeleton/Skeleton';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>{children}</BrowserRouter>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

function renderWithProviders(ui: React.ReactElement) {
  return render(ui, { wrapper: Wrapper });
}

const mockHotel: Hotel = {
  id: 1,
  name: 'Hotel Glaciar',
  address: 'Av. San Martin 123, Ushuaia',
  hotel_type: 'hotel',
  type_display: 'Hotel',
  location_type: 'centro',
  location_display: 'Centro',
  stars: 4,
  pet_friendly: true,
  main_image: 'https://example.com/hotel1.jpg',
  min_price: 45000,
  target_currency: 'ARS',
  last_updated: new Date(Date.now() - 3 * 3600 * 1000).toISOString(),
  best_platform: 'Booking.com',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

describe('HotelCard', () => {
  it('renders hotel name', () => {
    renderWithProviders(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText('Hotel Glaciar')).toBeInTheDocument();
  });

  it('renders star rating icons', () => {
    renderWithProviders(<HotelCard hotel={mockHotel} />);
    const stars = screen.getAllByText('Hotel Glaciar');
    expect(stars[0]).toBeInTheDocument();
  });

  it('shows pet friendly badge', () => {
    renderWithProviders(<HotelCard hotel={mockHotel} />);
    expect(screen.getByTitle('Pet Friendly')).toBeInTheDocument();
  });

  it('shows best platform badge', () => {
    renderWithProviders(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText(/Booking\.com/)).toBeInTheDocument();
  });

  it('shows price formatted', () => {
    renderWithProviders(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText(/ARS/)).toBeInTheDocument();
    expect(screen.getByText(/45\.000/)).toBeInTheDocument();
  });

  it('has link to detail page', () => {
    renderWithProviders(<HotelCard hotel={mockHotel} />);
    const link = screen.getByRole('link', { name: /explorar/i });
    expect(link).toHaveAttribute('href', '/hoteles/1');
  });

  it('shows time ago for last updated', () => {
    renderWithProviders(<HotelCard hotel={mockHotel} />);
    expect(screen.getByText(/hace 3h/)).toBeInTheDocument();
  });

  it('handles missing image gracefully', () => {
    const noImg = { ...mockHotel, main_image: undefined };
    renderWithProviders(<HotelCard hotel={noImg} />);
    expect(screen.getByText('Hotel Glaciar')).toBeInTheDocument();
  });
});

describe('LoadingSpinner', () => {
  it('renders with default message', () => {
    render(<LoadingSpinner />);
    expect(screen.getByText('Cargando información...')).toBeInTheDocument();
  });

  it('renders with custom message', () => {
    render(<LoadingSpinner message="Buscando hoteles..." />);
    expect(screen.getByText('Buscando hoteles...')).toBeInTheDocument();
  });

  it('applies size classes', () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });
});

describe('HotelCardSkeleton', () => {
  it('renders without crashing', () => {
    const { container } = render(<HotelCardSkeleton />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });
});
