"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { MapPin } from "lucide-react"

interface AttractionItem {
  attraction: string
  commentCount: number
}

interface TopAttractionsListProps {
  attractions: AttractionItem[]
}

export function TopAttractionsList({ attractions }: TopAttractionsListProps) {
  if (!attractions || attractions.length === 0) return null

  const top5 = attractions.slice(0, 5)

  return (
    <Card className="shadow-sm border-border h-full flex flex-col">
      <CardHeader className="pb-4 border-b border-transparent">
        <CardTitle className="text-lg flex items-center gap-2">
          <div className="p-1.5 bg-primary/10 rounded-md">
            <MapPin className="w-4 h-4 text-primary" />
          </div>
          Top Atracciones
        </CardTitle>
        <CardDescription>
          Destinos con mayor volumen de reseñas en este rubro
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 pt-2">
        <ul className="flex flex-col h-full justify-start">
          {top5.map((item, i) => (
            <li 
              key={i} 
              className="flex justify-between items-center py-3.5 border-b last:border-0 hover:bg-slate-50/50 transition-colors group px-1"
            >
              <div className="flex items-center gap-3 overflow-hidden pr-2">
                <span className="font-bold text-muted-foreground/60 w-5 text-right text-sm">
                  {i + 1}.
                </span>
                <span className="font-medium text-slate-700 group-hover:text-primary transition-colors truncate text-sm">
                  {item.attraction}
                </span>
              </div>
              <span className="bg-slate-100 text-slate-600 border border-slate-200 text-xs px-2.5 py-1 rounded-full font-semibold ml-2 shrink-0 tabular-nums">
                {item.commentCount.toLocaleString('es-CL')}
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}