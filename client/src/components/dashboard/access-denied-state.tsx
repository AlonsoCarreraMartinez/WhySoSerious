"use client"

import { ShieldAlert } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export function AccessDeniedState({ message }: { message?: string }) {
  return (
    <div className="flex h-screen w-full items-center justify-center p-6 bg-background" role="main">
      <Card className="max-w-md w-full">
        <CardContent className="py-12 text-center flex flex-col items-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
            <ShieldAlert className="h-8 w-8 text-destructive" />
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">
            Access Denied
          </h2>
          <p className="text-muted-foreground">
            {message || "You do not have permission to access this application."}
          </p>
        </CardContent>
      </Card>
    </div>
  )
}