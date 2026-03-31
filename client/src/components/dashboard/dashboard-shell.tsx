"use client"

import { Header } from "./header"
import { Sidebar } from "./sidebar"
import { MainDashboard } from "./main-dashboard"
import { TeamDetail } from "./team-detail"
import { ChannelDetail } from "./channel-detail"
import { EmployeeEmptyState } from "./employee-empty-state"
import { RoleSelector } from "./role-selector"
import { useDashboard } from "@/lib/dashboard-context"

export function DashboardShell() {
  const { currentView, userRole } = useDashboard()

  const renderMainContent = () => {
    if (userRole === "employee") {
      return <EmployeeEmptyState />
    }

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
      <RoleSelector />
    </div>
  )
}
