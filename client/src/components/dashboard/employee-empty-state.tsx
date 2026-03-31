"use client"

import { UserX } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export function EmployeeEmptyState() {
  return (
    <div className="flex flex-1 items-center justify-center p-6" role="main">
      <Card className="max-w-md w-full">
        <CardContent className="py-12 text-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <UserX className="h-8 w-8 text-muted-foreground" />
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">
            No Teams Assigned
          </h2>
          <p className="text-muted-foreground">
            You do not have any teams assigned for monitoring. Please contact your
            administrator if you believe this is an error.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
