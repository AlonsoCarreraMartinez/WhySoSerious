"use client"

import { Bell, ChevronDown, LogOut, Globe, Eye, EyeOff, HelpCircle } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
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
import { mockNotifications, mockCurrentUser, type Visibility } from "@/lib/mock-data"

function getVisibilityIcon(visibility: Visibility) {
  switch (visibility) {
    case "org-wide":
      return Globe
    case "public":
      return Eye
    case "private":
      return EyeOff
  }
}

export function Header() {
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const unreadCount = mockNotifications.filter((n) => !n.read).length

  const initials = mockCurrentUser.name
    .split(" ")
    .map((n) => n[0])
    .join("")

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6" role="banner">
      <div className="flex items-center gap-4">
        <img
          src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/logo.png-RN81r7PSY9V5OJuXvX8MX3uMmtGZKb.jpeg"
          alt="whysoserious logo"
          className="h-10 w-auto"
        />
        <div className="flex flex-col">
          <span className="text-lg font-semibold text-foreground">whysoserious</span>
          <span className="text-xs text-muted-foreground">HR Burnout Detection</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="relative"
          onClick={() => setNotificationsOpen(true)}
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
              <span className="hidden md:inline-block">{mockCurrentUser.name}</span>
              <ChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-64">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium">{mockCurrentUser.name}</p>
                <p className="text-xs text-muted-foreground">{mockCurrentUser.email}</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <div className="px-2 py-2">
              <p className="text-xs font-medium text-muted-foreground mb-1">Role</p>
              <Badge variant="secondary" className="font-medium">
                {mockCurrentUser.role}
              </Badge>
            </div>
            <DropdownMenuSeparator />
            <div className="px-2 py-2">
              <p className="text-xs font-medium text-muted-foreground mb-2">Managed Teams</p>
              <div className="flex flex-wrap gap-1">
                {mockCurrentUser.managedTeams.map((team) => {
                  const Icon = getVisibilityIcon(team.visibility)
                  return (
                    <Badge key={team.name} variant="outline" className="text-xs flex items-center gap-1">
                      <Icon className="h-3 w-3" />
                      {team.name}
                    </Badge>
                  )
                })}
              </div>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive cursor-pointer">
              <LogOut className="mr-2 h-4 w-4" />
              Log Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <Dialog open={notificationsOpen} onOpenChange={setNotificationsOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Notifications</DialogTitle>
            <DialogDescription>
              Recent alerts and updates from burnout monitoring
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="max-h-80">
            <div className="flex flex-col gap-3 pr-4">
              {mockNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`rounded-lg border p-3 ${
                    notification.read ? "bg-background" : "bg-primary/5 border-primary/20"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-medium text-sm">{notification.title}</p>
                      <p className="text-sm text-muted-foreground">{notification.message}</p>
                    </div>
                    {!notification.read && (
                      <div className="h-2 w-2 rounded-full bg-primary shrink-0 mt-1.5" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">{notification.timestamp}</p>
                </div>
              ))}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </header>
  )
}
