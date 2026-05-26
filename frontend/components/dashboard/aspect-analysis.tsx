"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, AlertTriangle } from "lucide-react"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Cell, Tooltip } from "recharts"

interface AspectItem {
  aspect: string
  freq: number
  keywords: string
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
  const barColor = isStrength ? "hsl(var(--success))" : "hsl(var(--destructive))"
  const bgColor = isStrength ? "bg-success/10" : "bg-destructive/10"
  const iconColor = isStrength ? "text-success" : "text-destructive"
  
  const chartData = items.map(item => ({
    aspect: item.aspect.charAt(0).toUpperCase() + item.aspect.slice(1),
    freq: item.freq,
    keywords: item.keywords
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
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div className="bg-popover border border-border rounded-lg p-3 shadow-lg">
                        <p className="font-medium text-foreground">{data.aspect}</p>
                        <p className="text-sm text-muted-foreground">
                          Frecuencia: <span className="font-semibold text-foreground">{data.freq}</span>
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Bar 
                dataKey="freq" 
                radius={[0, 4, 4, 0]}
                barSize={24}
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={barColor} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="space-y-3">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Opiniones Clave por Aspecto
          </p>
          {items.map((item) => (
            <div key={item.aspect} className="space-y-2">
              <p className="text-sm font-medium text-foreground capitalize">{item.aspect}</p>
              <div className="flex flex-wrap gap-1.5">
                {item.keywords.split(", ").map((keyword) => (
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
