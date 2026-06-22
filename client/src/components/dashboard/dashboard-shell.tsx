"use client"

import { Header } from "./header"
import { Sidebar } from "./sidebar"
import { MainDashboard } from "./main-dashboard"
import { TeamDetail } from "./team-detail"
import { ChannelDetail } from "./channel-detail"
import { EmployeeEmptyState } from "./employee-empty-state"
import { AccessDeniedState } from "./access-denied-state"
import { useDashboard } from "@/lib/dashboard-context"
import { Loader2 } from "lucide-react"

export function DashboardShell() {
  const { currentView, userRole, isCheckingAuth, inOrg, authMessage } = useDashboard()

  if (isCheckingAuth) {
    return (
      <div className="flex h-screen w-full flex-col items-center justify-center bg-background">
        <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
        <h2 className="text-xl font-semibold">Connecting to Microsoft Teams...</h2>
        <p className="text-muted-foreground">Verifying your identity and permissions</p>
      </div>
    )
  }

  if (!inOrg) {
    return <AccessDeniedState message={authMessage} />
  }

  if (userRole === "employee") {
    return (
      <div className="flex h-screen w-full bg-background">
        <EmployeeEmptyState />
      </div>
    )
  }

  const renderMainContent = () => {
    switch (currentView) {
      case "team":
        return <TeamDetail />
      case "channel":
        return <ChannelDetail />
      default:
        return <MainDashboard />
    }
  }

  return (
    <div className="flex h-screen flex-col">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto bg-background">
          {renderMainContent()}
        </main>
      </div>
    </div>
  )
}