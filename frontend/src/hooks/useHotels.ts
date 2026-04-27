import { useQuery } from '@tanstack/react-query';
import { hotelsApi } from '@/api/hotels';
import type { HotelFilters } from '@/types';

/**
 * Fetch paginated list of hotels with filters
 */
export const useHotels = (filters?: HotelFilters) => {
  return useQuery({
    queryKey: ['hotels', filters],
    queryFn: () => hotelsApi.getAll(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  });
};

/**
 * Fetch a single hotel by ID
 */
export const useHotel = (id: number) => {
  return useQuery({
    queryKey: ['hotels', id],
    queryFn: () => hotelsApi.getById(id),
    staleTime: 5 * 60 * 1000,
    enabled: !!id, // Only fetch if ID exists
  });
};

/**
 * Fetch featured/highlighted hotels
 */
export const useFeaturedHotels = () => {
  return useQuery({
    queryKey: ['hotels', 'featured'],
    queryFn: () => hotelsApi.getFeatured(),
    staleTime: 10 * 60 * 1000, // 10 minutes (featured hotels don't change often)
  });
};

/**
 * Fetch price comparison for a hotel
 */
export const usePriceComparison = (hotelId: number) => {
  return useQuery({
    queryKey: ['hotels', hotelId, 'prices'],
    queryFn: () => hotelsApi.comparePrices(hotelId),
    staleTime: 5 * 60 * 1000,
    enabled: !!hotelId,
  });
};

