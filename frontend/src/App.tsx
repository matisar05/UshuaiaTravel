import { Routes, Route } from 'react-router-dom'
import ScrollToTop from '@/components/common/ScrollToTop/ScrollToTop'
import { ErrorBoundary } from '@/components/common/ErrorBoundary/ErrorBoundary'
import AppShell from '@/components/layout/AppShell/AppShell'
import HomePage from '@/pages/HomePage/HomePage'
import HotelsPage from '@/pages/HotelsPage/HotelsPage'
import HotelDetailPage from '@/pages/HotelDetailPage/HotelDetailPage'
import DonatePage from '@/pages/DonatePage/DonatePage'
import GuiaPage from '@/pages/GuiaPage/GuiaPage'
import { ROUTES } from '@/constants/routes'

function App() {
  return (
    <ErrorBoundary>
      <ScrollToTop />
      <Routes>
        <Route path={ROUTES.HOME} element={<HomePage />} />
        <Route element={<AppShell />}>
          <Route path={ROUTES.HOTELES} element={<HotelsPage />} />
          <Route path={ROUTES.HOTEL_DETAIL} element={<HotelDetailPage />} />
          <Route path={ROUTES.DONAR} element={<DonatePage />} />
          <Route path={ROUTES.GUIA} element={<GuiaPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  )
}

export default App
