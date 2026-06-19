"use client"

import { Badge } from "@/components/ui/badge"
import { MapPin, Star, Map, Building2 } from "lucide-react"

interface DashboardHeaderProps {
  name: string
  subtitle?: string
  totalReviews: number
  totalAttractions?: number
  totalRubros?: number
}

export function DashboardHeader({ 
  name, 
  subtitle = "Panel de Análisis de Experiencia", 
  totalReviews,
  totalAttractions,
  totalRubros
}: DashboardHeaderProps) {
  return (
    <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-border">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
          <MapPin className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">{name}</h1>
          <p className="text-sm text-muted-foreground">{subtitle}</p>
        </div>
      </div>
      
      <div className="flex flex-wrap items-center gap-3">
        <Badge variant="secondary" className="text-sm px-4 py-2 gap-2 w-fit shadow-sm">
          <Star className="h-4 w-4 text-warning" fill="currentColor" />
          <span className="font-semibold text-foreground">{totalReviews.toLocaleString("es-CL")}</span>
          <span className="text-muted-foreground font-normal">reseñas analizadas</span>
        </Badge>

        {totalAttractions !== undefined && totalAttractions > 0 && (
          <Badge variant="outline" className="text-sm px-4 py-2 gap-2 w-fit bg-card shadow-sm animate-in fade-in slide-in-from-right-2">
            <Map className="h-4 w-4 text-primary" />
            <span className="font-semibold text-foreground">{totalAttractions.toLocaleString("es-CL")}</span>
            <span className="text-muted-foreground font-normal">atracciones</span>
          </Badge>
        )}

        {totalRubros !== undefined && totalRubros > 0 && (
          <Badge variant="outline" className="text-sm px-4 py-2 gap-2 w-fit bg-card shadow-sm animate-in fade-in slide-in-from-right-4">
            <Building2 className="h-4 w-4 text-primary" />
            <span className="font-semibold text-foreground">{totalRubros.toLocaleString("es-CL")}</span>
            <span className="text-muted-foreground font-normal">rubros</span>
          </Badge>
        )}
      </div>
    </header>
  )
}