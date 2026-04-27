// Core Hotel Types
export interface Hotel {
  id: number;
  name: string;
  description?: string;
  description_short?: string;
  address: string;
  hotel_type: HotelType;
  type_display: string;
  location_type: LocationType;
  location_display: string;
  stars: number;
  pet_friendly: boolean;
  amenities?: Record<string, boolean> | string[];
  contact_info?: {
    phone?: string;
    email?: string;
    website?: string;
  };
  images?: string[];
  main_image?: string;
  latitude?: number;
  longitude?: number;
  min_price?: number;
  price_range?: {
    min: number;
    max: number;
  };
  created_at: string;
  updated_at: string;
}

// Price Information
export interface Price {
  id: number;
  hotel: number;
  platform: Platform;
  platform_url: string;
  price_per_night: number;
  currency: Currency;
  room_type?: string;
  max_guests: number;
  is_available: boolean;
  last_checked: string;
  notes?: string;
}

// Price Comparison Response
export interface PriceComparison {
  hotel_id: number;
  hotel_name: string;
  comparison: Record<string, Price[]>;
  cheapest: Price | null;
}

// Enums
export type HotelType = 'hotel' | 'hostel' | 'apart' | 'cabaña' | 'casa';
export type LocationType = 'centro' | 'afueras' | 'montaña';
export type Platform = 'booking' | 'airbnb' | 'tripadvisor' | 'local' | 'direct';
export type Currency = 'ARS' | 'USD' | 'EUR';

// Filter Parameters
export interface HotelFilters {
  hotel_type?: HotelType;
  location_type?: LocationType;
  stars?: number;
  min_stars?: number;
  pet_friendly?: boolean;
  min_price?: number;
  max_price?: number;
  search?: string;
  ordering?: string;
  page?: number;
  checkin?: string;
  checkout?: string;
  guests?: number;
}

// API Response Types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
