import { Team, Channel, Member, HistoricalDataPoint } from "./mock-data"

const API_BASE = `${(import.meta as any).env.VITE_API_URL}/api`

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  date: string;
  targetTeam: string | null;
  isRead: boolean;
}

export const api = {
  
  getDashboardTeams: async (): Promise<Team[]> => {
    const res = await fetch(`${API_BASE}/teams/dashboard`)
    if (!res.ok) throw new Error("Failed to fetch dashboard teams")
    return res.json()
  },
  
  getTeamDetail: async (teamName: string): Promise<Team> => {
    const res = await fetch(`${API_BASE}/teams/${encodeURIComponent(teamName)}`)
    if (!res.ok) throw new Error("Failed to fetch team details")
    return res.json()
  },

  getDashboardChannels: async (): Promise<Channel[]> => {
    const res = await fetch(`${API_BASE}/channels/dashboard`)
    if (!res.ok) throw new Error("Failed to fetch dashboard channels")
    return res.json()
  },

  getTeamChannels: async (teamName: string): Promise<Channel[]> => {
    const res = await fetch(`${API_BASE}/channels/team/${encodeURIComponent(teamName)}`)
    if (!res.ok) throw new Error("Failed to fetch team channels")
    return res.json()
  },

  getChannelDetail: async (channelId: string): Promise<Channel> => {
    const res = await fetch(`${API_BASE}/channels/${encodeURIComponent(channelId)}`)
    if (!res.ok) throw new Error("Failed to fetch channel details")
    return res.json()
  },

  getHistoricalData: async (targetName: string, startDate?: string | null, endDate?: string | null): Promise<HistoricalDataPoint[]> => {
    let url = `${API_BASE}/burnout/historical/${encodeURIComponent(targetName)}`
    
    if (startDate && endDate) {
      url += `?start_date=${startDate}&end_date=${endDate}`
    }
    
    const res = await fetch(url)
    if (!res.ok) throw new Error("Failed to fetch historical data")
    return res.json()
  },

  getTeamMembers: async (teamName: string): Promise<Member[]> => {
    const res = await fetch(`${API_BASE}/users/team/${encodeURIComponent(teamName)}`)
    if (!res.ok) throw new Error("Failed to fetch team members")
    return res.json()
  },

  getChannelMembers: async (channelId: string): Promise<Member[]> => {
    const res = await fetch(`${API_BASE}/users/channel/${encodeURIComponent(channelId)}`)
    if (!res.ok) throw new Error("Failed to fetch channel members")
    return res.json()
  },

  getNotifications: async (email: string): Promise<AppNotification[]> => {
    const res = await fetch(`${API_BASE}/notifications/${encodeURIComponent(email)}`)
    if (!res.ok) throw new Error("Failed to fetch notifications")
    return res.json()
  },

  markNotificationAsRead: async (notificationId: string, email: string): Promise<void> => {
    const res = await fetch(`${API_BASE}/notifications/${encodeURIComponent(notificationId)}/read`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
    if (!res.ok) throw new Error("Failed to mark notification as read")
  }
}