"use client"

import { Bell, ChevronDown, Globe, Eye, EyeOff, Info } from "lucide-react"
import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { type Visibility } from "@/lib/mock-data"
import { useDashboard } from "@/lib/dashboard-context"
import { api, type AppNotification } from "@/lib/api"

function getVisibilityIcon(visibility: Visibility | string) {
  switch (visibility) {
    case "org-wide":
      return Globe
    case "public":
      return Eye
    case "private":
      return EyeOff
    default:
      return EyeOff
  }
}

export function Header() {
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [notifications, setNotifications] = useState<AppNotification[]>([])
  
  const { currentUser } = useDashboard()

  useEffect(() => {
    if (currentUser?.email) {
      const fetchNotifs = () => {
        api.getNotifications(currentUser.email)
          .then(setNotifications)
          .catch(console.error)
      }

      fetchNotifs()
      const intervalId = setInterval(fetchNotifs, 300000)

      return () => clearInterval(intervalId)
    }
  }, [currentUser])

  if (!currentUser) return null

  const unreadCount = notifications.filter((n) => !n.isRead).length

  const handleOpenChange = (open: boolean) => {
    setNotificationsOpen(open)
    if (open && unreadCount > 0) {
      const unread = notifications.filter(n => !n.isRead)
      setNotifications(prev => prev.map(n => ({ ...n, isRead: true })))
      
      unread.forEach(n => {
        api.markNotificationAsRead(n.id, currentUser.email).catch(console.error)
      })
    }
  }

  const initials = currentUser.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6" role="banner">
      <div className="flex items-center gap-4">
        <img
          src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/logo.png-RN81r7PSY9V5OJuXvX8MX3uMmtGZKb.jpeg"
          alt="whysoserious logo"
          className="h-10 w-auto"
        />
        <div className="flex flex-col">
          <span className="text-lg font-semibold text-foreground">WhySoSerious</span>
          <span className="text-xs text-muted-foreground">HR Burnout Detection</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary">
              <Info className="h-5 w-5" />
              <span className="sr-only">MBI Information</span>
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80 p-4" align="end">
            <div className="space-y-3">
              <h4 className="font-semibold text-sm">Maslach Burnout Inventory (MBI)</h4>
              <p className="text-xs text-muted-foreground">
                Our AI maps communication patterns to MBI dimensions (Exhaustion, Cynicism, Inefficacy).
              </p>
              <div className="grid gap-2 text-xs">
                <div className="flex items-start gap-2">
                  <div className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-red-500" />
                  <div>
                    <span className="font-semibold text-foreground">Critical (75-100)</span>
                    <p className="text-muted-foreground">Severe burnout risk. Immediate intervention required.</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-orange-500" />
                  <div>
                    <span className="font-semibold text-foreground">High (50-74)</span>
                    <p className="text-muted-foreground">Significant risk. Preventive measures recommended.</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-yellow-500" />
                  <div>
                    <span className="font-semibold text-foreground">Moderate (25-49)</span>
                    <p className="text-muted-foreground">Early signs. Monitor team workload and engagement.</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-green-500" />
                  <div>
                    <span className="font-semibold text-foreground">Low (0-24)</span>
                    <p className="text-muted-foreground">Healthy levels. Normal stress, engaged and effective.</p>
                  </div>
                </div>
              </div>
            </div>
          </PopoverContent>
        </Popover>

        <Button
          variant="ghost"
          size="icon"
          className="relative"
          onClick={() => handleOpenChange(true)}
          aria-label={`Notifications, ${unreadCount} unread`}
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
            >
              {unreadCount}
            </Badge>
          )}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary text-primary-foreground">{initials}</AvatarFallback>
              </Avatar>
              <span className="hidden md:inline-block">{currentUser.name}</span>
              <ChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-64">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium">{currentUser.name}</p>
                <p className="text-xs text-muted-foreground">{currentUser.email}</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <div className="px-2 py-2">
              <p className="text-xs font-medium text-muted-foreground mb-1">Role</p>
              <Badge variant="secondary" className="font-medium">
                {currentUser.role}
              </Badge>
            </div>
            <DropdownMenuSeparator />
            <div className="px-2 py-2">
              <p className="text-xs font-medium text-muted-foreground mb-2">Managed Teams</p>
              <div className="flex flex-wrap gap-1">
                {currentUser.managedTeams.map((team: any) => {
                  const Icon = getVisibilityIcon(team.visibility)
                  return (
                    <Badge key={team.name} variant="outline" className="text-xs flex items-center gap-1">
                      <Icon className="h-3 w-3" />
                      {team.name}
                    </Badge>
                  )
                })}
                {currentUser.managedTeams.length === 0 && (
                  <span className="text-xs text-muted-foreground">No assigned teams</span>
                )}
              </div>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <Dialog open={notificationsOpen} onOpenChange={handleOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Notifications</DialogTitle>
            <DialogDescription>
              Recent alerts and updates from burnout monitoring
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="max-h-80">
            <div className="flex flex-col gap-3 pr-4">
              {notifications.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">No new notifications</p>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`rounded-lg border p-3 ${
                      notification.isRead ? "bg-background" : "bg-primary/5 border-primary/20"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-medium text-sm">{notification.title}</p>
                        <p className="text-sm text-muted-foreground">{notification.message}</p>
                      </div>
                      {!notification.isRead && (
                        <div className="h-2 w-2 rounded-full bg-primary shrink-0 mt-1.5" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      {new Date(notification.date).toLocaleString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </header>
  )
}