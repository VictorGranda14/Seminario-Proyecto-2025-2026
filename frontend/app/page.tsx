import { dashboardData } from "@/lib/dashboard-data"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { ExecutiveSummary } from "@/components/dashboard/executive-summary"
import { SentimentKPIs } from "@/components/dashboard/sentiment-kpis"
import { TXDimensionsChart } from "@/components/dashboard/tx-dimensions-chart"
import { AspectAnalysis } from "@/components/dashboard/aspect-analysis"

export default function DashboardPage() {
  const { attractionInfo, executiveSummary, txDimensions, aspectAnalysis } = dashboardData

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <DashboardHeader 
          name={attractionInfo.name} 
          totalReviews={attractionInfo.totalReviews} 
        />
        
        {/* Row 1: Executive Summary & KPIs */}
        <section className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ExecutiveSummary summary={executiveSummary} />
          </div>
          <div>
            <SentimentKPIs 
              positive={attractionInfo.sentimentRatio.positive} 
              negative={attractionInfo.sentimentRatio.negative} 
            />
          </div>
        </section>

        {/* Row 2: TX Dimensions Radar Chart */}
        <section className="mt-6">
          <TXDimensionsChart dimensions={txDimensions} />
        </section>

        {/* Row 3: ABSA Analysis */}
        <section className="mt-6">
          <AspectAnalysis 
            strengths={aspectAnalysis.strengths} 
            alerts={aspectAnalysis.alerts} 
          />
        </section>
      </div>
    </main>
  )
}
