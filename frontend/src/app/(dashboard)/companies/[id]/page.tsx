"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { companyAPI } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import type { CompanyIntelligence } from "@/types";

const COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#6366f1"];

export default function CompanyPage() {
  const { id } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["company", id],
    queryFn: async () => { const res = await companyAPI.get(id as string); return res.data.data as CompanyIntelligence; },
  });

  if (isLoading) return <p>Loading...</p>;
  if (!data) return <p>Company not found</p>;

  const { company, analytics, frequently_asked_questions, questions_by_round, recent_experiences } = data;
  const topicData = analytics.top_topics.map((t) => ({ name: t.topic, count: t.count }));
  const diffData = Object.entries(analytics.difficulty_dist).map(([k, v]) => ({ name: k, value: v }));
  const roundData = Object.entries(analytics.round_dist).map(([k, v]) => ({ name: k, value: v }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold">{company.name}</h2>
        <p className="text-muted-foreground">{company.industry || "Technology"} {company.website && `• ${company.website}`}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Experiences", value: analytics.total_experiences },
          { label: "Total Questions", value: analytics.total_questions },
          { label: "Success Rate", value: `${analytics.success_rate}%` },
          { label: "Round Types", value: Object.keys(analytics.round_dist).length },
        ].map((s) => (
          <Card key={s.label}>
            <CardContent className="pt-6 text-center">
              <p className="text-3xl font-bold">{s.value}</p>
              <p className="text-sm text-muted-foreground">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Topics */}
        <Card>
          <CardHeader><CardTitle>Most Asked Topics</CardTitle></CardHeader>
          <CardContent>
            {topicData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={topicData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="text-muted-foreground text-center py-8">No data yet</p>}
          </CardContent>
        </Card>

        {/* Difficulty Distribution */}
        <Card>
          <CardHeader><CardTitle>Difficulty & Round Distribution</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium mb-2">Difficulty</p>
                {diffData.map((d, i) => (
                  <div key={d.name} className="flex justify-between py-1">
                    <span className="text-sm">{d.name}</span>
                    <Badge variant="outline">{d.value}</Badge>
                  </div>
                ))}
              </div>
              <div>
                <p className="text-sm font-medium mb-2">Rounds</p>
                {roundData.map((r) => (
                  <div key={r.name} className="flex justify-between py-1">
                    <span className="text-sm">{r.name}</span>
                    <Badge variant="outline">{r.value}</Badge>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* FAQs */}
      <Card>
        <CardHeader><CardTitle>Frequently Asked Questions</CardTitle></CardHeader>
        <CardContent>
          {frequently_asked_questions.length > 0 ? (
            <div className="space-y-3">
              {frequently_asked_questions.map((faq, i) => (
                <div key={i} className="flex items-start justify-between py-2 border-b last:border-0">
                  <div>
                    <p className="text-sm font-medium">{faq.question}</p>
                    <Badge variant="outline" className="mt-1">{faq.topic}</Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">Asked {faq.frequency}x</span>
                </div>
              ))}
            </div>
          ) : <p className="text-muted-foreground">No questions recorded yet</p>}
        </CardContent>
      </Card>

      {/* Recent Experiences */}
      <Card>
        <CardHeader><CardTitle>Recent Experiences</CardTitle></CardHeader>
        <CardContent>
          {recent_experiences.length > 0 ? (
            <div className="space-y-2">
              {recent_experiences.map((exp) => (
                <div key={exp.id} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div className="flex gap-2">
                    <Badge variant="outline">{exp.round_type}</Badge>
                    <Badge variant="outline">{exp.difficulty}</Badge>
                    <span className="text-sm">{exp.role}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge>{exp.outcome}</Badge>
                    <span className="text-xs text-muted-foreground">{exp.interview_date}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : <p className="text-muted-foreground">No experiences yet</p>}
        </CardContent>
      </Card>
    </div>
  );
}
