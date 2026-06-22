"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { app } from "@microsoft/teams-js"

type ViewState = "dashboard" | "team" | "channel"
type UserRole = "admin" | "manager" | "employee" | "none"

interface User {
  name: string
  email: string
  role: string
  managedTeams: any[]
  avatar?: string
}

interface DashboardContextType {
  currentView: ViewState
  userRole: UserRole
  currentUser: User | null
  isCheckingAuth: boolean
  inOrg: boolean
  authMessage: string
  selectedTeamId: string | null
  selectedChannelId: string | null
  isContextMode: boolean
  navigateToDashboard: () => void
  navigateToTeam: (teamId: string) => void
  navigateToChannel: (channelId: string) => void
  toggleContextMode: () => void
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [currentView, setCurrentView] = useState<ViewState>("dashboard")
  const [selectedTeamId, setSelectedTeamId] = useState<string | null>(null)
  const [selectedChannelId, setSelectedChannelId] = useState<string | null>(null)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)
  const [userRole, setUserRole] = useState<UserRole>("none")
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [inOrg, setInOrg] = useState(false)
  const [authMessage, setAuthMessage] = useState("")
  const [isContextMode, setIsContextMode] = useState(false)

  useEffect(() => {
    const initTeamsAndAuth = async () => {
      let userEmail = ""
      let userName = ""

      try {
        await app.initialize()
        const context = await app.getContext()
        userEmail = context.user?.userPrincipalName || context.user?.loginHint || ""
        userName = context.user?.userDisplayName || userEmail.split("@")[0]

        if (!userEmail) throw new Error("Could not get user email from Teams")

      } catch (error) {
        setInOrg(false)
        setAuthMessage("Security block: You must open this dashboard inside Microsoft Teams.")
        setIsCheckingAuth(false)
        return
      }

      try {
        const API_BASE = `${(import.meta as any).env.VITE_API_URL}/api`

        const response = await fetch(`${API_BASE}/auth/verify`, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true"
          },
          body: JSON.stringify({ email: userEmail })
        })

        if (!response.ok) throw new Error("Backend verification failed")

        const authData = await response.json()

        if (authData.token) {
          sessionStorage.setItem("jwt_token", authData.token)
        }

        setInOrg(authData.in_org)
        setAuthMessage(authData.auth_message)

        if (authData.in_org) {
          let computedRole: UserRole = "employee" 
          
          if (authData.is_admin && authData.db_role?.toLowerCase() === "admin") {
            computedRole = "admin" 
          } else if (authData.managed_teams && authData.managed_teams.length > 0) {
            computedRole = "manager" 
          }

          setUserRole(computedRole)
          setCurrentUser({
            name: userName,
            email: userEmail,
            role: authData.db_role || "Employee", 
            managedTeams: authData.managed_teams || [], 
            avatar: "" 
          })
        }
      } catch (error) {
        setInOrg(false)
        setAuthMessage("Could not connect to the authentication server.")
      } finally {
        setIsCheckingAuth(false)
      }
    }

    initTeamsAndAuth()
  }, [])

  const navigateToDashboard = () => setCurrentView("dashboard")
  const navigateToTeam = (teamId: string) => {
    setSelectedTeamId(teamId)
    setCurrentView("team")
  }
  const navigateToChannel = (channelId: string) => {
    setSelectedChannelId(channelId)
    setCurrentView("channel")
  }
  const toggleContextMode = () => setIsContextMode((prev) => !prev)

  return (
    <DashboardContext.Provider
      value={{
        currentView, userRole, currentUser, isCheckingAuth, inOrg, authMessage,
        selectedTeamId, selectedChannelId, isContextMode, navigateToDashboard, 
        navigateToTeam, navigateToChannel, toggleContextMode,
      }}
    >
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard() {
  const context = useContext(DashboardContext)
  if (context === undefined) {
    throw new Error("useDashboard must be used within a DashboardProvider")
  }
  return context
}