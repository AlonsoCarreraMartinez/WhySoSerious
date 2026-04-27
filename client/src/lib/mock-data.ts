export type BurnoutLevel = "critical" | "high" | "moderate" | "low"
export type Visibility = "public" | "private" | "org-wide" | "shared"

export interface ContextMetrics {
  avg_overtime: number
  avg_density: number
  avg_latency: number
}

export interface Team {
  id: string
  name: string
  visibility: Visibility
  memberCount: number
  burnoutScore: number
  burnoutLevel: BurnoutLevel
  exhaustion: number
  cynicism: number
  inefficacy: number
  wbi?: number
  wbi_e?: number
  wbi_c?: number
  wbi_i?: number
  context?: ContextMetrics
}

export interface Channel {
  id: string
  teamId: string
  name: string
  visibility: Visibility
  memberCount: number
  burnoutScore: number
  burnoutLevel: BurnoutLevel
  exhaustion: number
  cynicism: number
  inefficacy: number
  wbi?: number
  wbi_e?: number
  wbi_c?: number
  wbi_i?: number
  context?: ContextMetrics
}

export interface ManagedTeam {
  name: string
  visibility: Visibility
}

export interface CurrentUser {
  id: string
  name: string
  email: string
  role: "Global Administrator" | "HR Manager" | "Team Lead"
  managedTeams: ManagedTeam[]
}

export const mockCurrentUser: CurrentUser = {
  id: "u1",
  name: "Jane Doe",
  email: "jane.doe@company.com",
  role: "Global Administrator",
  managedTeams: [
    { name: "Oviedo", visibility: "org-wide" },
    { name: "León", visibility: "public" },
    { name: "La Bañeza", visibility: "private" },
  ],
}

export interface Member {
  id: string
  name: string
  email: string
  role: "manager" | "member"
  avatar?: string
}

export interface ChatSession {
  id: string
  channelId: string
  date: string
  density: number
  latency: number
  messageCount: number
}

export interface Notification {
  id: string
  title: string
  message: string
  timestamp: string
  read: boolean
}

export interface HistoricalDataPoint {
  date: string
  score: number
  wbi?: number
  exhaustion?: number
  cynicism?: number
  inefficacy?: number
}

export function getBurnoutLevel(score: number): BurnoutLevel {
  if (score >= 75) return "critical"
  if (score >= 50) return "high"
  if (score >= 25) return "moderate"
  return "low"
}

export function getBurnoutColor(level: BurnoutLevel): string {
  switch (level) {
    case "critical":
      return "bg-red-500 text-white"
    case "high":
      return "bg-orange-500 text-white"
    case "moderate":
      return "bg-yellow-500 text-yellow-950"
    case "low":
      return "bg-green-500 text-white"
  }
}

export function getBurnoutBorderColor(level: BurnoutLevel): string {
  switch (level) {
    case "critical":
      return "border-l-red-500"
    case "high":
      return "border-l-orange-500"
    case "moderate":
      return "border-l-yellow-500"
    case "low":
      return "border-l-green-500"
  }
}

export const mockTeams: Team[] = [
  { id: "1", name: "Engineering Core", visibility: "private", memberCount: 24, burnoutScore: 82, burnoutLevel: "critical", exhaustion: 85, cynicism: 78, inefficacy: 83 },
  { id: "2", name: "Product Design", visibility: "org-wide", memberCount: 12, burnoutScore: 68, burnoutLevel: "high", exhaustion: 72, cynicism: 65, inefficacy: 67 },
  { id: "3", name: "Customer Success", visibility: "public", memberCount: 18, burnoutScore: 55, burnoutLevel: "high", exhaustion: 58, cynicism: 52, inefficacy: 55 },
  { id: "4", name: "Marketing", visibility: "public", memberCount: 8, burnoutScore: 42, burnoutLevel: "moderate", exhaustion: 45, cynicism: 38, inefficacy: 43 },
  { id: "5", name: "Data Analytics", visibility: "private", memberCount: 6, burnoutScore: 35, burnoutLevel: "moderate", exhaustion: 38, cynicism: 32, inefficacy: 35 },
  { id: "6", name: "HR Operations", visibility: "org-wide", memberCount: 5, burnoutScore: 22, burnoutLevel: "low", exhaustion: 25, cynicism: 20, inefficacy: 21 },
  { id: "7", name: "Finance", visibility: "private", memberCount: 7, burnoutScore: 18, burnoutLevel: "low", exhaustion: 20, cynicism: 15, inefficacy: 19 },
  { id: "8", name: "Legal", visibility: "private", memberCount: 4, burnoutScore: 28, burnoutLevel: "moderate", exhaustion: 30, cynicism: 26, inefficacy: 28 },
  { id: "9", name: "Sales", visibility: "public", memberCount: 15, burnoutScore: 48, burnoutLevel: "moderate", exhaustion: 50, cynicism: 45, inefficacy: 49 },
  { id: "10", name: "Infrastructure", visibility: "private", memberCount: 9, burnoutScore: 62, burnoutLevel: "high", exhaustion: 65, cynicism: 60, inefficacy: 61 },
]

