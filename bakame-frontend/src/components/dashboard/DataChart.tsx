import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, TrendingUp, Activity } from "lucide-react";

interface DataChartProps {
  title?: string;
  type?: "bar" | "line";
}

export function DataChart({ title = "Student Progress", type = "bar" }: DataChartProps) {
  const chartData = type === "bar" ? [
    { label: "English Lessons", value: 247, color: "stat-blue" },
    { label: "Math Sessions", value: 189, color: "stat-green" },
    { label: "Debate Practice", value: 156, color: "stat-purple" },
    { label: "Comprehension", value: 203, color: "stat-orange" }
  ] : [
    { label: "Speaking Confidence", value: "94.2%", color: "stat-blue" },
    { label: "Lesson Completion", value: "87.5%", color: "stat-green" },
    { label: "Student Engagement", value: "91.8%", color: "stat-purple" }
  ];

  return (
    <Card className="animate-fade-in">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {type === "bar" ? <BarChart3 className="h-5 w-5 text-primary" /> : <Activity className="h-5 w-5 text-primary" />}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {chartData.map((item, index) => (
            <div key={index} className={`flex items-center justify-between p-4 bg-${item.color}/5 rounded-lg border border-${item.color}/20 animate-scale-in`} style={{ animationDelay: `${index * 0.1}s` }}>
              <div>
                <p className="text-sm font-medium text-foreground">{item.label}</p>
                <p className={`text-2xl font-bold text-${item.color}`}>{item.value}</p>
              </div>
              <TrendingUp className={`h-8 w-8 text-${item.color}`} />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
