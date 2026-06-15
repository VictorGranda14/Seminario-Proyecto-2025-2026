"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer, Tooltip, Legend } from "recharts"
import { Target, Loader2, Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

interface TXDimension {
  dimension: string
  score: number
}

interface AttractionOption {
  id: string
  name: string
}

interface TXDimensionsChartProps {
  dimensions: TXDimension[]
  baseName?: string
  compareDimensions?: TXDimension[]
  compareName?: string
  attractionsList?: AttractionOption[]
  selectedCompareId?: string
  onCompareChange?: (id: string) => void
  isLoadingCompare?: boolean
}

export function TXDimensionsChart({ 
  dimensions, 
  baseName = "Atracción Actual",
  compareDimensions,
  compareName,
  attractionsList = [],
  selectedCompareId,
  onCompareChange,
  isLoadingCompare = false
}: TXDimensionsChartProps) {

  const [openCompare, setOpenCompare] = useState(false)

  // Fusionamos los datos usando llaves estáticas seguras para el motor de Recharts
  const mergedData = useMemo(() => {
    return dimensions.map(baseItem => {
      const compareItem = compareDimensions?.find(c => c.dimension === baseItem.dimension)
      const compareScore = compareItem ? compareItem.score : 0.1 
      
      return {
        dimension: baseItem.dimension,
        baseScore: baseItem.score === 0 ? 0.1 : baseItem.score,
        compareScore: compareScore
      }
    })
  }, [dimensions, compareDimensions])

  const formatScore = (val: number) => val === 0.1 ? 0 : val

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-2">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <Target className="h-4 w-4 text-primary" />
          </div>
          <div>
            <CardTitle className="text-base">Dimensiones de Experiencia Turística</CardTitle>
            <CardDescription>Análisis multidimensional de la experiencia del visitante</CardDescription>
          </div>
        </div>

        {/* Selector de Comparación con Combobox (Buscador) */}
        {attractionsList.length > 0 && onCompareChange && (
          <div className="w-full sm:w-[260px]">
            <Popover open={openCompare} onOpenChange={setOpenCompare}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={openCompare}
                  className="w-full justify-between h-8 text-xs border-primary/30 focus:ring-primary font-normal"
                >
                  {isLoadingCompare ? (
                    <div className="flex items-center gap-2"><Loader2 className="h-3 w-3 animate-spin"/> Cargando...</div>
                  ) : selectedCompareId && selectedCompareId !== "none" ? (
                    attractionsList.find((attr) => attr.id === selectedCompareId)?.name
                  ) : (
                    "Comparar con..."
                  )}
                  <ChevronsUpDown className="ml-2 h-3 w-3 shrink-0 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-[300px] p-0" align="end">
                <Command>
                  <CommandInput placeholder="Buscar atracción para comparar..." className="text-xs" />
                  <CommandList>
                    <CommandEmpty>No se encontraron resultados.</CommandEmpty>
                    <CommandGroup>
                      {/* Opción para limpiar la comparación */}
                      <CommandItem
                        value="Quitar comparación ninguna"
                        onSelect={() => {
                          onCompareChange("none")
                          setOpenCompare(false)
                        }}
                        className="text-xs text-muted-foreground italic"
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4",
                            selectedCompareId === "none" || !selectedCompareId ? "opacity-100" : "opacity-0"
                          )}
                        />
                        Quitar comparación
                      </CommandItem>
                      
                      {/* Lista dinámica de atracciones */}
                      {attractionsList.map((attr) => (
                        <CommandItem
                          key={attr.id}
                          value={attr.name}
                          onSelect={() => {
                            onCompareChange(attr.id)
                            setOpenCompare(false)
                          }}
                          className="text-xs"
                        >
                          <Check
                            className={cn(
                              "mr-2 h-4 w-4",
                              selectedCompareId === attr.id ? "opacity-100" : "opacity-0"
                            )}
                          />
                          {attr.name}
                        </CommandItem>
                      ))}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </PopoverContent>
            </Popover>
          </div>
        )}
      </CardHeader>
      
      <CardContent>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={mergedData} margin={{ top: 20, right: 40, bottom: 20, left: 40 }} cx="50%" cy="50%" outerRadius="90%">
              <PolarGrid stroke="#cbd5e1" strokeWidth={0.75} gridType="circle" radialLines={true} />
              <PolarAngleAxis dataKey="dimension" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12, fontWeight: 500 }} />
              
              <Tooltip 
                formatter={(value: number) => [`${formatScore(value)}%`]}
                contentStyle={{ borderRadius: '8px', fontSize: '13px' }}
              />
              <Legend wrapperStyle={{ fontSize: '13px', paddingTop: '10px' }} />

              {/* Polígono de la Atracción Base */}
              <Radar
                name={baseName}
                dataKey="baseScore"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.3}
                strokeWidth={2.5}
                isAnimationActive={false}
                dot={{
                  r: 4,
                  fill: "hsl(var(--background))",
                  stroke: "hsl(var(--primary))",
                  strokeWidth: 2
                }}
                activeDot={{
                  r: 6,
                  fill: "hsl(var(--primary))",
                  stroke: "hsl(var(--background))",
                  strokeWidth: 2
                }}
              />

              {/* Polígono del Competidor */}
              {compareName && (
                <Radar
                  name={compareName}
                  dataKey="compareScore"
                  stroke="#10b981" 
                  fill="#10b981"
                  fillOpacity={0.3}
                  strokeWidth={2.5}
                  isAnimationActive={false}
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
              )}
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Resumen inferior */}
        <div className="flex flex-wrap justify-center gap-4 mt-4 pt-4 border-t border-border">
          {dimensions.map((dim) => (
            <div key={dim.dimension} className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">{dim.dimension}:</span>
              <span className="font-semibold text-foreground">{formatScore(dim.score)}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}