export const mockChannels: Channel[] = [
  { id: "c1", teamId: "1", name: "sprint-planning", visibility: "public", memberCount: 20, burnoutScore: 88, burnoutLevel: "critical", exhaustion: 90, cynicism: 85, inefficacy: 89 },
  { id: "c2", teamId: "1", name: "incident-response", visibility: "private", memberCount: 8, burnoutScore: 79, burnoutLevel: "critical", exhaustion: 82, cynicism: 76, inefficacy: 79 },
  { id: "c3", teamId: "2", name: "design-reviews", visibility: "shared", memberCount: 10, burnoutScore: 65, burnoutLevel: "high", exhaustion: 68, cynicism: 62, inefficacy: 65 },
  { id: "c4", teamId: "3", name: "escalations", visibility: "private", memberCount: 15, burnoutScore: 58, burnoutLevel: "high", exhaustion: 60, cynicism: 56, inefficacy: 58 },
  { id: "c5", teamId: "1", name: "code-reviews", visibility: "shared", memberCount: 18, burnoutScore: 52, burnoutLevel: "high", exhaustion: 55, cynicism: 50, inefficacy: 51 },
  { id: "c6", teamId: "4", name: "campaigns", visibility: "public", memberCount: 6, burnoutScore: 38, burnoutLevel: "moderate", exhaustion: 40, cynicism: 35, inefficacy: 39 },
  { id: "c7", teamId: "5", name: "reports", visibility: "private", memberCount: 4, burnoutScore: 28, burnoutLevel: "moderate", exhaustion: 30, cynicism: 25, inefficacy: 29 },
  { id: "c8", teamId: "6", name: "general", visibility: "public", memberCount: 5, burnoutScore: 15, burnoutLevel: "low", exhaustion: 18, cynicism: 12, inefficacy: 15 },
]

export interface TeamHistoricalData {
  date: string
  [teamId: string]: number | string
}

export const mockTeamHistoricalData: TeamHistoricalData[] = [
  { date: "Mar 1", "1": 78, "2": 62, "3": 50, "4": 38, "5": 32 },
  { date: "Mar 5", "1": 80, "2": 64, "3": 52, "4": 40, "5": 33 },
  { date: "Mar 9", "1": 79, "2": 66, "3": 53, "4": 41, "5": 34 },
  { date: "Mar 13", "1": 81, "2": 65, "3": 54, "4": 42, "5": 34 },
  { date: "Mar 17", "1": 80, "2": 67, "3": 53, "4": 41, "5": 35 },
  { date: "Mar 21", "1": 82, "2": 68, "3": 55, "4": 42, "5": 35 },
  { date: "Mar 25", "1": 82, "2": 68, "3": 55, "4": 42, "5": 35 },
]

export interface DimensionHistoricalData {
  date: string
  exhaustion: number
  cynicism: number
  inefficacy: number
  overall: number
}

