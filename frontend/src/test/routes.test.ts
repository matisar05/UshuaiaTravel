import { describe, it, expect } from 'vitest';
import { ROUTES, buildHotelDetailRoute, buildSearchRoute } from '@/constants/routes';

describe('ROUTES', () => {
  it('has all expected routes', () => {
    expect(ROUTES.HOME).toBe('/');
    expect(ROUTES.HOTELES).toBe('/hoteles');
    expect(ROUTES.DONAR).toBe('/donar');
    expect(ROUTES.HOTEL_DETAIL).toBe('/hoteles/:id');
  });
});

describe('buildHotelDetailRoute', () => {
  it('builds correct URL for numeric id', () => {
    expect(buildHotelDetailRoute(5)).toBe('/hoteles/5');
  });

  it('builds correct URL for string id', () => {
    expect(buildHotelDetailRoute('arakur-ushuaia')).toBe('/hoteles/arakur-ushuaia');
  });
});

describe('buildSearchRoute', () => {
  it('builds search URL with encoded query', () => {
    const url = buildSearchRoute('cerro castor');
    expect(url).toContain('/hoteles?search=');
    expect(url).toContain('cerro%20castor');
  });
});
