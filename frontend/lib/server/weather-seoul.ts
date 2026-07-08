/** 서울 현재 날씨 — OpenWeatherMap Current Weather API */

export type SeoulWeatherPayload = {
  city: string
  temp_c: number
  description: string
  icon: string
}

const OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

export async function getSeoulWeather(): Promise<SeoulWeatherPayload> {
  const apiKey = process.env.WEATHER_API_KEY?.trim() ?? ""
  if (!apiKey) {
    throw new Error("WEATHER_API_KEY가 설정되지 않았습니다.")
  }

  const url = new URL(OPEN_WEATHER_URL)
  url.searchParams.set("q", "Seoul,KR")
  url.searchParams.set("appid", apiKey)
  url.searchParams.set("units", "metric")
  url.searchParams.set("lang", "kr")

  const res = await fetch(url.toString(), {
    cache: "no-store",
    signal: AbortSignal.timeout(12_000),
  })

  if (!res.ok) {
    const body = await res.text().catch(() => "")
    throw new Error(`OpenWeather HTTP ${res.status}${body ? `: ${body.slice(0, 120)}` : ""}`)
  }

  const data = (await res.json()) as {
    name?: string
    main?: { temp?: number }
    weather?: Array<{ description?: string; icon?: string }>
  }

  const w = data.weather?.[0]
  const temp = data.main?.temp
  if (temp == null || !w?.icon) {
    throw new Error("OpenWeather 응답 형식이 올바르지 않습니다.")
  }

  return {
    city: data.name?.trim() || "Seoul",
    temp_c: Math.round(temp),
    description: (w.description || "").trim() || "—",
    icon: w.icon,
  }
}
