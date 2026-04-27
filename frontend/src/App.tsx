import { Routes, Route } from 'react-router-dom'
import ScrollToTop from './components/common/ScrollToTop/ScrollToTop'
import HomePage from './pages/HomePage/HomePage'
import HotelsPage from './pages/HotelsPage/HotelsPage'
import HotelDetailPage from './pages/HotelDetailPage/HotelDetailPage'
import DonatePage from './pages/DonatePage/DonatePage'

function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/hoteles" element={<HotelsPage />} />
        <Route path="/hotel/:id" element={<HotelDetailPage />} />
        <Route path="/donar" element={<DonatePage />} />
      </Routes>
    </>
  )
}

export default App

