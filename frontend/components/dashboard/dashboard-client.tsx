"use client"

import { useEffect, useMemo, useState } from "react"
import { AlertCircle, BarChart3, Database, Globe2, Layers3 } from "lucide-react"

import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { ExecutiveSummary } from "@/components/dashboard/executive-summary"
import { SentimentKPIs } from "@/components/dashboard/sentiment-kpis"
import { TXDimensionsChart } from "@/components/dashboard/tx-dimensions-chart"
import { AspectAnalysis } from "@/components/dashboard/aspect-analysis"
import MacroCategoriesChart from "@/components/dashboard/macro-categorias-chart"
import { SummaryOverviewPanel } from "@/components/dashboard/summary-overview-panel"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Spinner } from "@/components/ui/spinner"
import { dashboardData as fallbackDashboardData } from "@/lib/dashboard-data"
import {
  fetchDashboardDataByView,
  fetchVistasDisponibles,
  formatTipoVista,
  type VistaDisponible,
} from "@/lib/backend-api"

export function DashboardClient() {
  const [vistas, setVistas] = useState<VistaDisponible[]>([])
  const [nationalViewId, setNationalViewId] = useState<string>("")
  const [selectedRubroId, setSelectedRubroId] = useState<string>("")
  const [selectedAttractionId, setSelectedAttractionId] = useState<string>("")
  const [nationalData, setNationalData] = useState(fallbackDashboardData)
  const [rubroData, setRubroData] = useState(fallbackDashboardData)
  const [attractionData, setAttractionData] = useState(fallbackDashboardData)
  const [isLoadingViews, setIsLoadingViews] = useState(true)
  const [isLoadingNational, setIsLoadingNational] = useState(false)
  const [isLoadingRubro, setIsLoadingRubro] = useState(false)
  const [isLoadingAttraction, setIsLoadingAttraction] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [compareAttractionId, setCompareAttractionId] = useState<string>("none")
  const [compareData, setCompareData] = useState(fallbackDashboardData)
  const [isLoadingCompare, setIsLoadingCompare] = useState(false)
  const [openAttraction, setOpenAttraction] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadViews() {
      setIsLoadingViews(true)
      setError(null)
      try {
        const response = await fetchVistasDisponibles()
        if (cancelled) return

        setVistas(response)
        const national = response.find((item) => item.tipo_vista === "pais")
        const rubro = response.find((item) => item.tipo_vista === "rubro")
        const attraction = response.find((item) => item.tipo_vista === "atraccion")

        setNationalViewId((current) => current || national?.identificador_vista || response[0]?.identificador_vista || "")
        setSelectedRubroId((current) => current || rubro?.identificador_vista || response[0]?.identificador_vista || "")
        setSelectedAttractionId((current) => current || attraction?.identificador_vista || response[0]?.identificador_vista || "")
      } catch (err) {
        if (cancelled) return
        setError(err instanceof Error ? err.message : "No se pudo cargar el listado de vistas.")
      } finally {
        if (!cancelled) {
          setIsLoadingViews(false)
        }
      }
    }

    loadViews()

    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!nationalViewId) return

    let cancelled = false

    async function loadNational() {
      setIsLoadingNational(true)
      setError(null)
      try {
        const dashboard = await fetchDashboardDataByView(nationalViewId)
        if (cancelled) return
        setNationalData(dashboard)
      } catch (err) {
        if (cancelled) return
        setError(err instanceof Error ? err.message : "No se pudo cargar el análisis nacional.")
      } finally {
        if (!cancelled) {
          setIsLoadingNational(false)
        }
      }
    }

    loadNational()

    return () => {
      cancelled = true
    }
  }, [nationalViewId])

  useEffect(() => {
    if (!compareAttractionId || compareAttractionId === "none") {
      setCompareData(fallbackDashboardData)
      return
    }
    
    let cancelled = false
    async function loadCompare() {
      setIsLoadingCompare(true)
      try {
        const dashboard = await fetchDashboardDataByView(compareAttractionId)
        if (!cancelled) setCompareData(dashboard)
      } catch (err) {
        console.error("Error cargando comparativa", err)
      } finally {
        if (!cancelled) setIsLoadingCompare(false)
      }
    }
    loadCompare()
    return () => { cancelled = true }
  }, [compareAttractionId])

  useEffect(() => {
    if (!selectedRubroId) return

    let cancelled = false

    async function loadRubro() {
      setIsLoadingRubro(true)
      setError(null)
      try {
        const dashboard = await fetchDashboardDataByView(selectedRubroId)
        if (cancelled) return
        setRubroData(dashboard)
      } catch (err) {
        if (cancelled) return
        setError(err instanceof Error ? err.message : "No se pudo cargar el análisis por rubro.")
      } finally {
        if (!cancelled) {
          setIsLoadingRubro(false)
        }
      }
    }

    loadRubro()

    return () => {
      cancelled = true
    }
  }, [selectedRubroId])

  useEffect(() => {
    if (!selectedAttractionId) return

    let cancelled = false

    async function loadAttraction() {
      setIsLoadingAttraction(true)
      setError(null)
      try {
        const dashboard = await fetchDashboardDataByView(selectedAttractionId)
        if (cancelled) return
        setAttractionData(dashboard)
      } catch (err) {
        if (cancelled) return
        setError(err instanceof Error ? err.message : "No se pudo cargar la atracción seleccionada.")
      } finally {
        if (!cancelled) {
          setIsLoadingAttraction(false)
        }
      }
    }

    loadAttraction()

    return () => {
      cancelled = true
    }
  }, [selectedAttractionId])

  const rubroViews = useMemo(() => vistas.filter((item) => item.tipo_vista === "rubro"), [vistas])
  const attractionViews = useMemo(
    () => vistas.filter((item) => item.tipo_vista === "atraccion"),
    [vistas],
  )

  const nationalView = useMemo(
    () => vistas.find((item) => item.identificador_vista === nationalViewId),
    [nationalViewId, vistas],
  )
  const selectedRubroView = useMemo(
    () => vistas.find((item) => item.identificador_vista === selectedRubroId),
    [selectedRubroId, vistas],
  )
  const selectedAttractionView = useMemo(
    () => vistas.find((item) => item.identificador_vista === selectedAttractionId),
    [selectedAttractionId, vistas],
  )

  function renderNeutralHero(title: string, subtitle: string, totalReviews: number) {
    return (
      <Card className="border-muted/70 bg-gradient-to-r from-primary/5 via-background to-background">
        <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10">
              <Globe2 className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">Vista inicial</p>
              <h3 className="text-2xl font-semibold tracking-tight text-foreground">{title}</h3>
              <p className="text-sm text-muted-foreground">{subtitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3 shadow-sm">
            <BarChart3 className="h-4 w-4 text-primary" />
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground">Comentarios analizados</p>
              <p className="text-lg font-semibold text-foreground">{totalReviews.toLocaleString("es-CL")}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }


function renderViewSection(
    title: string,
    data: typeof fallbackDashboardData,
    loading: boolean,
    subtitle?: string,
    variant: "national" | "detail" = "detail",
  ) {
    return (
      <section className="mt-8 space-y-6">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-foreground">{title}</h2>
            {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
          </div>
          {loading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Spinner className="size-4" />
              Actualizando sección...
            </div>
          )}
        </div>

        {variant === "national" ? (
          renderNeutralHero(
            "Panel nacional",
            "Resumen global de todas las atracciones y rubros",
            data.attractionInfo.totalReviews,
          )
        ) : (
          <DashboardHeader name={data.attractionInfo.name} totalReviews={data.attractionInfo.totalReviews} />
        )}

        {/* Se eliminó el SummaryOverviewPanel para ir directo al grano */}

        {/* Se cambió a grid-cols-5 para equilibrar los anchos */}
        <section className="grid grid-cols-1 lg:grid-cols-5 gap-6 pt-4">
          <div className="lg:col-span-3">
            {/* El resumen ahora ocupa 3/5 (levemente más corto) */}
            <ExecutiveSummary summary={data.executiveSummary} />
          </div>
          <div className="lg:col-span-2">
            {/* Los KPIs ahora ocupan 2/5 (más anchos para que quepan bien) */}
            <SentimentKPIs
              positive={data.attractionInfo.sentimentRatio.positive ?? 0}
              negative={data.attractionInfo.sentimentRatio.negative ?? 0}
              neutral={data.attractionInfo.sentimentRatio.neutral ?? 0}
            />
          </div>
        </section>

        <section>
          <TXDimensionsChart 
            dimensions={data.txDimensions} 
            baseName={data.attractionInfo.name}
            // Los siguientes props solo se activan en la pestaña "detail"
            {...(variant === "detail" ? {
              compareDimensions: compareAttractionId !== "none" ? compareData.txDimensions : undefined,
              compareName: compareAttractionId !== "none" ? compareData.attractionInfo.name : undefined,
              attractionsList: attractionViews.map(v => ({ id: v.identificador_vista, name: v.nombre_vista })),
              selectedCompareId: compareAttractionId,
              onCompareChange: setCompareAttractionId,
              isLoadingCompare: isLoadingCompare
            } : {})}
          />
        </section>

        <section>
          <AspectAnalysis
            strengths={data.aspectAnalysis.strengths}
            alerts={data.aspectAnalysis.alerts}
          />
        </section>
      </section>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Contenedor principal de Pestañas */}
        <Tabs defaultValue="global" className="w-full">
          
          <div className="flex flex-col items-center mb-8">
            <TabsList className="grid w-full max-w-md grid-cols-2">
              <TabsTrigger value="global">Visión Global y Rubros</TabsTrigger>
              <TabsTrigger value="atraccion">Análisis por Atracción</TabsTrigger>
            </TabsList>
          </div>

          {/* === INTERFAZ 1: NACIONAL Y RUBROS === */}
          <TabsContent value="global" className="space-y-12 animate-in fade-in-50 duration-500">
            
            {/* SECCIÓN A: CONTEXTO NACIONAL (Macro) */}
            <section className="space-y-6">
              <div className="flex flex-col gap-1">
                <h2 className="text-2xl font-bold tracking-tight text-foreground">Panorama Nacional</h2>
                <p className="text-muted-foreground">Métricas base de todas las atracciones turísticas analizadas a lo largo del país.</p>
              </div>

              {renderNeutralHero(
                "Análisis País",
                "Métricas consolidadas de Chile",
                nationalData.attractionInfo.totalReviews
              )}
              
              <SummaryOverviewPanel
                title="Resumen General País"
                overview={nationalData.summaryOverview}
              />

              {nationalData.macroCategories && nationalData.macroCategories.length > 0 && (
                <div className="pt-6 animate-in slide-in-from-bottom-4 duration-700">
                  <MacroCategoriesChart data={nationalData.macroCategories} />
                </div>
              )}
            </section>

            {/* SECCIÓN B: DESGLOSE POR RUBRO (Dinámico) */}
            <section className="space-y-6 pt-8 border-t">
              <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div className="flex flex-col gap-1">
                  <h2 className="text-2xl font-bold tracking-tight text-foreground">Análisis por Rubro</h2>
                  <p className="text-muted-foreground">Filtra para descubrir tendencias específicas del sector.</p>
                </div>
                
                <div className="w-full md:w-80">
                  <Select
                    value={selectedRubroId}
                    onValueChange={setSelectedRubroId}
                    disabled={isLoadingViews || rubroViews.length === 0}
                  >
                    <SelectTrigger className="w-full shadow-sm">
                      <SelectValue placeholder={isLoadingViews ? "Cargando rubros..." : "Selecciona un rubro"} />
                    </SelectTrigger>
                    <SelectContent>
                      {rubroViews.map((item) => (
                        <SelectItem key={item.identificador_vista} value={item.identificador_vista}>
                          {item.nombre_vista}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {isLoadingRubro ? (
                <div className="flex items-center gap-2 py-12 justify-center text-muted-foreground">
                  <Spinner className="size-5" />
                  <span>Procesando métricas del rubro...</span>
                </div>
              ) : (
                <div className="space-y-6 animate-in fade-in-50 duration-500">
                  {/* Se cambió a grid-cols-5 para equilibrar los anchos */}
                  <section className="grid grid-cols-1 lg:grid-cols-5 gap-6 pt-4">
                    <div className="lg:col-span-3">
                      {/* El resumen ahora ocupa 3/5 (levemente más corto) */}
                      <ExecutiveSummary summary={rubroData.executiveSummary} />
                    </div>
                    <div className="lg:col-span-2">
                      {/* Los KPIs ahora ocupan 2/5 (más anchos para que quepan bien) */}
                      <SentimentKPIs
                        positive={rubroData.attractionInfo.sentimentRatio.positive ?? 0}
                        negative={rubroData.attractionInfo.sentimentRatio.negative ?? 0}
                        neutral={rubroData.attractionInfo.sentimentRatio.neutral ?? 0}
                      />
                    </div>
                  </section>

                  <section>
                    <AspectAnalysis
                      strengths={rubroData.aspectAnalysis.strengths}
                      alerts={rubroData.aspectAnalysis.alerts}
                    />
                  </section>
                </div>
              )}
            </section>
          </TabsContent>

          {/* === INTERFAZ 2: ATRACCIÓN ESPECÍFICA === */}
          <TabsContent value="atraccion" className="space-y-8 animate-in fade-in-50 duration-500">
            <Card className="border-primary/20 shadow-sm">
              <CardHeader className="pb-3 bg-primary/5">
                <CardTitle className="text-base flex items-center gap-2">
                  <Layers3 className="h-4 w-4 text-primary" />
                  Buscador de Atracciones
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <Popover open={openAttraction} onOpenChange={setOpenAttraction}>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={openAttraction}
                        className="w-full justify-between border-primary/30 focus:ring-primary font-normal"
                        disabled={isLoadingViews || attractionViews.length === 0}
                      >
                        {selectedAttractionId
                          ? attractionViews.find((view) => view.identificador_vista === selectedAttractionId)?.nombre_vista
                          : isLoadingViews 
                            ? "Cargando atracciones..." 
                            : "Busca o selecciona una atracción..."}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-[400px] p-0" align="start">
                      <Command>
                        <CommandInput placeholder="Escribe para buscar..." />
                        <CommandList>
                          <CommandEmpty>No se encontraron resultados.</CommandEmpty>
                          <CommandGroup>
                            {attractionViews.map((view) => (
                              <CommandItem
                                key={view.identificador_vista}
                                value={view.nombre_vista}
                                onSelect={() => {
                                  setSelectedAttractionId(view.identificador_vista)
                                  setOpenAttraction(false)
                                }}
                              >
                                <Check
                                  className={cn(
                                    "mr-2 h-4 w-4",
                                    selectedAttractionId === view.identificador_vista ? "opacity-100" : "opacity-0"
                                  )}
                                />
                                {view.nombre_vista}
                              </CommandItem>
                            ))}
                          </CommandGroup>
                        </CommandList>
                      </Command>
                    </PopoverContent>
                  </Popover>
              </CardContent>
            </Card>

            {selectedAttractionId ? (
              renderViewSection(
                "Vista de Atracción",
                attractionData,
                isLoadingAttraction,
                selectedAttractionView ? `Analizando: ${selectedAttractionView.nombre_vista}` : ""
              )
            ) : (
              <div className="text-center py-20 text-muted-foreground">
                Selecciona una atracción en el menú superior para ver su análisis detallado.
              </div>
            )}
          </TabsContent>
          
        </Tabs>

        {/* Manejo de errores global */}
        {error && (
          <Alert variant="destructive" className="mt-8">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error de conexión</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>
    </main>
  )
}