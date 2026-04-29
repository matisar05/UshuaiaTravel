import {
  Building2,
  Home,
  Compass,
  Globe,
  Building,
  Plane,
  Briefcase,
  CloudSun,
} from "lucide-react";
import type { Platform } from "@/types";
import type { ComponentType } from "react";

export interface PlatformConfig {
  label: string;
  icon: ComponentType<{ className?: string }>;
  color: string;
  bg: string;
  border: string;
}

const PLATFORM_MAP: Record<Platform, PlatformConfig> = {
  booking: {
    label: "Booking.com",
    icon: Building2,
    color: "#003580",
    bg: "bg-[#003580]/10",
    border: "border-[#003580]/30",
  },
  airbnb: {
    label: "Airbnb",
    icon: Home,
    color: "#FF5A5F",
    bg: "bg-[#FF5A5F]/10",
    border: "border-[#FF5A5F]/30",
  },
  tripadvisor: {
    label: "TripAdvisor",
    icon: Compass,
    color: "#00AF87",
    bg: "bg-[#00AF87]/10",
    border: "border-[#00AF87]/30",
  },
  despegar: {
    label: "Despegar",
    icon: Plane,
    color: "#4B0082",
    bg: "bg-[#4B0082]/10",
    border: "border-[#4B0082]/30",
  },
  expedia: {
    label: "Expedia",
    icon: Briefcase,
    color: "#FFC107",
    bg: "bg-[#FFC107]/10",
    border: "border-[#FFC107]/30",
  },
  amadeus: {
    label: "Amadeus",
    icon: CloudSun,
    color: "#2563EB",
    bg: "bg-blue-600/10",
    border: "border-blue-600/30",
  },
  local: {
    label: "Sitio Local",
    icon: Globe,
    color: "#64748b",
    bg: "bg-slate-500/10",
    border: "border-slate-500/30",
  },
  direct: {
    label: "Sitio Oficial",
    icon: Building,
    color: "#64748b",
    bg: "bg-slate-500/10",
    border: "border-slate-500/30",
  },
};

export function getPlatformConfig(platform: Platform): PlatformConfig {
  return PLATFORM_MAP[platform] ?? PLATFORM_MAP.direct;
}
