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

const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = sessionStorage.getItem("jwt_token");
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {})
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return fetch(url, { ...options, headers });
};

export const api = {
  
  getDashboardTeams: async (): Promise<Team[]> => {
    const res = await fetchWithAuth(`${API_BASE}/teams/dashboard`)
    if (!res.ok) throw new Error("Failed to fetch dashboard teams")
    const data = await res.json()
    
    return data.map((team: any) => ({
      ...team,
      burnoutIndex: team.burnout_index ?? team.burnoutIndex ?? 0,
      sentimentScore: team.sentiment_score ?? team.sentimentScore ?? 0,
      messageCount: team.message_count ?? team.messageCount ?? 0,
      memberCount: team.member_count ?? team.memberCount ?? 0,
    }))
  },
  
  getTeamDetail: async (teamName: string): Promise<Team> => {
    const res = await fetchWithAuth(`${API_BASE}/teams/${encodeURIComponent(teamName)}`)
    if (!res.ok) throw new Error("Failed to fetch team details")
    const team = await res.json()
    
    return {
      ...team,
      burnoutIndex: team.burnout_index ?? team.burnoutIndex ?? 0,
      sentimentScore: team.sentiment_score ?? team.sentimentScore ?? 0,
      messageCount: team.message_count ?? team.messageCount ?? 0,
      memberCount: team.member_count ?? team.memberCount ?? 0,
    }
  },

  getDashboardChannels: async (): Promise<Channel[]> => {
    const res = await fetchWithAuth(`${API_BASE}/channels/dashboard`)
    if (!res.ok) throw new Error("Failed to fetch dashboard channels")
    const data = await res.json()
    
    return data.map((channel: any) => ({
      ...channel,
      burnoutIndex: channel.burnout_index ?? channel.burnoutIndex ?? 0,
      sentimentScore: channel.sentiment_score ?? channel.sentimentScore ?? 0,
      messageCount: channel.message_count ?? channel.messageCount ?? 0,
    }))
  },

  getChannelDetail: async (channelId: string): Promise<Channel> => {
    const res = await fetchWithAuth(`${API_BASE}/channels/${encodeURIComponent(channelId)}`)
    if (!res.ok) throw new Error("Failed to fetch channel details")
    const channel = await res.json()
    
    return {
      ...channel,
      burnoutIndex: channel.burnout_index ?? channel.burnoutIndex ?? 0,
      sentimentScore: channel.sentiment_score ?? channel.sentimentScore ?? 0,
      messageCount: channel.message_count ?? channel.messageCount ?? 0,
    }
  },

  getBurnoutHistorical: async (targetName: string, startDate?: string, endDate?: string): Promise<HistoricalDataPoint[]> => {
    let url = `${API_BASE}/burnout/historical/${encodeURIComponent(targetName)}`
    
    if (startDate && endDate) {
      url += `?start_date=${startDate}&end_date=${endDate}`
    }
    
    const res = await fetchWithAuth(url)
    if (!res.ok) throw new Error("Failed to fetch historical data")
    return res.json()
  },

  getTeamMembers: async (teamName: string): Promise<Member[]> => {
    const res = await fetchWithAuth(`${API_BASE}/users/team/${encodeURIComponent(teamName)}`)
    if (!res.ok) throw new Error("Failed to fetch team members")
    return res.json()
  },

  getChannelMembers: async (channelId: string): Promise<Member[]> => {
    const res = await fetchWithAuth(`${API_BASE}/users/channel/${encodeURIComponent(channelId)}`)
    if (!res.ok) throw new Error("Failed to fetch channel members")
    return res.json()
  },

  getNotifications: async (email: string): Promise<AppNotification[]> => {
    const res = await fetchWithAuth(`${API_BASE}/notifications/${encodeURIComponent(email)}`)
    if (!res.ok) throw new Error("Failed to fetch notifications")
    return res.json()
  },

  markNotificationAsRead: async (notificationId: string, email: string): Promise<void> => {
    const res = await fetchWithAuth(`${API_BASE}/notifications/${notificationId}/read?user_email=${encodeURIComponent(email)}`, {
      method: 'PUT'
    })
    if (!res.ok) throw new Error("Failed to mark notification as read")
  }
}