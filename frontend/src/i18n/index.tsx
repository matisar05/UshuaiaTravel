/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, type ReactNode } from 'react';
import type { SupportedLocale } from './translations';
import { getTranslations } from './translations';

interface I18nContextValue {
  t: (key: string) => string;
  locale: SupportedLocale;
}

const I18nContext = createContext<I18nContextValue>({
  t: (key: string) => key,
  locale: 'es',
});

export function I18nProvider({ children, locale = 'es' }: { children: ReactNode; locale?: SupportedLocale }) {
  const translations = getTranslations(locale);
  const t = (key: string) => translations[key] || key;
  return (
    <I18nContext.Provider value={{ t, locale }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useTranslation() {
  return useContext(I18nContext);
}
