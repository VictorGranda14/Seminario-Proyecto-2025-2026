"use client"

import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer, Tooltip, Legend } from "recharts"
import { Target } from "lucide-react"

export interface TXDimension {
  dimension: string
  total?: number
  positive?: number
  negative?: number
  score?: number 
}

interface TXDimensionsChartProps {
  dimensions: TXDimension[]
  baseName?: string
  compareDimensions?: any
  compareName?: string
  attractionsList?: any[]
  selectedCompareId?: string
  onCompareChange?: (id: string) => void
  isLoadingCompare?: boolean
}

export function TXDimensionsChart({ 
  dimensions, 
  baseName = "Atracción Actual",
}: TXDimensionsChartProps) {


  const chartData = useMemo(() => {
    return dimensions.map(item => ({
      dimension: item.dimension,
      positive: (item.positive === undefined ? item.score : item.positive) === 0 ? 0.1 : (item.positive !== undefined ? item.positive : item.score),
      negative: item.negative === 0 ? 0.1 : (item.negative || 0.1),
      originalPos: item.positive || 0,
      originalNeg: item.negative || 0,
      originalTotal: item.total || 0
    }))
  }, [dimensions])

  // Formateador para el Tooltip (devuelve 0 real en vez de 0.1)
  const formatTooltip = (val: number) => val === 0.1 ? 0 : val

  if (!dimensions || dimensions.length === 0) {
    return (
      <Card>
        <CardContent className="flex h-64 items-center justify-center text-muted-foreground">
          No hay datos de dimensiones disponibles.
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-2">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <Target className="h-4 w-4 text-primary" />
          </div>
          <div>
            <CardTitle className="text-base">Dimensiones de la Experiencia</CardTitle>
            <CardDescription>
              Polaridad de las motivaciones turísticas en {baseName}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={chartData} margin={{ top: 20, right: 40, bottom: 20, left: 40 }} cx="50%" cy="50%" outerRadius="85%">
              <PolarGrid stroke="#cbd5e1" strokeWidth={0.75} gridType="circle" radialLines={true} />
              <PolarAngleAxis dataKey="dimension" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12, fontWeight: 500 }} />
              
              <Tooltip 
                formatter={(value: number) => [formatTooltip(value), "Menciones"]}
                contentStyle={{ borderRadius: '8px', fontSize: '13px' }}
              />
              <Legend wrapperStyle={{ fontSize: '13px', paddingTop: '10px' }} />

              {/* Polígono de Experiencias Positivas */}
              <Radar
                name="Impacto Positivo"
                dataKey="positive"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.35}
                strokeWidth={2.5}
                isAnimationActive={true}
                dot={{
                  r: 4,
                  fill: "hsl(var(--background))",
                  stroke: "#10b981",
                  strokeWidth: 2
                }}
                activeDot={{
                  r: 6,
                  fill: "#10b981",
                  stroke: "hsl(var(--background))",
                  strokeWidth: 2
                }}
              />

              {/* Polígono de Fricciones/Quejas */}
              <Radar
                name="Fricciones (Negativo)"
                dataKey="negative"
                stroke="#ef4444"
                fill="#ef4444"
                fillOpacity={0.35}
                strokeWidth={2.5}
                isAnimationActive={true}
                dot={{
                  r: 4,
                  fill: "hsl(var(--background))",
                  stroke: "#ef4444",
                  strokeWidth: 2
                }}
                activeDot={{
                  r: 6,
                  fill: "#ef4444",
                  stroke: "hsl(var(--background))",
                  strokeWidth: 2
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Resumen inferior detallado */}
        <div className="flex flex-wrap justify-center gap-6 mt-4 pt-4 border-t border-border">
          {chartData.map((dim) => (
            <div key={dim.dimension} className="flex flex-col items-center text-sm">
              <span className="text-muted-foreground text-xs uppercase tracking-wider mb-1">{dim.dimension}</span>
              <div className="flex items-center gap-1.5 font-medium">
                <span className="text-emerald-500">{dim.originalPos}</span>
                <span className="text-border">/</span>
                <span className="text-red-500">{dim.originalNeg}</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}