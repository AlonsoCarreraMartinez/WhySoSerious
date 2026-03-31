
import { DashboardProvider } from "@/lib/dashboard-context"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"

export default function Home() {
  return (
    <DashboardProvider>
      <DashboardShell />
    </DashboardProvider>
  )
}
