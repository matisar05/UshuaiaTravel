import { apiClient } from './client';
import type {
  Hotel,
  Price,
  PriceComparison,
  HotelFilters,
  PaginatedResponse,
} from '@/types';

export const hotelsApi = {
  /**
   * Get paginated list of hotels with optional filters
   */
  getAll: async (params?: HotelFilters): Promise<PaginatedResponse<Hotel>> => {
    const { data } = await apiClient.get<PaginatedResponse<Hotel>>('/hotels/', { params });
    return data;
  },

  /**
   * Get a single hotel by ID
   */
  getById: async (id: number): Promise<Hotel> => {
    const { data } = await apiClient.get<Hotel>(`/hotels/${id}/`);
    return data;
  },

  /**
   * Get featured/highlighted hotels
   */
  getFeatured: async (): Promise<Hotel[]> => {
    const { data } = await apiClient.get<Hotel[]>('/hotels/featured/');
    return data;
  },

  /**
   * Compare prices across platforms for a specific hotel
   */
  comparePrices: async (id: number): Promise<PriceComparison> => {
    const { data } = await apiClient.get<PriceComparison>(`/hotels/${id}/compare_prices/`);
    return data;
  },
};

export const pricesApi = {
  /**
   * Get all prices
   */
  getAll: async (): Promise<PaginatedResponse<Price>> => {
    const { data} = await apiClient.get<PaginatedResponse<Price>>('/prices/');
    return data;
  },
};
