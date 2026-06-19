"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface DimensionTotal {
  dimension: string
  count: number
  percentage: number
  positive?: number
  negative?: number
}

interface SummaryOverview {
  totalComments: number
  totalAttractions: number
  totalRubros: number
  dimensionTotals: DimensionTotal[]
  topAttractions: Array<{ attraction: string; commentCount: number }>
  topRubros: Array<{ rubro: string; commentCount: number }>
}

interface SummaryOverviewPanelProps {
  title: string
  overview: SummaryOverview
}

export function SummaryOverviewPanel({ title, overview }: SummaryOverviewPanelProps) {
  if (!overview) return null

  // Filtramos para asegurar que no haya dimensiones vacías y ordenamos por volumen total
  const chartData = overview.dimensionTotals
    .filter(d => d.count > 0)
    .sort((a, b) => b.count - a.count)

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Columna Izquierda: Rankings (Top Rubros y Top Atracciones) */}
      <div className="flex flex-col gap-6 md:col-span-1">
        
        {/* Tarjeta: Top Rubros */}
        <Card className="shadow-sm border-border flex-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Top 5 Rubros</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {overview.topRubros.slice(0, 5).map((item, index) => (
                <li key={index} className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground truncate pr-2" title={item.rubro}>
                    {index + 1}. {item.rubro}
                  </span>
                  <span className="font-semibold text-foreground">
                    {item.commentCount.toLocaleString("es-CL")}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Tarjeta: Top Atracciones */}
        <Card className="shadow-sm border-border flex-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Top 5 Atracciones</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {overview.topAttractions.slice(0, 5).map((item, index) => (
                <li key={index} className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground truncate pr-2" title={item.attraction}>
                    {index + 1}. {item.attraction}
                  </span>
                  <span className="font-semibold text-foreground">
                    {item.commentCount.toLocaleString("es-CL")}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Columna Derecha: Gráfico de Dimensiones Apiladas */}
      <Card className="shadow-sm border-border md:col-span-2">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg">Impacto por Dimensión Turística</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Contenedor con altura estricta para evitar que Recharts colapse */}
          <div style={{ width: '100%', height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 10, right: 30, left: 10, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f3f4f6" />
                
                <XAxis 
                  type="number" 
                  tick={{ fontSize: 12, fill: '#6b7280' }} 
                  axisLine={{ stroke: '#e5e7eb' }} 
                />
                
                <YAxis 
                  dataKey="dimension" 
                  type="category" 
                  width={110} 
                  interval={0}
                  tick={{ fontSize: 12, fill: '#4b5563' }}
                  axisLine={{ stroke: '#e5e7eb' }}
                />
                
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                />
                
                <Legend 
                  verticalAlign="top" 
                  align="right" 
                  iconType="circle" 
                  wrapperStyle={{ paddingBottom: '15px' }}
                />
                
                <Bar 
                  dataKey="positive" 
                  name="Positivo" 
                  stackId="a" 
                  fill="#334155" 
                  radius={[0, 0, 0, 0]} 
                />
                <Bar 
                  dataKey="negative" 
                  name="Neutro / Negativo" 
                  stackId="a" 
                  fill="#94a3b8"
                  radius={[0, 4, 4, 0]} 
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}