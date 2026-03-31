"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { getBurnoutLevel, getBurnoutColor } from "@/lib/mock-data"

interface BurnoutGaugeProps {
  score: number
  title?: string
  size?: "sm" | "lg"
}

export function BurnoutGauge({ score, title = "Burnout Score", size = "lg" }: BurnoutGaugeProps) {
  const level = getBurnoutLevel(score)
  const rotation = (score / 100) * 180 - 90 // -90 to 90 degrees

  const gaugeSize = size === "lg" ? "h-40 w-40" : "h-24 w-24"
  const fontSize = size === "lg" ? "text-4xl" : "text-2xl"
  const labelSize = size === "lg" ? "text-sm" : "text-xs"

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        <div className={cn("relative", gaugeSize)}>
          {/* Background arc */}
          <svg viewBox="0 0 100 50" className="w-full h-full overflow-visible">
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="hsl(142, 76%, 36%)" />
                <stop offset="25%" stopColor="hsl(48, 96%, 53%)" />
                <stop offset="50%" stopColor="hsl(25, 95%, 53%)" />
                <stop offset="100%" stopColor="hsl(0, 84%, 60%)" />
              </linearGradient>
            </defs>
            {/* Background track */}
            <path
              d="M 10 50 A 40 40 0 0 1 90 50"
              fill="none"
              stroke="hsl(var(--muted))"
              strokeWidth="8"
              strokeLinecap="round"
            />
            {/* Colored arc */}
            <path
              d="M 10 50 A 40 40 0 0 1 90 50"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${(score / 100) * 125.6} 125.6`}
            />
            {/* Needle */}
            <line
              x1="50"
              y1="50"
              x2="50"
              y2="15"
              stroke="hsl(var(--foreground))"
              strokeWidth="2"
              strokeLinecap="round"
              transform={`rotate(${rotation}, 50, 50)`}
            />
            <circle cx="50" cy="50" r="4" fill="hsl(var(--foreground))" />
          </svg>
        </div>
        <div className="mt-4 flex flex-col items-center">
          <span className={cn("font-bold", fontSize, {
            "text-green-500": level === "low",
            "text-yellow-500": level === "moderate",
            "text-orange-500": level === "high",
            "text-red-500": level === "critical",
          })}>
            {score}%
          </span>
          <span className={cn("capitalize mt-1", labelSize, getBurnoutColor(level).replace("bg-", "text-").split(" ")[0])}>
            {level} Risk
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
