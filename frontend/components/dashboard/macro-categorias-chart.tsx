"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, LabelList
} from "recharts"

interface MacroCategoryData {
  category: string
  freq: number
  positiveCount: number
  negativeCount: number
}

interface MacroCategoriesChartProps {
  data: MacroCategoryData[]
}

const CATEGORY_TRANSLATIONS: Record<string, string> = {
  "Variety of Activities": "Variedad de Actividades",
  "Hospitality": "Hospitalidad",
  "Quality of Service": "Calidad del Servicio",
  "Local Culture and History": "Cultura e Historia Local",
  "Physiography": "Fisiografía",
  "Food": "Comida",
  "Accessibility": "Accesibilidad",
  "Environment Management": "Gestión del Entorno",
  "Infrastructure": "Infraestructura",
  "Weather": "Clima",
  "Price": "Precio",
  "Safety": "Seguridad",
  "Visitor Management": "Gestión de Visitantes",
}

const MIN_PIXELS_FOR_INNER_LABEL = 35

const formatNumber = (n: number) =>
  n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${n}`

// Renderizador para la barra Positiva (Verde)
const renderPositiveLabel = (props: any) => {
  const { x, y, width, value } = props
  if (!value) return null
  
  const label = formatNumber(value)

  return (
    <text
      x={x + width / 2}
      y={y - 4}
      textAnchor="middle"
      dominantBaseline="auto"
      fontSize={10}
      fontFamily="Inter, system-ui, sans-serif"
      fill="#2d6a4f"
      fontWeight={600}
    >
      {label}
    </text>
  )
}

// Renderizador para la barra Negativa (Roja)
const renderNegativeLabel = (props: any) => {
  const { x, y, width, value, index, data } = props
  if (!value || !data) return null
  
  const label = formatNumber(value)

  // Extraemos el valor positivo para calcular matemáticamente el ancho de la barra verde en pantalla
  const posValue = data[index]?.positiveCount || 1
  const greenWidth = width * (posValue / value)

  // Distancia en píxeles entre el centro de la verde y el centro de la roja
  const distanceBetweenCenters = (greenWidth + width) / 2

  // Si los centros están a menos de 28 píxeles (riesgo inminente de choque frontal)
  // Y la barra roja es muy delgada (menor a 25px), la empujamos a la derecha.
  if (distanceBetweenCenters < 28 && width < 25) {
    return (
      <text
        x={x + width + 4}
        y={y - 4}
        textAnchor="start"
        dominantBaseline="auto"
        fontSize={10}
        fontFamily="Inter, system-ui, sans-serif"
        fill="#c0392b"
        fontWeight={600}
      >
        {label}
      </text>
    )
  }

  // Si hay distancia suficiente (porque la verde es grande o la roja es ancha), se queda centrada.
  return (
    <text
      x={x + width / 2}
      y={y - 4}
      textAnchor="middle"
      dominantBaseline="auto"
      fontSize={10}
      fontFamily="Inter, system-ui, sans-serif"
      fill="#c0392b"
      fontWeight={600}
    >
      {label}
    </text>
  )
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  const pos = payload.find((p: any) => p.dataKey === "positiveCount")
  const neg = payload.find((p: any) => p.dataKey === "negativeCount")
  const total = (pos?.value ?? 0) + (neg?.value ?? 0)
  const negRatio = total > 0 ? ((neg?.value / total) * 100).toFixed(1) : "0"

  return (
    <div style={{
      background: "#fff",
      border: "1px solid #e2e8f0",
      borderRadius: 8,
      padding: "10px 14px",
      fontSize: 12,
      fontFamily: "Inter, system-ui, sans-serif",
      boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
      minWidth: 200,
    }}>
      <p style={{ fontWeight: 600, marginBottom: 6, color: "#1e293b" }}>{label}</p>
      <p style={{ color: "#1b6b3a", marginBottom: 2 }}>
        Positivo: <strong>{pos?.value?.toLocaleString('es-CL')}</strong>
      </p>
      <p style={{ color: "#c0392b", marginBottom: 2 }}>
        Negativo: <strong>{neg?.value?.toLocaleString('es-CL')}</strong>
      </p>
      <p style={{ color: "#64748b", marginTop: 4, borderTop: "1px solid #f1f5f9", paddingTop: 4 }}>
        Tasa de fricción: <strong>{negRatio}%</strong>
      </p>
    </div>
  )
}

export function MacroCategoriesChart({ data }: MacroCategoriesChartProps) {
  if (!data || data.length === 0) return null

  const translatedData = data.map(item => ({
    ...item,
    categoryName: CATEGORY_TRANSLATIONS[item.category] || item.category,
  }))

  const chartHeight = Math.max(400, translatedData.length * 38)

  return (
    <Card className="shadow-sm border-border h-full flex flex-col">
      <CardHeader style={{ paddingBottom: 8 }}>
        <CardTitle style={{
          fontSize: 16,
          fontWeight: 600,
          color: "#1e293b",
          letterSpacing: "-0.01em",
        }}>
          Desempeño por Categoría
        </CardTitle>
        <CardDescription style={{ fontSize: 13, color: "#64748b" }}>
          Distribución de impacto positivo y negativo en atributos estructurales
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 pt-2">
        <div style={{ width: "100%", height: chartHeight }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={translatedData}
              layout="vertical"
              margin={{ top: 4, right: 40, left: 10, bottom: 0 }}
              barCategoryGap="25%"
            >
              <CartesianGrid
                strokeDasharray="4 4"
                horizontal={false}
                vertical={true}
                stroke="#f1f5f9"
              />

              <XAxis
                type="number"
                tick={{ fontSize: 11, fill: "#94a3b8", fontFamily: "Inter, system-ui, sans-serif" }}
                axisLine={{ stroke: "#e2e8f0" }}
                tickLine={false}
                tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : `${v}`}
              />

              <YAxis
                dataKey="categoryName"
                type="category"
                width={165}
                interval={0}
                tick={{ fontSize: 12, fill: "#475569", fontFamily: "Inter, system-ui, sans-serif", fontWeight: 500 }}
                axisLine={false}
                tickLine={false}
              />

              <Tooltip content={<CustomTooltip />} cursor={{ fill: "#f8fafc" }} />

              <Legend
                verticalAlign="top"
                align="right"
                iconType="circle"
                iconSize={8}
                wrapperStyle={{
                  paddingBottom: 20,
                  fontSize: 12,
                  fontFamily: "Inter, system-ui, sans-serif",
                  color: "#475569",
                }}
                formatter={(value) =>
                  value === "Positivo"
                    ? <span style={{ color: "#2d6a4f", fontWeight: 500 }}>Positivo</span>
                    : <span style={{ color: "#e05c4b", fontWeight: 500 }}>Negativo</span>
                }
              />

              <Bar
                dataKey="positiveCount"
                name="Positivo"
                stackId="a"
                fill="#2d6a4f"
                radius={[0, 0, 0, 0]}
                isAnimationActive={false}
              >
                <LabelList
                  dataKey="positiveCount"
                  content={renderPositiveLabel}
                />
              </Bar>

              <Bar
                dataKey="negativeCount"
                name="Negativos"
                stackId="a"
                fill="#e05c4b"
                radius={[0, 4, 4, 0]}
                isAnimationActive={false}
              >
                <LabelList
                  dataKey="negativeCount"
                  content={(props) => renderNegativeLabel({ ...props, data: translatedData })}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}