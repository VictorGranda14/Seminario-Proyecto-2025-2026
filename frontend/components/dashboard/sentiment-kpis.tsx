"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ThumbsUp, ThumbsDown } from "lucide-react"

interface SentimentKPIsProps {
  positive: number
  negative: number
}

export function SentimentKPIs({ positive, negative }: SentimentKPIsProps) {
  return (
    <div className="grid grid-cols-2 gap-4 h-full">
      <Card className="bg-success/5 border-success/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <ThumbsUp className="h-4 w-4 text-success" />
            Positivo
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-success">{positive}</span>
            <span className="text-lg text-success/70">%</span>
          </div>
        </CardContent>
      </Card>
      
      <Card className="bg-destructive/5 border-destructive/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <ThumbsDown className="h-4 w-4 text-destructive" />
            Negativo
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-destructive">{negative}</span>
            <span className="text-lg text-destructive/70">%</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