export const generateDimensionHistory = (
  baseExhaustion: number,
  baseCynicism: number,
  baseInefficacy: number
): DimensionHistoricalData[] => {
  const dates = ["Mar 1", "Mar 5", "Mar 9", "Mar 13", "Mar 17", "Mar 21", "Mar 25"]
  return dates.map((date, i) => {
    const variance = Math.sin(i * 0.5) * 5
    const exhaustion = Math.round(Math.max(0, Math.min(100, baseExhaustion - 5 + variance + i)))
    const cynicism = Math.round(Math.max(0, Math.min(100, baseCynicism - 3 + variance * 0.8 + i * 0.5)))
    const inefficacy = Math.round(Math.max(0, Math.min(100, baseInefficacy - 4 + variance * 0.6 + i * 0.8)))
    const overall = Math.round((exhaustion + cynicism + inefficacy) / 3)
    return { date, exhaustion, cynicism, inefficacy, overall }
  })
}

export const mockMembers: Record<string, Member[]> = {
  "1": [
    { id: "m1", name: "Sarah Chen", email: "sarah.chen@company.com", role: "manager" },
    { id: "m2", name: "Mike Johnson", email: "mike.j@company.com", role: "manager" },
    { id: "m3", name: "Emily Davis", email: "emily.d@company.com", role: "member" },
    { id: "m4", name: "Alex Kim", email: "alex.kim@company.com", role: "member" },
    { id: "m5", name: "Jordan Lee", email: "jordan.l@company.com", role: "member" },
    { id: "m6", name: "Taylor Swift", email: "taylor.s@company.com", role: "member" },
  ],
  "2": [
    { id: "m7", name: "Chris Brown", email: "chris.b@company.com", role: "manager" },
    { id: "m8", name: "Lisa Wang", email: "lisa.w@company.com", role: "member" },
    { id: "m9", name: "David Park", email: "david.p@company.com", role: "member" },
  ],
}

export const mockChatSessions: Record<string, ChatSession[]> = {
  "c1": [
    { id: "s1", channelId: "c1", date: "2024-01-15 09:30", density: 0.85, latency: 2.3, messageCount: 145 },
    { id: "s2", channelId: "c1", date: "2024-01-14 14:15", density: 0.72, latency: 3.1, messageCount: 98 },
    { id: "s3", channelId: "c1", date: "2024-01-13 10:00", density: 0.91, latency: 1.8, messageCount: 167 },
    { id: "s4", channelId: "c1", date: "2024-01-12 16:45", density: 0.68, latency: 4.2, messageCount: 82 },
  ],
  "c2": [
    { id: "s5", channelId: "c2", date: "2024-01-15 02:30", density: 0.95, latency: 0.8, messageCount: 234 },
    { id: "s6", channelId: "c2", date: "2024-01-10 23:15", density: 0.88, latency: 1.2, messageCount: 189 },
  ],
}

export const mockNotifications: Notification[] = [
  { id: "n1", title: "Analysis Complete", message: "Cronjob analysis updated successfully", timestamp: "2 min ago", read: false },
  { id: "n2", title: "High Risk Alert", message: "Engineering Core team exceeds burnout threshold", timestamp: "1 hour ago", read: false },
  { id: "n3", title: "Weekly Report", message: "Your weekly burnout summary is ready", timestamp: "3 hours ago", read: true },
  { id: "n4", title: "New Team Added", message: "Data Analytics team has been added to monitoring", timestamp: "1 day ago", read: true },
]

export const mockHistoricalData: HistoricalDataPoint[] = [
  { date: "Jan 1", score: 42 },
  { date: "Jan 5", score: 45 },
  { date: "Jan 9", score: 48 },
  { date: "Jan 13", score: 52 },
  { date: "Jan 17", score: 49 },
  { date: "Jan 21", score: 55 },
  { date: "Jan 25", score: 58 },
  { date: "Jan 29", score: 54 },
  { date: "Feb 2", score: 60 },
  { date: "Feb 6", score: 63 },
  { date: "Feb 10", score: 58 },
  { date: "Feb 14", score: 62 },
  { date: "Feb 18", score: 65 },
  { date: "Feb 22", score: 61 },
  { date: "Feb 26", score: 68 },
  { date: "Mar 1", score: 72 },
]