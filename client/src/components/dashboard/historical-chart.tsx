"use client"

import { useState } from "react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { CalendarIcon } from "lucide-react"
import { format } from "date-fns"
import { mockHistoricalData } from "@/lib/mock-data"
import { cn } from "@/lib/utils"

export function HistoricalChart() {
  const [dateRange, setDateRange] = useState<"30days" | "custom">("30days")
  const [startDate, setStartDate] = useState<Date>()
  const [endDate, setEndDate] = useState<Date>()

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Company Burnout Risk Over Time</CardTitle>
        <div className="flex items-center gap-2">
          <Button
            variant={dateRange === "30days" ? "default" : "outline"}
            size="sm"
            onClick={() => setDateRange("30days")}
          >
            Last 30 Days
          </Button>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant={dateRange === "custom" ? "default" : "outline"}
                size="sm"
                className="gap-2"
                onClick={() => setDateRange("custom")}
              >
                <CalendarIcon className="h-4 w-4" />
                {startDate && endDate
                  ? `${format(startDate, "MMM d")} - ${format(endDate, "MMM d")}`
                  : "Select Range"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <div className="flex flex-col sm:flex-row">
                <div className="p-3 border-b sm:border-b-0 sm:border-r">
                  <p className="text-sm font-medium mb-2">Start Date</p>
                  <Calendar
                    mode="single"
                    selected={startDate}
                    onSelect={setStartDate}
                    initialFocus
                  />
                </div>
                <div className="p-3">
                  <p className="text-sm font-medium mb-2">End Date</p>
                  <Calendar
                    mode="single"
                    selected={endDate}
                    onSelect={setEndDate}
                  />
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockHistoricalData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 12 }}
                className="text-muted-foreground"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "var(--radius)",
                }}
                labelStyle={{ color: "hsl(var(--foreground))" }}
              />
              <ReferenceLine y={75} stroke="hsl(0, 84%, 60%)" strokeDasharray="5 5" label={{ value: "Critical", position: "right", fill: "hsl(0, 84%, 60%)" }} />
              <ReferenceLine y={50} stroke="hsl(25, 95%, 53%)" strokeDasharray="5 5" label={{ value: "High", position: "right", fill: "hsl(25, 95%, 53%)" }} />
              <ReferenceLine y={25} stroke="hsl(48, 96%, 53%)" strokeDasharray="5 5" label={{ value: "Moderate", position: "right", fill: "hsl(48, 96%, 53%)" }} />
              <Line
                type="monotone"
                dataKey="score"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={{ fill: "hsl(var(--primary))", r: 4 }}
                activeDot={{ r: 6 }}
                name="Burnout Score"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 flex items-center justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-red-500" />
            <span className="text-muted-foreground">Critical (75+)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-orange-500" />
            <span className="text-muted-foreground">High (50-74)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-yellow-500" />
            <span className="text-muted-foreground">Moderate (25-49)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-green-500" />
            <span className="text-muted-foreground">Low (0-24)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
