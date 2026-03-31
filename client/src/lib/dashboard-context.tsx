"use client"

import { createContext, useContext, useState, type ReactNode } from "react"

export type UserRole = "admin" | "manager" | "employee"
export type ViewType = "dashboard" | "team" | "channel"

interface DashboardState {
  currentView: ViewType
  selectedTeamId: string | null
  selectedChannelId: string | null
  userRole: UserRole
  dateRange: "30days" | "custom"
  customDateStart: string | null
  customDateEnd: string | null
}

interface DashboardContextType extends DashboardState {
  navigateToDashboard: () => void
  navigateToTeam: (teamId: string) => void
  navigateToChannel: (channelId: string) => void
  setUserRole: (role: UserRole) => void
  setDateRange: (range: "30days" | "custom") => void
  setCustomDates: (start: string, end: string) => void
}

const DashboardContext = createContext<DashboardContextType | null>(null)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DashboardState>({
    currentView: "dashboard",
    selectedTeamId: null,
    selectedChannelId: null,
    userRole: "admin",
    dateRange: "30days",
    customDateStart: null,
    customDateEnd: null,
  })

  const navigateToDashboard = () => {
    setState((prev) => ({
      ...prev,
      currentView: "dashboard",
      selectedTeamId: null,
      selectedChannelId: null,
    }))
  }

  const navigateToTeam = (teamId: string) => {
    setState((prev) => ({
      ...prev,
      currentView: "team",
      selectedTeamId: teamId,
      selectedChannelId: null,
    }))
  }

  const navigateToChannel = (channelId: string) => {
    setState((prev) => ({
      ...prev,
      currentView: "channel",
      selectedChannelId: channelId,
    }))
  }

  const setUserRole = (role: UserRole) => {
    setState((prev) => ({ ...prev, userRole: role }))
  }

  const setDateRange = (range: "30days" | "custom") => {
    setState((prev) => ({ ...prev, dateRange: range }))
  }

  const setCustomDates = (start: string, end: string) => {
    setState((prev) => ({
      ...prev,
      customDateStart: start,
      customDateEnd: end,
    }))
  }

  return (
    <DashboardContext.Provider
      value={{
        ...state,
        navigateToDashboard,
        navigateToTeam,
        navigateToChannel,
        setUserRole,
        setDateRange,
        setCustomDates,
      }}
    >
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard() {
  const context = useContext(DashboardContext)
  if (!context) {
    throw new Error("useDashboard must be used within a DashboardProvider")
  }
  return context
}
