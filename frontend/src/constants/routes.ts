export const ROUTES = {
  HOME: '/',
  HOTELES: '/hoteles',
  HOTEL_DETAIL: '/hoteles/:id',
  DONAR: '/donar',
  GUIA: '/guia-ushuaia',
} as const;

export const buildHotelDetailRoute = (id: number | string) => `/hoteles/${id}`;
export const buildSearchRoute = (search: string) => `/hoteles?search=${encodeURIComponent(search)}`;
