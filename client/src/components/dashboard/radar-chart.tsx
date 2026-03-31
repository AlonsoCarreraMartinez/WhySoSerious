"use client"

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface RadarChartProps {
  exhaustion: number
  cynicism: number
  inefficacy: number
  title?: string
}

export function BurnoutRadarChart({
  exhaustion,
  cynicism,
  inefficacy,
  title = "Burnout Dimensions",
}: RadarChartProps) {
  const data = [
    { dimension: "Exhaustion", value: exhaustion, fullMark: 100 },
    { dimension: "Cynicism", value: cynicism, fullMark: 100 },
    { dimension: "Inefficacy", value: inefficacy, fullMark: 100 },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
              <PolarGrid className="stroke-muted" />
              <PolarAngleAxis
                dataKey="dimension"
                tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
              />
              <Radar
                name="Score"
                dataKey="value"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.3}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
