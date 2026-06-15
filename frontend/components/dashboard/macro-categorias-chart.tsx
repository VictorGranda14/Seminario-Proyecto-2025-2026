import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

export interface MacroCategory {
  category: string;
  freq: number;
  positiveCount: number;
  negativeCount: number;
}

export default function MacroCategoriesChart({ data }: { data: MacroCategory[] }) {
  if (!data || data.length === 0) {
    return <div className="p-4 text-center text-gray-500">No hay datos de macro categorías disponibles.</div>;
  }

  return (
    <div className="w-full bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-800 mb-6">Desempeño por Categoría Oficial</h3>
      
      {/* Contenedor estricto para evitar el colapso de altura a 0px */}
      <div style={{ width: '100%', height: 600 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 0, right: 30, left: 10, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f3f4f6" />
            
            <XAxis 
              type="number" 
              tick={{ fontSize: 12, fill: '#6b7280' }} 
              axisLine={{ stroke: '#e5e7eb' }} 
            />
            
            <YAxis 
              dataKey="category" 
              type="category" 
              width={160} 
              interval={0} // Muestra todos los nombres obligatoriamente
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
              wrapperStyle={{ paddingBottom: '20px' }}
            />
            
            <Bar 
              dataKey="positiveCount" 
              name="Positivo" 
              stackId="a" 
              fill="#334155" // Slate 700
              radius={[0, 0, 0, 0]} 
            />
            <Bar 
              dataKey="negativeCount" 
              name="Negativo" 
              stackId="a" 
              fill="#94a3b8" // Slate 400
              radius={[0, 4, 4, 0]} 
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}