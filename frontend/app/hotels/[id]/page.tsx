import dynamic from 'next/dynamic'

const DynamicMap = dynamic(() => import('@/components/organisms/HotelMap'), {
  ssr: false,
  loading: () => <div className="h-64 w-full animate-pulse bg-gray-200 rounded-lg" />
})

export const revalidate = 3600;

export async function generateStaticParams() {
    const hotels = await fetch('https://api.ushuaia.travel/v1/hotels/').then(res => res.json());
    return hotels.map((hotel) => ({
        id: hotel.external_id,
    }));
}

export default function HotelPage({ params }: { params: { id: string } }) {
    return (
        <div>
            <DynamicMap />
        </div>
    )
}
