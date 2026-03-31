"use client"

import { useDashboard, type UserRole } from "@/lib/dashboard-context"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export function RoleSelector() {
  const { userRole, setUserRole } = useDashboard()

  return (
    <div className="fixed bottom-4 right-4 z-50 rounded-lg border bg-card p-4 shadow-lg">
      <div className="flex items-center gap-3">
        <Label htmlFor="role-select" className="text-sm font-medium whitespace-nowrap">
          Simulate Role:
        </Label>
        <Select value={userRole} onValueChange={(value) => setUserRole(value as UserRole)}>
          <SelectTrigger id="role-select" className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="manager">Manager</SelectItem>
            <SelectItem value="employee">Employee</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  )
}
