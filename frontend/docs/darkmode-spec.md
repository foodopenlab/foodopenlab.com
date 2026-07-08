# FOODOPENLAB — 다크모드·라이트모드 구현 지시서

> **강사 원본:** 화이트 기본 + `dark:` 토글  
> **프로젝트 결정 (확정):** **기본값 = 라이트 모드** · **지금 설계된 UI = 라이트로 전환** · **다크 모드 = 신규 제작**

---

## ⚠️ 프로젝트 결정사항 (반드시 준수)

| 항목 | 결정 |
|------|------|
| **기본 테마** | **라이트 모드** (`defaultTheme="light"`) |
| **지금 설계된 인터페이스** | **라이트 모드로 수정** — 첫 방문·미설정 사용자는 밝은 UI를 본다 |
| **다크 모드** | **별도로 새로 만든다** — 토글 시에만 적용 |
| **코드 기준** | `:root` = 라이트 · `.dark` = 다크 |

### 왜 문서를 이렇게 쓰는가

코드(`app/globals.css`)에는 **아직** Dark Navy + Emerald가 `:root`에 들어 있어 **화면이 어둡게** 보인다.  
그러나 **제품 방향은 라이트 기본**이다. 따라서:

1. **지금 보이는 레이아웃·컴포넌트·브랜드(에메랄드)** 는 유지하되, **색만 라이트 팔레트로 재정의**한다.  
2. **현재 `:root`의 다크 색상값**은 **다크 모드(`.dark`)의 1차 베이스**로 옮긴다.  
3. 구현 완료 후 **기본 화면 = 라이트**, **토글 = 다크**가 된다.

> 이전 초안의「다크가 기본」설명은 **폐기**한다. 아래 to-be 기준만 따른다.

---

## 0. 현재 상태 (as-is) vs 목표 (to-be)

| 항목 | as-is (코드) | to-be (목표) |
|------|----------------|--------------|
| `:root` | Dark Navy + Emerald (어두움) | **라이트 팔레트** (밝은 배경) |
| `.dark` | `:root`와 거의 동일 | **다크 팔레트** (현 `:root` 값 이전 + 보완) |
| 기본 테마 | 사실상 다크 (`:root`만 적용) | **라이트** |
| `next-themes` | 미연결 | `defaultTheme="light"` |
| 토글 | 없음 | 해/달 → **다크 모드 진입** |

---

## 1. 기본 방침

| 항목 | 값 |
|------|-----|
| **기본 테마** | **`light`** |
| **토글** | 사용자가 **다크**로 전환 가능 |
| **제어** | `next-themes` + `<html class="dark">` (`attribute="class"`) |
| **Tailwind** | `@custom-variant dark (&:is(.dark *));` (v4, 설정 완료) |
| **컴포넌트 색** | 시맨틱 토큰 (`bg-background`, `text-foreground` …) **우선** |

강사 지시어의 `defaultTheme="light"`와 **방향 일치**.  
FOODOPENLAB은 gray/blue 대신 **에메랄드 브랜드**를 라이트·다크 양쪽에 각각 맞춘다.

---

## 2. 구현 순서 (권장)

```
1. app/globals.css
   - :root  ← 라이트 팔레트 (§3.2) — ★ 기본 UI가 여기로 바뀜
   - .dark  ← 다크 팔레트 (§3.3) — 현 :root 값 이전 + 다크 전용 보완

2. app/layout.tsx
   - ThemeProvider, defaultTheme="light"

3. components/theme/theme-toggle.tsx
   - 라이트(기본): Moon → 다크 전환
   - 다크: Sun → 라이트 전환

4. navigation.tsx, admin-header.tsx — 토글 배치

5. 하드코딩 색상·차트 oklch — 라이트/다크 각각 대비 점검

6. npm run build + 주요 페이지 시각 회귀
```

---

## 3. CSS 변수 구조 (핵심)

### 3.1 원칙

```
:root     → 라이트 모드 (= 지금 설계된 인터페이스를 밝게 재해석한 SSOT)
.dark     → 다크 모드 (= 신규 제작, 현 코드의 다크 색을 베이스로)
```

| 블록 | 역할 | 작업 |
|------|------|------|
| `:root` | **기본(라이트)** | 현 UI 설계 의도 유지 + **밝은 배경·진한 텍스트**로 토큰 재정의 |
| `.dark` | **토글(다크)** | `app/globals.css` **현재 `:root` 전체**를 이전한 뒤, 다크 전용으로 다듬기 |

### 3.2 라이트 모드 토큰 (`:root` — 기본 UI)

