"use client"

import { Eye, EyeOff, Users, Globe, Link2 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { getBurnoutColor, getBurnoutBorderColor, type BurnoutLevel, type Visibility } from "@/lib/mock-data"

interface BurnoutCardProps {
  name: string
  visibility: Visibility
  memberCount: number
  burnoutScore: number
  burnoutLevel: BurnoutLevel
  onClick?: () => void
  rank?: number
}

function VisibilityIcon({ visibility }: { visibility: Visibility }) {
  switch (visibility) {
    case "org-wide":
      return <Globe className="h-4 w-4" aria-hidden="true" />
    case "shared":
      return <Link2 className="h-4 w-4" aria-hidden="true" />
    case "public":
      return <Eye className="h-4 w-4" aria-hidden="true" />
    case "private":
      return <EyeOff className="h-4 w-4" aria-hidden="true" />
  }
}

export function BurnoutCard({
  name,
  visibility,
  memberCount,
  burnoutScore,
  burnoutLevel,
  onClick,
  rank,
}: BurnoutCardProps) {
  return (
    <Card
      className={cn(
        "cursor-pointer border-l-4 transition-all hover:shadow-md",
        getBurnoutBorderColor(burnoutLevel)
      )}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onClick?.()
        }
      }}
      aria-label={`${name}, burnout score ${burnoutScore}, ${memberCount} members, ${visibility}`}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              {rank && (
                <span className="text-lg font-bold text-muted-foreground">#{rank}</span>
              )}
              <h3 className="font-semibold text-foreground truncate">{name}</h3>
            </div>
            <div className="mt-2 flex items-center gap-3 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <VisibilityIcon visibility={visibility} />
                <span className="sr-only">{visibility}</span>
              </span>
              <span className="flex items-center gap-1">
                <Users className="h-4 w-4" aria-hidden="true" />
                {memberCount}
              </span>
            </div>
          </div>
          <Badge className={cn("shrink-0", getBurnoutColor(burnoutLevel))}>
            {burnoutScore}%
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}
