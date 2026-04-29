import { useEffect } from 'react';

interface AdSenseProps {
  slot?: string;
  format?: 'auto' | 'rectangle' | 'horizontal' | 'vertical';
  className?: string;
}

const CLIENT_ID = import.meta.env.VITE_ADSENSE_CLIENT || '';

declare global {
  interface Window {
    adsbygoogle: Array<Record<string, unknown>>;
  }
}

export default function GoogleAdSense({ slot, format = 'auto', className = '' }: AdSenseProps) {
  useEffect(() => {
    if (!CLIENT_ID) return;
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch {
      // AdSense push failed (no script loaded or ad blocked)
    }
  }, []);

  if (!CLIENT_ID) return null;

  return (
    <div className={className}>
      <ins
        className="adsbygoogle"
        style={{ display: 'block' }}
        data-ad-client={CLIENT_ID}
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive="true"
      />
    </div>
  );
}
