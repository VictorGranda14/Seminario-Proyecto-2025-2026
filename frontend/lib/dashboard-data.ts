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
    { dimension: "Hedonismo", score: 85 },
    { dimension: "Cultura Local", score: 70 },
    { dimension: "Conocimiento", score: 65 },
    { dimension: "Participación", score: 50 },
    { dimension: "Renovación", score: 30 },
    { dimension: "Significado", score: 15 },
    { dimension: "Novedad", score: 0 }
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
  // Inyectamos la estructura vacía tipada
  macroCategories: [] as Array<{
    category: string;
    freq: number;
    positiveCount: number;
    negativeCount: number;
  }>
}

export type DashboardData = typeof dashboardData