**지금 설계된 인터페이스를 라이트로 옮긴다** = 레이아웃·컴포넌트 구조는 그대로, **시맨틱 토큰만 밝은 톤**으로.

| 토큰 | 1차 값 | 용도 |
|------|--------|------|
| `--background` | `oklch(0.99 0.005 250)` | 페이지 배경 (밝은 회청白) |
| `--foreground` | `oklch(0.18 0.02 250)` | 본문 (다크 네이비 텍스트) |
| `--card` | `oklch(1 0 0)` | 카드·패널 (흰색) |
| `--card-foreground` | `oklch(0.18 0.02 250)` | 카드 텍스트 |
| `--primary` | `oklch(0.55 0.15 160)` | 브랜드 에메랄드 (라이트에서 가독성 확보) |
| `--primary-foreground` | `oklch(0.99 0 0)` | primary 위 텍스트 |
| `--secondary` | `oklch(0.96 0.01 250)` | 보조 배경 |
| `--muted` | `oklch(0.96 0.01 250)` | 비활성·힌트 배경 |
| `--muted-foreground` | `oklch(0.45 0.02 250)` | 보조 텍스트 |
| `--accent` | `oklch(0.55 0.15 160)` | 강조 (primary와 동일 계열) |
| `--border` | `oklch(0.90 0.01 250)` | 구분선 |
| `--input` | `oklch(0.94 0.01 250)` | 입력 필드 배경 |
| `--ring` | `oklch(0.55 0.15 160)` | 포커스 링 |

- sidebar·chart·destructive: `styles/globals.css` shadcn 라이트 `:root`를 참고하되 **primary/accent는 에메랄드** 유지.  
- 구현 후 **첫 방문 화면이 이 팔레트**여야 한다.

### 3.3 다크 모드 토큰 (`.dark` — 신규 제작)

**다크 모드는 새로 만든다.** 1차 베이스 = **현재 `app/globals.css`의 `:root` 블록** (Dark Navy + Emerald).

| 토큰 | 값 (현행 `:root`에서 이전) | 용도 |
|------|---------------------------|------|
| `--background` | `oklch(0.13 0.02 250)` | 페이지 배경 |
| `--foreground` | `oklch(0.95 0 0)` | 본문 텍스트 |
| `--card` | `oklch(0.16 0.02 250)` | 카드·패널 |
| `--primary` | `oklch(0.72 0.17 160)` | 에메랄드 (다크에서 밝게) |
| `--primary-foreground` | `oklch(0.13 0.02 250)` | primary 위 텍스트 |
| `--muted` | `oklch(0.22 0.02 250)` | 보조 배경 |
| `--muted-foreground` | `oklch(0.65 0 0)` | 보조 텍스트 |
| `--border` | `oklch(0.28 0.02 250)` | 구분선 |
| `--ring` | `oklch(0.72 0.17 160)` | 포커스 링 |

sidebar·chart 등 나머지 토큰도 **현 `:root` 전체를 `.dark`로 복사**한 뒤, 다크 전용으로만 미세 조정.

### 3.4 마이그레이션 스케치 (`app/globals.css`)

```css
/* 기본 = 라이트 (지금 설계 UI의 밝은 버전) */
:root {
  /* §3.2 라이트 토큰 */
}

/* 토글 = 다크 (신규 — 현 :root 다크 값 이전) */
.dark {
  /* §3.3 — 기존 :root 블록 (Dark Navy + Emerald) */
}

/* @custom-variant dark, @theme inline, @layer base 유지 */
```

**배포 시:** `ThemeProvider`의 `defaultTheme="light"`와 **함께** CSS를 배포한다.  
그렇지 않으면 `:root`만 바뀌어 잠깐 밝아 보이거나, 반대로 다크가 남을 수 있다.

---

## 4. next-themes 설정

```tsx
// app/layout.tsx
import { ThemeProvider } from "next-themes"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className="flex min-h-screen flex-col overflow-x-clip font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"       // ★ 기본값: 라이트
          enableSystem={false}       // 1차: OS 자동 전환 제외
          disableTransitionOnChange
          storageKey="foodopenlab-theme"
        >
          <RootNavigationGate />
          <div className="flex min-h-0 flex-1 flex-col">{children}</div>
        </ThemeProvider>
        {process.env.NODE_ENV === "production" && <Analytics />}
      </body>
    </html>
  )
}
```

| 옵션 | 값 |
|------|-----|
| `defaultTheme` | **`"light"`** |
| `enableSystem` | `false` (2차에서 `true` 검토) |

---

## 5. 테마 토글 컴포넌트

경로: `components/theme/theme-toggle.tsx`

