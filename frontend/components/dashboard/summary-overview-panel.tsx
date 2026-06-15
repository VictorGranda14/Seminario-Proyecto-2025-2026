"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart3, Building2, MapPinned, Users } from "lucide-react"

interface DimensionTotalItem {
  dimension: string
  count: number
  percentage: number
}

interface RankedAttractionItem {
  attraction: string
  commentCount: number
}

interface RankedRubroItem {
  rubro: string
  commentCount: number
}

interface SummaryOverviewData {
  totalComments: number
  totalAttractions: number
  totalRubros: number
  dimensionTotals: DimensionTotalItem[]
  topAttractions: RankedAttractionItem[]
  topRubros: RankedRubroItem[]
}

interface SummaryOverviewPanelProps {
  title: string
  overview: SummaryOverviewData
}

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Users
  label: string
  value: string
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        <div>
          <p className="text-xs uppercase tracking-wider text-muted-foreground">{label}</p>
          <p className="text-2xl font-semibold text-foreground">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}

function RankingCard({
  title,
  badgeLabel,
  items,
  emptyText,
}: {
  title: string
  badgeLabel: string
  items: Array<{ label: string; value: number }>
  emptyText: string
}) {
  const maxValue = Math.max(...items.map((item) => item.value), 1)

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-3">
          <CardTitle className="text-sm">{title}</CardTitle>
          <Badge variant="secondary" className="text-xs">
            {badgeLabel}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">{emptyText}</p>
        ) : (
          items.map((item, index) => (
            <div key={`${item.label}-${index}`} className="space-y-1">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-foreground">{item.label}</span>
                <span className="text-muted-foreground">{item.value}</span>
              </div>
              <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary"
                  style={{ width: `${Math.max(8, Math.round((item.value / maxValue) * 100))}%` }}
                />
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}

export function SummaryOverviewPanel({ title, overview }: SummaryOverviewPanelProps) {
  const dimensionItems = overview.dimensionTotals.map((item) => ({
    label: `${item.dimension} · ${item.percentage}%`,
    value: item.count,
  }))

  const attractionItems = overview.topAttractions.map((item) => ({
    label: item.attraction,
    value: item.commentCount,
  }))

  const rubroItems = overview.topRubros.map((item) => ({
    label: item.rubro,
    value: item.commentCount,
  }))

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-primary" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard icon={Users} label="Comentarios totales" value={overview.totalComments.toLocaleString("es-CL")} />
          <StatCard icon={MapPinned} label="Atracciones" value={overview.totalAttractions.toString()} />
          <StatCard icon={Building2} label="Rubros" value={overview.totalRubros.toString()} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-1">
            <RankingCard
              title="Dimensiones totales"
              badgeLabel="impacto global"
              items={dimensionItems}
              emptyText="Sin dimensiones registradas todavía."
            />
          </div>
          <RankingCard
            title="Top atracciones"
            badgeLabel="más comentarios"
            items={attractionItems}
            emptyText="Sin atracciones para mostrar."
          />
          <RankingCard
            title="Top rubros"
            badgeLabel="más comentarios"
            items={rubroItems}
            emptyText="Sin rubros para mostrar."
          />
        </div>
      </CardContent>
    </Card>
  )
}
