"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, AlertTriangle } from "lucide-react"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"

// 1. Actualizamos la interfaz para soportar la data de Python (array) 
// y la variable totalFreq que agregamos al backend
interface AspectItem {
  aspect: string
  freq: number
  totalFreq?: number 
  keywords: string | string[]
}

interface AspectAnalysisProps {
  strengths: AspectItem[]
  alerts: AspectItem[]
}

function AspectCard({ 
  title, 
  description,
  items, 
  type,
  icon: Icon
}: { 
  title: string
  description: string
  items: AspectItem[]
  type: "strength" | "alert"
  icon: typeof TrendingUp
}) {
  const isStrength = type === "strength"
  const barColor = isStrength ? "#2eab79" : "#d9534f" 
  const bgColor = isStrength ? "bg-success/10" : "bg-destructive/10"
  const iconColor = isStrength ? "text-success" : "text-destructive"
  
  // 2. Normalizamos la data para que el gráfico y las keywords no crasheen
  const chartData = items.map(item => ({
    aspect: item.aspect.charAt(0).toUpperCase() + item.aspect.slice(1),
    freq: item.freq,
    totalFreq: item.totalFreq,
    // Soporta tanto el fallback (string) como el script Python (array)
    keywords: Array.isArray(item.keywords) ? item.keywords : item.keywords.split(", ")
  }))

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${bgColor}`}>
            <Icon className={`h-4 w-4 ${iconColor}`} />
          </div>
          <div>
            <CardTitle className="text-base">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={chartData} 
              layout="vertical"
              margin={{ top: 0, right: 20, bottom: 0, left: 0 }}
            >
              <XAxis 
                type="number" 
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                dataKey="aspect" 
                type="category" 
                tick={{ fill: "hsl(var(--foreground))", fontSize: 12, fontWeight: 500 }}
                axisLine={false}
                tickLine={false}
                width={80}
              />
              <Tooltip
                cursor={{ fill: "transparent" }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
                        <p className="font-medium text-foreground">{data.aspect}</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          {isStrength ? "Positivos" : "Quejas directas"}: <span className="font-semibold text-foreground">{data.freq}</span>
                          {data.totalFreq && (
                            <span className="text-xs text-muted-foreground ml-1 block">
                              (de {data.totalFreq} menciones totales)
                            </span>
                          )}
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Bar 
                dataKey="freq" 
                fill={barColor}
                radius={[0, 4, 4, 0]}
                barSize={24}
                isAnimationActive={false} 
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="space-y-3">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Opiniones Clave por Aspecto
          </p>
          {chartData.map((item) => (
            <div key={item.aspect} className="space-y-2">
              <p className="text-sm font-medium text-foreground capitalize">{item.aspect}</p>
              <div className="flex flex-wrap gap-1.5">
                {item.keywords.map((keyword: string) => (
                  <Badge 
                    key={keyword} 
                    variant="secondary" 
                    className={`text-xs font-normal ${
                      isStrength 
                        ? "bg-success/10 text-success border-success/20" 
                        : "bg-destructive/10 text-destructive border-destructive/20"
                    }`}
                  >
                    {keyword}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export function AspectAnalysis({ strengths, alerts }: AspectAnalysisProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <AspectCard 
        title="Fortalezas"
        description="Aspectos mejor valorados por los visitantes"
        items={strengths} 
        type="strength"
        icon={TrendingUp}
      />
      <AspectCard 
        title="Alertas y Fricciones"
        description="Áreas que requieren atención inmediata"
        items={alerts} 
        type="alert"
        icon={AlertTriangle}
      />
    </div>
  )
}