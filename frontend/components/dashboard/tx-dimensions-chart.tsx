"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer } from "recharts"
import { Target } from "lucide-react"

interface TXDimension {
  dimension: string
  score: number
}

interface TXDimensionsChartProps {
  dimensions: TXDimension[]
}

export function TXDimensionsChart({ dimensions }: TXDimensionsChartProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <Target className="h-4 w-4 text-primary" />
          </div>
          <div>
            <CardTitle className="text-base">Dimensiones de Experiencia Turística</CardTitle>
            <CardDescription>Análisis multidimensional de la experiencia del visitante</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={dimensions} margin={{ top: 20, right: 40, bottom: 20, left: 40 }} cx="50%" cy="50%" outerRadius="90%">
              <PolarGrid 
                stroke="#cbd5e1"
                strokeWidth={0.75}
                gridType="circle"
                radialLines={true}
              />
              <PolarAngleAxis 
                dataKey="dimension" 
                tick={{ 
                  fill: "hsl(var(--muted-foreground))", 
                  fontSize: 12,
                  fontWeight: 500
                }}
              />
              <Radar
                name="Puntuación"
                dataKey="score"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.3}
                strokeWidth={2.5}
                dot={{
                  r: 5,
                  fill: "hsl(var(--background))",
                  stroke: "hsl(var(--primary))",
                  strokeWidth: 2.5
                }}
                activeDot={{
                  r: 7,
                  fill: "hsl(var(--primary))",
                  stroke: "hsl(var(--background))",
                  strokeWidth: 2
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-wrap justify-center gap-4 mt-4 pt-4 border-t border-border">
          {dimensions.map((dim) => (
            <div key={dim.dimension} className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">{dim.dimension}:</span>
              <span className="font-semibold text-foreground">{dim.score}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
