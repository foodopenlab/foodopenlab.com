"use client"

import { useEffect, useState } from "react"
import { apiPath } from "@/lib/api-path"
import { cn } from "@/lib/utils"

type SeoulWeather = {
  city: string
  temp_c: number
  description: string
  icon: string
}

const WEATHER_API_URL = apiPath("weather/seoul")

export function SeoulWeatherNav({ className }: { className?: string }) {
  const [weather, setWeather] = useState<SeoulWeather | null>(null)

  useEffect(() => {
    let cancelled = false

    fetch(WEATHER_API_URL)
      .then(async (res) => {
        if (!res.ok) return null
        return (await res.json()) as SeoulWeather
      })
      .then((data) => {
        if (!cancelled && data) setWeather(data)
      })
      .catch(() => {})

    return () => {
      cancelled = true
    }
  }, [])

  if (!weather) return null

  return (
    <div
      className={cn(
        "flex items-center gap-1.5 rounded-full border border-border/60 bg-secondary/40 px-2.5 py-1.5 text-sm text-foreground",
        className,
      )}
      title={`${weather.city} · ${weather.description}`}
      aria-label={`${weather.city} 날씨 ${weather.temp_c}도, ${weather.description}`}
    >
      <img
        src={`https://openweathermap.org/img/wn/${weather.icon}@2x.png`}
        alt=""
        width={28}
        height={28}
        className="h-7 w-7 shrink-0"
        aria-hidden
      />
      <span className="font-medium tabular-nums">{weather.temp_c}°</span>
    </div>
  )
}
