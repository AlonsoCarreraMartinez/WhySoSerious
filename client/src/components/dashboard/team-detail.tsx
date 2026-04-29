"use client"

import { useState, useEffect, useRef } from "react"
import { ArrowLeft, Eye, EyeOff, Users, Globe, CalendarIcon, Search } from "lucide-react"
import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Legend
} from "recharts"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Input } from "@/components/ui/input"
import { format } from "date-fns"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { BurnoutCard } from "./burnout-card"
import { BurnoutGauge } from "./burnout-gauge"
import { BurnoutRadarChart } from "./radar-chart"
import { useDashboard } from "@/lib/dashboard-context"
import { api } from "@/lib/api"

function VisibilityBadge({ visibility }: { visibility: string }) {
  const Icon = visibility === "org-wide" ? Globe : visibility === "public" ? Eye : EyeOff
  return (
    <Badge variant="secondary" className="flex items-center gap-1">
      <Icon className="h-3 w-3" />
      {visibility === "org-wide" ? "Org-wide" : visibility}
    </Badge>
  )
}

export function TeamDetail() {
  const { selectedTeamId, navigateToDashboard, navigateToChannel, isContextMode } = useDashboard()
  const [startDate, setStartDate] = useState<Date>()
  const [endDate, setEndDate] = useState<Date>()
  const [channelSearchQuery, setChannelSearchQuery] = useState("")
  const loadedTeamId = useRef<string | null>(null)

  const [team, setTeam] = useState<any>(null)
  const [channels, setChannels] = useState<any[]>([])
  const [members, setMembers] = useState<any[]>([])
  const [dimensionHistory, setDimensionHistory] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const getOvertimeLabel = (val: number) => {
    if (val >= 1.2) return "Weekend"
    if (val >= 1.1) return "After Hours"
    return "Work Hours"
  }

  const formatDimensionTooltip = (value: any, name: any, props: any) => {
    if (!isContextMode || !props.payload.context) return [value, name]
    const ctx = props.payload.context
    if (name === "Exhaustion") return [`${value} / Overtime: ${getOvertimeLabel(ctx.avg_overtime)}`, name]
    if (name === "Cynicism") return [`${value} / Latency: ${ctx.avg_latency} min/msg`, name]
    if (name === "Inefficacy") return [`${value} / Density: ${ctx.avg_density} msg/min`, name]
    return [value, name]
  }

  const formatOverallTooltip = (value: any, name: any, props: any) => {
    if (!isContextMode || !props.payload.context) return [value, name]
    const ctx = props.payload.context
    return [`${value} / Overtime: ${getOvertimeLabel(ctx.avg_overtime)} / Density: ${ctx.avg_density} / Latency: ${ctx.avg_latency}`, name]
  }

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedTeamId || selectedTeamId === "undefined") {
        navigateToDashboard()
        return
      }

      try {
        const isNewTeam = loadedTeamId.current !== selectedTeamId
        if (isNewTeam) {
          loadedTeamId.current = selectedTeamId
        }

        const startStr = startDate ? startDate.toISOString() : undefined
        const endStr = endDate ? new Date(endDate.setHours(23, 59, 59, 999)).toISOString() : undefined

        if (isNewTeam) {
          const fetchedTeam = await api.getTeamDetail(selectedTeamId)
          setTeam(fetchedTeam)

          const [fetchedChannels, fetchedMembers, fetchedHistory] = await Promise.all([
            api.getTeamChannels(selectedTeamId).catch(() => []),
            api.getTeamMembers(selectedTeamId).catch(() => []),
            api.getHistoricalData(selectedTeamId, startStr, endStr).catch(() => [])
          ])

          setChannels(fetchedChannels)
          setMembers(fetchedMembers)

          const formattedHistory = (fetchedHistory || []).map((point: any) => ({
            date: point.date,
            overall: point.score || 0,
            exhaustion: point.exhaustion || 0,
            cynicism: point.cynicism || 0,
            inefficacy: point.inefficacy || 0,
            wbi: point.wbi || point.score || 0,
            wbi_e: point.wbi_e || point.exhaustion || 0,
            wbi_c: point.wbi_c || point.cynicism || 0,
            wbi_i: point.wbi_i || point.inefficacy || 0,
            context: point.context || null
          }))

          setDimensionHistory(formattedHistory)
        } else {
          const [fetchedTeam, fetchedChannels, fetchedMembers, fetchedHistory] = await Promise.all([
            api.getTeamDetail(selectedTeamId).catch(() => team),
            api.getTeamChannels(selectedTeamId).catch(() => channels),
            api.getTeamMembers(selectedTeamId).catch(() => members),
            api.getHistoricalData(selectedTeamId, startStr, endStr).catch(() => [])
          ])

          if (fetchedTeam) setTeam(fetchedTeam)
          setChannels(fetchedChannels)
          setMembers(fetchedMembers)

          const formattedHistory = (fetchedHistory || []).map((point: any) => ({
            date: point.date,
            overall: point.score || 0,
            exhaustion: point.exhaustion || 0,
            cynicism: point.cynicism || 0,
            inefficacy: point.inefficacy || 0,
            wbi: point.wbi || point.score || 0,
            wbi_e: point.wbi_e || point.exhaustion || 0,
            wbi_c: point.wbi_c || point.cynicism || 0,
            wbi_i: point.wbi_i || point.inefficacy || 0,
            context: point.context || null
          }))
          
          setDimensionHistory(formattedHistory)
        }

      } catch (error) {
        setTeam(null)
      } finally {
        setIsLoading(false)
      }
    }

    if (selectedTeamId && selectedTeamId !== "undefined") {
      if (loadedTeamId.current !== selectedTeamId) {
        setIsLoading(true)
      }
      fetchData()
      
      const intervalId = setInterval(fetchData, 300000)
      return () => clearInterval(intervalId)
    }
  }, [selectedTeamId, navigateToDashboard, startDate, endDate])

  const handleResetDates = () => {
    setStartDate(undefined)
    setEndDate(undefined)
  }

  if (!selectedTeamId || selectedTeamId === "undefined") return null

  if (isLoading) {
    return <div className="flex h-full items-center justify-center p-6 text-muted-foreground">Loading team details...</div>
  }

  if (!team) {
    return (
      <div className="p-6 flex flex-col items-start gap-4">
        <h2 className="text-xl font-bold">Team not found or error loading data</h2>
        <Button onClick={navigateToDashboard}>Return to Dashboard</Button>
      </div>
    )
  }

  const managers = members.filter((m) => m.role.toLowerCase() === "manager")
  const regularMembers = members.filter((m) => m.role.toLowerCase() === "member")
  const filteredChannels = channels.filter(c => c.name.toLowerCase().includes(channelSearchQuery.toLowerCase()))

  return (
    <div className="flex flex-col gap-6 p-6" role="main">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={navigateToDashboard}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-foreground">{team.name}</h1>
            <VisibilityBadge visibility={team.visibility} />
          </div>
          <p className="text-muted-foreground flex items-center gap-1 mt-1">
            <Users className="h-4 w-4" />
            {team.memberCount} members
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <BurnoutGauge score={isContextMode ? (team.wbi ?? team.burnoutScore) : team.burnoutScore} title="Team Burnout Mean" />
        <BurnoutRadarChart
          exhaustion={isContextMode ? (team.wbi_e ?? team.exhaustion) : team.exhaustion}
          cynicism={isContextMode ? (team.wbi_c ?? team.cynicism) : team.cynicism}
          inefficacy={isContextMode ? (team.wbi_i ?? team.inefficacy) : team.inefficacy}
          title="Burnout Dimensions Comparison"
          isContextMode={isContextMode}
          contextMetrics={team.context}
        />
      </div>

      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="channels" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="channels">Channels</TabsTrigger>
              <TabsTrigger value="members">Members</TabsTrigger>
              <TabsTrigger value="burnout">Burnout</TabsTrigger>
              <TabsTrigger value="metrics">Metrics</TabsTrigger>
            </TabsList>

            <TabsContent value="channels">
              <div className="flex items-center gap-4 mb-6">
                <div className="relative flex-1 max-w-sm">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input 
                    placeholder="Search channels..." 
                    value={channelSearchQuery}
                    onChange={(e) => setChannelSearchQuery(e.target.value)}
                    className="pl-8"
                  />
                </div>
                <span className="text-sm text-muted-foreground">
                  {filteredChannels.length} of {channels.length} channels
                </span>
              </div>
              {filteredChannels.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {filteredChannels.map((channel) => (
                    <BurnoutCard
                      key={channel.id}
                      name={channel.name}
                      visibility={channel.visibility}
                      memberCount={channel.memberCount}
                      burnoutScore={isContextMode ? (channel.wbi ?? channel.burnoutScore) : channel.burnoutScore}
                      burnoutLevel={channel.burnoutLevel}
                      onClick={() => navigateToChannel(channel.id)}
                    />
                  ))}
                </div>
              ) : (
                <div className="py-8 text-center">
                  <p className="text-muted-foreground">No channels found</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="members">
              {members.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {managers.map((member) => (
                      <TableRow key={member.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar className="h-8 w-8">
                              <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                                {member.name.split(" ").map((n: string) => n[0]).join("")}
                              </AvatarFallback>
                            </Avatar>
                            <span className="font-medium">{member.name}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground">{member.email}</TableCell>
                        <TableCell>
                          <Badge variant="default">Manager</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                    {regularMembers.map((member) => (
                      <TableRow key={member.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <Avatar className="h-8 w-8">
                              <AvatarFallback className="bg-secondary text-secondary-foreground text-xs">
                                {member.name.split(" ").map((n: string) => n[0]).join("")}
                              </AvatarFallback>
                            </Avatar>
                            <span className="font-medium">{member.name}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground">{member.email}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">Member</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="py-8 text-center">
                  <p className="text-muted-foreground">No member data</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="burnout">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">Team Burnout Evolution</h3>
                    <p className="text-sm text-muted-foreground">Historical burnout index</p>
                  </div>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" size="sm" className="gap-2">
                        <CalendarIcon className="h-4 w-4" />
                        {startDate && endDate
                          ? `${format(startDate, "MMM d")} - ${format(endDate, "MMM d")}`
                          : "Select Dates"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="end">
                      <div className="flex flex-col sm:flex-row">
                        <div className="p-3 border-b sm:border-b-0 sm:border-r">
                          <p className="text-sm font-medium mb-2">Start Date</p>
                          <Calendar mode="single" selected={startDate} onSelect={setStartDate} />
                        </div>
                        <div className="p-3">
                          <p className="text-sm font-medium mb-2">End Date</p>
                          <Calendar mode="single" selected={endDate} onSelect={setEndDate} />
                        </div>
                      </div>
                      <div className="p-2 border-t flex justify-center bg-muted/20">
                        <Button variant="ghost" size="sm" className="w-full text-muted-foreground" onClick={handleResetDates}>
                          Reset Dates
                        </Button>
                      </div>
                    </PopoverContent>
                  </Popover>
                </div>
                
                {dimensionHistory.length > 0 ? (
                  <>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={dimensionHistory} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                          <defs>
                            <linearGradient id="colorOverall" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="hsl(0, 84%, 60%)" stopOpacity={0.4}/>
                              <stop offset="50%" stopColor="hsl(25, 95%, 53%)" stopOpacity={0.4}/>
                              <stop offset="95%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0.4}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                          <XAxis dataKey="date" tick={{ fontSize: 12 }} className="text-muted-foreground" />
                          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} className="text-muted-foreground" yAxisId="left" />
                          <YAxis domain={[0, 100]} yAxisId="right" orientation="right" tick={false} axisLine={false} />
                          <ReferenceLine y={75} yAxisId="left" stroke="hsl(0, 84%, 60%)" strokeDasharray="5 5" label={{ value: "Critical", position: "right", fill: "hsl(0, 84%, 60%)", fontSize: 11 }} />
                          <ReferenceLine y={50} yAxisId="left" stroke="hsl(25, 95%, 53%)" strokeDasharray="5 5" label={{ value: "High", position: "right", fill: "hsl(25, 95%, 53%)", fontSize: 11 }} />
                          <ReferenceLine y={25} yAxisId="left" stroke="hsl(48, 96%, 53%)" strokeDasharray="5 5" label={{ value: "Moderate", position: "right", fill: "hsl(48, 96%, 40%)", fontSize: 11 }} />
                          <Tooltip 
                            contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))" }} 
                            formatter={formatOverallTooltip}
                          />
                          <Area type="monotone" dataKey={isContextMode ? "wbi" : "overall"} stroke="hsl(var(--primary))" fill="url(#colorOverall)" strokeWidth={3} dot={{ r: 4 }} name="Overall Score" yAxisId="left" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </>
                ) : (
                  <div className="py-8 text-center text-muted-foreground">Not enough data</div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="metrics">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">Individual Dimension Metrics</h3>
                    <p className="text-sm text-muted-foreground">Comparing Exhaustion, Cynicism, and Inefficacy over time</p>
                  </div>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" size="sm" className="gap-2">
                        <CalendarIcon className="h-4 w-4" />
                        {startDate && endDate ? `${format(startDate, "MMM d")} - ${format(endDate, "MMM d")}` : "Select Date Range"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="end">
                      <div className="flex flex-col sm:flex-row">
                        <div className="p-3 border-b sm:border-b-0 sm:border-r">
                          <p className="text-sm font-medium mb-2">Start Date</p>
                          <Calendar mode="single" selected={startDate} onSelect={setStartDate} initialFocus />
                        </div>
                        <div className="p-3">
                          <p className="text-sm font-medium mb-2">End Date</p>
                          <Calendar mode="single" selected={endDate} onSelect={setEndDate} />
                        </div>
                      </div>
                      <div className="p-2 border-t flex justify-center bg-muted/20">
                        <Button variant="ghost" size="sm" className="w-full text-muted-foreground" onClick={handleResetDates}>
                          Reset Dates
                        </Button>
                      </div>
                    </PopoverContent>
                  </Popover>
                </div>
                {dimensionHistory.length > 0 ? (
                  <>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={dimensionHistory} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                          <XAxis dataKey="date" tick={{ fontSize: 12 }} className="text-muted-foreground" />
                          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} className="text-muted-foreground" yAxisId="left" />
                          <YAxis domain={[0, 100]} yAxisId="right" orientation="right" tick={false} axisLine={false} />
                          <ReferenceLine y={75} yAxisId="left" stroke="hsl(0, 84%, 60%)" strokeDasharray="5 5" label={{ value: "Critical", position: "right", fill: "hsl(0, 84%, 60%)", fontSize: 11 }} />
                          <ReferenceLine y={50} yAxisId="left" stroke="hsl(25, 95%, 53%)" strokeDasharray="5 5" label={{ value: "High", position: "right", fill: "hsl(25, 95%, 53%)", fontSize: 11 }} />
                          <ReferenceLine y={25} yAxisId="left" stroke="hsl(48, 96%, 53%)" strokeDasharray="5 5" label={{ value: "Moderate", position: "right", fill: "hsl(48, 96%, 40%)", fontSize: 11 }} />
                          <Tooltip 
                            contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))" }} 
                            formatter={formatDimensionTooltip}
                          />
                          <Legend />
                          <Line type="monotone" dataKey={isContextMode ? "wbi_e" : "exhaustion"} stroke="hsl(280, 65%, 60%)" strokeWidth={2} dot={{ r: 4 }} yAxisId="left" name="Exhaustion" />
                          <Line type="monotone" dataKey={isContextMode ? "wbi_c" : "cynicism"} stroke="hsl(210, 80%, 50%)" strokeWidth={2} dot={{ r: 4 }} yAxisId="left" name="Cynicism" />
                          <Line type="monotone" dataKey={isContextMode ? "wbi_i" : "inefficacy"} stroke="hsl(180, 70%, 45%)" strokeWidth={2} dot={{ r: 4 }} yAxisId="left" name="Inefficacy" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="mt-4 flex items-center justify-center gap-6 text-sm flex-wrap">
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
                  </>
                ) : (
                  <div className="py-8 text-center text-muted-foreground">Not enough data</div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}