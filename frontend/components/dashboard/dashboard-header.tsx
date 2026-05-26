"use client"

import { Badge } from "@/components/ui/badge"
import { MapPin, Star } from "lucide-react"

interface DashboardHeaderProps {
  name: string
  totalReviews: number
}

export function DashboardHeader({ name, totalReviews }: DashboardHeaderProps) {
  return (
    <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-border">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
          <MapPin className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">{name}</h1>
          <p className="text-sm text-muted-foreground">Panel de Análisis de Experiencia</p>
        </div>
      </div>
      <Badge variant="secondary" className="text-sm px-4 py-2 gap-2 w-fit">
        <Star className="h-4 w-4 text-warning" />
        <span className="font-semibold text-foreground">{totalReviews.toLocaleString("es-CL")}</span>
        <span className="text-muted-foreground">reseñas</span>
      </Badge>
    </header>
  )
}
