"use client"

import { LayoutDashboard, Users, Hash } from "lucide-react"
import { cn } from "@/lib/utils"
import { useDashboard } from "@/lib/dashboard-context"

const navItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "teams", label: "Teams", icon: Users },
  { id: "channels", label: "Channels", icon: Hash },
] as const

export function Sidebar() {
  const { currentView, navigateToDashboard } = useDashboard()

  const handleNavClick = (itemId: string) => {
    if (itemId === "dashboard" || itemId === "teams" || itemId === "channels") {
      navigateToDashboard()
    }
  }

  return (
    <aside
      className="flex w-64 flex-col bg-sidebar text-sidebar-foreground"
      role="navigation"
      aria-label="Main navigation"
    >
      <nav className="flex-1 p-4">
        <ul className="flex flex-col gap-1">
          {navItems.map((item) => {
            const isActive =
              item.id === "dashboard"
                ? currentView === "dashboard"
                : item.id === "teams"
                  ? currentView === "team"
                  : currentView === "channel"

            return (
              <li key={item.id}>
                <button
                  onClick={() => handleNavClick(item.id)}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                  )}
                  aria-current={isActive ? "page" : undefined}
                >
                  <item.icon className="h-5 w-5" aria-hidden="true" />
                  {item.label}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="border-t border-sidebar-border p-4">
        <p className="text-xs text-sidebar-foreground/50">
          Powered by Microsoft Teams Data
        </p>
      </div>
    </aside>
  )
}
