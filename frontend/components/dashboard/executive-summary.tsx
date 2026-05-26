"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles } from "lucide-react"

interface ExecutiveSummaryProps {
  summary: string
}

export function ExecutiveSummary({ summary }: ExecutiveSummaryProps) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <Sparkles className="h-4 w-4 text-primary" />
          </div>
          <CardTitle className="text-base">Resumen Ejecutivo</CardTitle>
          <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full">
            Generado por IA
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-relaxed text-muted-foreground">{summary}</p>
      </CardContent>
    </Card>
  )
}
