"use client"

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface RadarChartProps {
  exhaustion: number
  cynicism: number
  inefficacy: number
  title?: string
  isContextMode?: boolean
  contextMetrics?: {
    avg_overtime: number
    avg_density: number
    avg_latency: number
  }
}

export function BurnoutRadarChart({
  exhaustion,
  cynicism,
  inefficacy,
  title = "Burnout Dimensions",
  isContextMode = false,
  contextMetrics,
}: RadarChartProps) {
  const data = [
    { dimension: "Exhaustion", value: exhaustion, fullMark: 100 },
    { dimension: "Cynicism", value: cynicism, fullMark: 100 },
    { dimension: "Inefficacy", value: inefficacy, fullMark: 100 },
  ]

  const getOvertimeLabel = (val: number) => {
    if (val >= 1.2) return "Weekend"
    if (val >= 1.1) return "After Hours"
    return "Work Hours"
  }

  return (
    <Card className="flex flex-col h-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col justify-between flex-1">
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

        {isContextMode && contextMetrics && (
          <div className="mt-4 grid grid-cols-3 gap-2 border-t pt-4 text-center">
            <div>
              <p className="text-xs text-muted-foreground">Overtime</p>
              <p className="font-medium text-sm text-foreground">
                {getOvertimeLabel(contextMetrics.avg_overtime)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Density</p>
              <p className="font-medium text-sm text-foreground">
                {contextMetrics.avg_density} msg/min
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Latency</p>
              <p className="font-medium text-sm text-foreground">
                {contextMetrics.avg_latency} min/msg
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}