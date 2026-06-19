export const dashboardData = {
  attractionInfo: {
    name: "Viña Santa Rita",
    totalReviews: 153446,
    sentimentRatio: { positive: 78, neutral: 0, negative: 22 }
  },
  summaryOverview: {
    totalComments: 153446,
    totalAttractions: 1,
    totalRubros: 1,
    dimensionTotals: [
      { dimension: "Hedonismo", count: 40120, percentage: 26.12 },
      { dimension: "Cultura Local", count: 31240, percentage: 20.34 },
      { dimension: "Conocimiento", count: 28110, percentage: 18.31 },
      { dimension: "Participación", count: 22010, percentage: 14.33 },
      { dimension: "Renovación", count: 14120, percentage: 9.19 },
    ],
    topAttractions: [
      { attraction: "Viña Santa Rita", commentCount: 153446 }
    ],
    topRubros: [
      { rubro: "Viñas", commentCount: 153446 }
    ]
  },
  executiveSummary: "La experiencia general es altamente valorada, destacando el profesionalismo de los guías y la calidad del tour clásico. Sin embargo, existe una fricción operativa crítica relacionada con el sistema de reservas y quejas emergentes sobre la relación precio-calidad en la degustación de vinos.",
  txDimensions: [
    { dimension: "Hedonismo", total: 85, positive: 70, negative: 15 },
    { dimension: "Cultura Local", total: 70, positive: 60, negative: 10 },
    { dimension: "Conocimiento", total: 65, positive: 50, negative: 15 },
    { dimension: "Participación", total: 50, positive: 45, negative: 5 },
    { dimension: "Renovación", total: 30, positive: 20, negative: 10 },
    { dimension: "Significado", total: 15, positive: 10, negative: 5 },
    { dimension: "Novedad", total: 0, positive: 0, negative: 0 }
  ],
  dimensionTotals: [
      { dimension: "Hedonismo", count: 40120, percentage: 26.12, positive: 30000, negative: 10120 },
      { dimension: "Cultura Local", count: 31240, percentage: 20.34, positive: 25000, negative: 6240 },
      { dimension: "Conocimiento", count: 28110, percentage: 18.31, positive: 20000, negative: 8110 },
      { dimension: "Participación", count: 22010, percentage: 14.33, positive: 18000, negative: 2010 },
      { dimension: "Renovación", count: 14120, percentage: 9.19, positive: 10000, negative: 4120 },
      { dimension: "Significado", count: 8000, percentage: 5.22, positive: 6000, negative: 2000 },
      { dimension: "Novedad", count: 5000, percentage: 3.26, positive: 4000, negative: 1000 }
  ],
  aspectAnalysis: {
    strengths: [
      { aspect: "tour", freq: 302, keywords: "great, excellent, private" },
      { aspect: "wine", freq: 301, keywords: "great, delicious, fantastic" },
      { aspect: "guide", freq: 274, keywords: "knowledgeable, wonderful" }
    ],
    alerts: [
      { aspect: "wine", freq: 34, keywords: "not good, actual, worth" },
      { aspect: "reservation", freq: 14, keywords: "very, must, wise" },
      { aspect: "price", freq: 7, keywords: "steep, expensive" }
    ]
  },
  macroCategories: [] as Array<{
    category: string;
    freq: number;
    positiveCount: number;
    negativeCount: number;
  }>
}

export type DashboardData = typeof dashboardData