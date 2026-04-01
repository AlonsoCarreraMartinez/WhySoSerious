"use client"

import { useState, useMemo, useEffect } from "react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs"
import { Input } from "../ui/input"
import { BurnoutCard } from "./burnout-card"
import { useDashboard } from "../../lib/dashboard-context"
import { Search } from "lucide-react"

import { api } from "../../lib/api"
import { Team, Channel } from "../../lib/mock-data"

const CHART_COLORS = [
  "hsl(280, 65%, 60%)",  
  "hsl(210, 80%, 50%)",   
  "hsl(180, 70%, 45%)",   
  "hsl(330, 75%, 65%)",   
  "hsl(240, 60%, 55%)",   
]

export function MainDashboard() {
  const { navigateToTeam, navigateToChannel, currentUser, userRole } = useDashboard()
  const [teamSearch, setTeamSearch] = useState("")

  const [teams, setTeams] = useState<Team[]>([])
  const [channels, setChannels] = useState<Channel[]>([])
  const [chartData, setChartData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        let [fetchedTeams, fetchedChannels] = await Promise.all([
          api.getDashboardTeams(),
          api.getDashboardChannels()
        ])

        if (userRole === "manager" && currentUser) {
          const managedTeamNames = currentUser.managedTeams.map((t: any) => t.name)
          
          fetchedTeams = fetchedTeams.filter((team) => managedTeamNames.includes(team.name))
          
          const validTeamIds = fetchedTeams.map((t: any) => String(t.id || t._id))
          
          fetchedChannels = fetchedChannels.filter((channel: any) => {
            const cTeamId = String(channel.teamId || channel.team_id || "")
            return validTeamIds.includes(cTeamId) || managedTeamNames.includes(cTeamId)
          })
        }

        setTeams(fetchedTeams)
        setChannels(fetchedChannels)

        const top5Teams = fetchedTeams.slice(0, 5)

        if (top5Teams.length > 0) {
          const historyPromises = top5Teams.map(t => api.getHistoricalData(t.id))
          const histories = await Promise.all(historyPromises)

          const mergedByDate: Record<string, any> = {}

          histories.forEach((teamHistory, index) => {
            const teamId = top5Teams[index].id
            teamHistory.forEach((point: any) => {
              if (!mergedByDate[point.date]) {
                mergedByDate[point.date] = { date: point.date }
              }
              mergedByDate[point.date][teamId] = point.score
            })
          })

          const finalChartData = Object.values(mergedByDate)
          setChartData(finalChartData)
        } else {
          setChartData([])
        }

      } catch (error) {
        console.error("Error fetching dashboard data:", error)
      } finally {
        setIsLoading(false)
      }
    }

    if (currentUser) {
      setIsLoading(true)
      fetchDashboardData()
      
      const intervalId = setInterval(fetchDashboardData, 300000)
      return () => clearInterval(intervalId)
    }
  }, [currentUser, userRole])

  const topTeams = useMemo(() => 
    [...teams].sort((a, b) => b.burnoutScore - a.burnoutScore).slice(0, 5),
    [teams]
  )

  const topChannels = useMemo(() =>
    [...channels].sort((a, b) => b.burnoutScore - a.burnoutScore).slice(0, 5),
    [channels]
  )

  const allTeamsSorted = useMemo(() =>
    [...teams].sort((a, b) => a.name.localeCompare(b.name)),
    [teams]
  )

  const filteredTeams = useMemo(() =>
    allTeamsSorted.filter((team) =>
      team.name.toLowerCase().includes(teamSearch.toLowerCase())
    ),
    [allTeamsSorted, teamSearch]
  )

  if (isLoading || !currentUser) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-muted-foreground">
        Loading data from database...
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6 p-6" role="main">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome, <span className="font-medium text-foreground">{currentUser.name}</span>
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-destructive" />
              Top 5 Teams at Risk
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {topTeams.length > 0 ? (
              topTeams.map((team, index) => (
                <BurnoutCard
                  key={team.id}
                  name={team.name}
                  visibility={team.visibility}
                  memberCount={team.memberCount}
                  burnoutScore={team.burnoutScore}
                  burnoutLevel={team.burnoutLevel}
                  rank={index + 1}
                  onClick={() => navigateToTeam(team.id)}
                />
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No teams to display.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-destructive" />
              Top 5 Channels at Risk
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {topChannels.length > 0 ? (
              topChannels.map((channel, index) => (
                <BurnoutCard
                  key={channel.id}
                  name={channel.name}
                  visibility={channel.visibility}
                  memberCount={channel.memberCount}
                  burnoutScore={channel.burnoutScore}
                  burnoutLevel={channel.burnoutLevel}
                  rank={index + 1}
                  onClick={() => navigateToChannel(channel.id)}
                />
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No channels to display.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="trends" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="trends">Trends</TabsTrigger>
              <TabsTrigger value="all-teams">Teams</TabsTrigger>
            </TabsList>

            <TabsContent value="trends">
              <div>
                <h3 className="text-lg font-semibold mb-2">Top 5 Teams - Burnout Index Evolution (Last 30 Days)</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Comparing burnout trends for the highest-risk teams
                </p>
                {chartData.length > 0 ? (
                  <>
                    <div className="h-[350px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
                            yAxisId="left"
                          />
                          <YAxis
                            domain={[0, 100]}
                            yAxisId="right"
                            orientation="right"
                            tick={false}
                            axisLine={false}
                          />
                          <ReferenceLine
                            y={75}
                            yAxisId="left"
                            stroke="hsl(0, 84%, 60%)"
                            strokeDasharray="5 5"
                            label={{ value: "Critical", position: "right", fill: "hsl(0, 84%, 60%)", fontSize: 11 }}
                          />
                          <ReferenceLine
                            y={50}
                            yAxisId="left"
                            stroke="hsl(25, 95%, 53%)"
                            strokeDasharray="5 5"
                            label={{ value: "High", position: "right", fill: "hsl(25, 95%, 53%)", fontSize: 11 }}
                          />
                          <ReferenceLine
                            y={25}
                            yAxisId="left"
                            stroke="hsl(48, 96%, 53%)"
                            strokeDasharray="5 5"
                            label={{ value: "Moderate", position: "right", fill: "hsl(48, 96%, 40%)", fontSize: 11 }}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "hsl(var(--card))",
                              border: "1px solid hsl(var(--border))",
                              borderRadius: "var(--radius)",
                            }}
                            labelStyle={{ color: "hsl(var(--foreground))" }}
                          />
                          <Legend />
                          {topTeams.map((team, index) => (
                            <Line
                              key={team.id}
                              type="monotone"
                              dataKey={team.id}
                              stroke={CHART_COLORS[index % CHART_COLORS.length]}
                              strokeWidth={2}
                              dot={{ fill: CHART_COLORS[index % CHART_COLORS.length], r: 3 }}
                              name={team.name}
                              yAxisId="left"
                            />
                          ))}
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
                  </>
                ) : (
                  <div className="py-8 text-center text-muted-foreground">Not enough data to display trends.</div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="all-teams">
              <div>
                <div className="flex items-center gap-4 mb-4">
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search teams..."
                      value={teamSearch}
                      onChange={(e) => setTeamSearch(e.target.value)}
                      className="pl-10"
                      aria-label="Search teams"
                    />
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {filteredTeams.length} of {allTeamsSorted.length} teams
                  </span>
                </div>
                <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                  {filteredTeams.map((team) => (
                    <BurnoutCard
                      key={team.id}
                      name={team.name}
                      visibility={team.visibility}
                      memberCount={team.memberCount}
                      burnoutScore={team.burnoutScore}
                      burnoutLevel={team.burnoutLevel}
                      onClick={() => navigateToTeam(team.id)}
                    />
                  ))}
                </div>
                {filteredTeams.length === 0 && (
                  <div className="py-8 text-center text-muted-foreground">
                    No teams found matching your search
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}