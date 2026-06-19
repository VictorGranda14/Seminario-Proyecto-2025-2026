import type { DashboardData } from "@/lib/dashboard-data"

export interface VistaDisponible {
  identificador_vista: string
  nombre_vista: string
  tipo_vista: "atraccion" | "rubro" | "pais" | string
  ultima_actualizacion: string
}

interface BackendMetricasPayload {
  vistaInfo?: {
    identificadorVista?: string
    nombreVista?: string
    tipoVista?: string
    totalReviews?: number
    sentimentRatio?: {
      positive?: number
      neutral?: number
      negative?: number
    }
  }
  summaryOverview?: {
    totalComments?: number
    totalAttractions?: number
    totalRubros?: number
    dimensionTotals?: Array<{
      dimension?: string
      count?: number
      percentage?: number
      positive?: number
      negative?: number
    }>
    topAttractions?: Array<{
      attraction?: string
      commentCount?: number
    }>
    topRubros?: Array<{
      rubro?: string
      commentCount?: number
    }>
  }
  executiveSummary?: string
  txDimensions?: Array<{
    dimension?: string
    total?: number
    positive?: number
    negative?: number
  }>
  aspectAnalysis?: {
    strengths?: Array<{ aspect?: string; freq?: number; keywords?: string[] | string }>
    alerts?: Array<{ aspect?: string; freq?: number; keywords?: string[] | string }>
  }
  macroCategories?: Array<{
    category?: string
    freq?: number
    positiveCount?: number
    negativeCount?: number
  }>
  identificador_vista?: string
  nombre_vista?: string
  tipo_vista?: string
}

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"

function getBackendBaseUrl() {
  return process.env.NEXT_PUBLIC_BACKEND_URL?.trim() || DEFAULT_BACKEND_URL
}

async function fetchJson<T>(path: string): Promise<T> {
  const baseUrl = getBackendBaseUrl()
  const response = await fetch(`${baseUrl}${path}`, {
    cache: "no-store",
  })

  if (!response.ok) {
    const body = await response.text()
    throw new Error(`Error ${response.status} en ${path}: ${body || "sin detalle"}`)
  }

  return response.json() as Promise<T>
}

function normalizeKeywords(value: string[] | string | undefined): string {
  if (Array.isArray(value)) {
    return value.join(", ")
  }
  if (typeof value === "string") {
    return value
  }
  return ""
}

function toDashboardData(payload: BackendMetricasPayload): DashboardData {
  const name = payload.vistaInfo?.nombreVista || payload.nombre_vista || "Vista sin nombre"
  const totalReviews = Number(payload.vistaInfo?.totalReviews || 0)
  const positive = Number(payload.vistaInfo?.sentimentRatio?.positive || 0)
  const neutral = Number(payload.vistaInfo?.sentimentRatio?.neutral || 0)
  const negative = Number(payload.vistaInfo?.sentimentRatio?.negative || 0)

  // 1. Definimos la plantilla estricta de las 7 dimensiones
  const STANDARD_DIMENSIONS = [
    "Hedonismo",
    "Cultura Local",
    "Conocimiento",
    "Participación",
    "Renovación",
    "Significado",
    "Novedad"
  ]

  // 2. Función auxiliar para comparar ignorando tildes y mayúsculas
  const normalizeString = (str: string) => 
    str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim()

  const rawDimensions = payload.txDimensions || []

  const txDimensions = STANDARD_DIMENSIONS.map((stdDim) => {
    const found = rawDimensions.find(
      (item) => item.dimension && normalizeString(item.dimension) === normalizeString(stdDim)
    )
    return {
      dimension: stdDim,
      total: found ? Number(found.total || 0) : 0,
      positive: found ? Number(found.positive || 0) : 0,
      negative: found ? Number(found.negative || 0) : 0,
    }
  })
  

  const strengths = (payload.aspectAnalysis?.strengths || []).map((item) => ({
    aspect: item.aspect || "general",
    freq: Number(item.freq || 0),
    keywords: normalizeKeywords(item.keywords),
  }))

  const alerts = (payload.aspectAnalysis?.alerts || []).map((item) => ({
    aspect: item.aspect || "general",
    freq: Number(item.freq || 0),
    keywords: normalizeKeywords(item.keywords),
  }))

  const macroCategories = (payload.macroCategories || []).map((item) => ({
    category: item.category || "Sin clasificar",
    freq: Number(item.freq || 0),
    positiveCount: Number(item.positiveCount || 0),
    negativeCount: Number(item.negativeCount || 0),
  }))

  const summaryOverview = {
    totalComments: Number(payload.summaryOverview?.totalComments || totalReviews),
    totalAttractions: Number(payload.summaryOverview?.totalAttractions || 0),
    totalRubros: Number(payload.summaryOverview?.totalRubros || 0),
    dimensionTotals: (payload.summaryOverview?.dimensionTotals || []).map((item) => ({
      dimension: item.dimension || "Sin clasificar",
      count: Number(item.count || 0),
      percentage: Number(item.percentage || 0),
      positive: Number(item.positive || 0),
      negative: Number(item.negative || 0),
    })),
    topAttractions: (payload.summaryOverview?.topAttractions || []).map((item) => ({
      attraction: item.attraction || "Sin nombre",
      commentCount: Number(item.commentCount || 0),
    })),
    topRubros: (payload.summaryOverview?.topRubros || []).map((item) => ({
      rubro: item.rubro || "Sin nombre",
      commentCount: Number(item.commentCount || 0),
    })),
  }

  return {
    attractionInfo: {
      name,
      totalReviews,
      sentimentRatio: {
        positive,
        neutral,
        negative,
      },
    },
    dimensionTotals: summaryOverview.dimensionTotals,
    summaryOverview,
    executiveSummary:
      payload.executiveSummary || "Aun no hay resumen generado para esta vista.",
    txDimensions,
    aspectAnalysis: {
      strengths,
      alerts,
    },
    macroCategories,
  }
}

export async function fetchVistasDisponibles(): Promise<VistaDisponible[]> {
  return fetchJson<VistaDisponible[]>("/metricas/disponibles")
}

export async function fetchDashboardDataByView(
  identificadorVista: string,
): Promise<DashboardData> {
  const payload = await fetchJson<BackendMetricasPayload>(
    `/metricas/${encodeURIComponent(identificadorVista)}`,
  )
  return toDashboardData(payload)
}

export function formatTipoVista(tipoVista: string): string {
  if (tipoVista === "atraccion") return "Atraccion"
  if (tipoVista === "rubro") return "Rubro"
  if (tipoVista === "pais") return "Pais"
  return tipoVista
}