```tsx
"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])
  if (!mounted) {
    return <Button variant="ghost" size="icon" className="size-10" aria-hidden />
  }

  const isDark = resolvedTheme === "dark"

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      className="size-10 rounded-full"
      aria-label={isDark ? "라이트 모드로 전환" : "다크 모드로 전환"}
      onClick={() => setTheme(isDark ? "light" : "dark")}
    >
      {isDark ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </Button>
  )
}
```

| 현재 테마 | 아이콘 | 클릭 시 |
|-----------|--------|---------|
| **라이트 (기본)** | Moon | → 다크 |
| **다크** | Sun | → 라이트 |

---

## 6. 토글 배치

| 위치 | 파일 |
|------|------|
| 공개 사이트 상단 | `components/landing/navigation.tsx` |
| 관리자 헤더 | `components/admin/admin-header.tsx` |

---

## 7. 컴포넌트 적용 패턴

### ✅ 권장

```tsx
<div className="bg-background text-foreground">
<div className="border-border bg-card/60">
<p className="text-muted-foreground">
<Button className="bg-primary text-primary-foreground">
```

시맨틱 토큰만 쓰면 라이트/다크 전환 시 **`dark:` 접두사 불필요**.

### ❌ 지양

```tsx
<div className="bg-white dark:bg-[#0a0a0a]">
```

### 하드코딩 점검

`bg-white`, `text-gray-`, 다크 전용 `oklch(...)` 인라인 → 토큰 또는 CSS 변수로 치환.  
Recharts·배지 등 **다크 기준 하드코딩 색**은 라이트에서 대비 깨질 수 있음 → 2차 점검.

---

## 8. 영역별 가이드

### 8.1 랜딩 / 공개

```tsx
<header className="sticky top-0 z-50 border-b border-border/60 bg-background/95 backdrop-blur-sm">
  <ThemeToggle />
</header>
```

### 8.2 관리자

`bg-card`, `bg-background`, `bg-muted/20` 등 시맨틱 클래스 유지.  
**라이트가 기본**이므로 관리자 대시보드도 첫 로드 시 밝은 톤이어야 한다.

### 8.3 차트·코드

- 라이트: 충분한 대비의 chart 색  
- 다크: 현행 oklch 차트 팔레트 유지

### 8.4 파비콘

`layout.tsx` metadata의 `prefers-color-scheme` 아이콘 — 테마 토글과 동기화는 **2차**.

---

## 9. 이미지

```tsx
<img className="dark:opacity-80 dark:brightness-90" src="…" />
```

---

## 10. 검증 체크리스트

- [ ] 첫 방문(시크릿) → **라이트 UI** (밝은 배경)
- [ ] 토글 → **다크** 전환 시 현재(구) 다크 네이비 느낌과 유사
- [ ] 토글 → 라이트 복귀 정상
- [ ] 새로고침 후 선택 테마 유지 (`foodopenlab-theme`)
- [ ] `/`, `/admin`, `/recalls`, `/supplier` 등 주요 페이지 대비·가독성
- [ ] hydration 경고 없음
- [ ] `npm run build` 성공

---

## 11. 요약 — 한 줄 지시 (에이전트·구현용)

> **기본값은 라이트(`defaultTheme="light"`). `app/globals.css`의 `:root`를 라이트 팔레트(§3.2)로 바꿔 지금 설계된 UI를 밝은 테마로 만든다. 현재 `:root`의 다크 색은 `.dark`(§3.3)로 옮겨 다크 모드를 신규 제작한다. `ThemeToggle`로 라이트↔다크 전환. 컴포넌트는 `bg-background` 등 시맨틱 토큰 유지.**

---

## 부록 A — 강사 원본 · 이전 초안 · 확정안

| 구분 | 기본 테마 | `:root` | `.dark` |
|------|-----------|---------|---------|
| 강사 원본 | 라이트 | 라이트 gray/blue | 다크 gray |
| 이전 초안 (폐기) | 다크 | 라이트 신규 | 현 UI |
| **확정 (본 문서)** | **라이트** | **지금 설계 UI → 라이트로 수정** | **다크 신규 제작** |

## 부록 B — 관련 파일

| 파일 | 역할 |
|------|------|
| `app/globals.css` | `:root`(라이트) / `.dark`(다크) SSOT |
| `styles/globals.css` | shadcn 라이트 참고용 |
| `app/layout.tsx` | `ThemeProvider`, `defaultTheme="light"` |
| `components/landing/navigation.tsx` | 공개 토글 |
| `components/admin/admin-header.tsx` | 관리자 토글 |


## 다크모드
