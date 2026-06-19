import Link from "next/link";
import { Brain, BarChart3, MessageSquare, Target, BookOpen, Search } from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  { icon: MessageSquare, title: "Interview Experiences", desc: "Collect and learn from real interview experiences submitted by students." },
  { icon: Brain, title: "AI Mock Interviews", desc: "Resume-aware, company-specific mock interviews with adaptive follow-ups." },
  { icon: BarChart3, title: "Company Intelligence", desc: "Know what companies ask, their patterns, difficulty trends, and success rates." },
  { icon: Target, title: "Placement Readiness", desc: "Explainable readiness scores for each target company." },
  { icon: BookOpen, title: "Personalized Learning", desc: "AI-generated study plans based on your weaknesses and target companies." },
  { icon: Search, title: "Knowledge Base", desc: "Search across all interview questions by company, topic, or technology." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      {/* Hero */}
      <div className="container mx-auto px-6 pt-20 pb-16 text-center">
        <div className="flex justify-center mb-6">
          <div className="flex items-center gap-3 rounded-full bg-primary/10 px-4 py-2 text-primary text-sm font-medium">
            <Brain className="h-5 w-5" />
            Placement Intelligence Platform
          </div>
        </div>
        <h1 className="text-5xl font-bold tracking-tight mb-6">
          Become <span className="text-primary">Interview Ready</span>
          <br />with Real Intelligence
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
          A continuously learning ecosystem that becomes smarter after every interview.
          Real experiences. Company intelligence. Personalized AI coaching.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/register">
            <Button size="lg" className="text-base px-8">Get Started</Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline" className="text-base px-8">Sign In</Button>
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Everything You Need to Crack Placements</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f) => (
            <div key={f.title} className="rounded-xl border bg-card p-6 hover:shadow-lg transition-shadow">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 mb-4">
                <f.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
              <p className="text-muted-foreground text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="container mx-auto px-6 py-16 text-center">
        <div className="rounded-2xl bg-primary p-12 text-primary-foreground">
          <h2 className="text-3xl font-bold mb-4">Every Interview Makes Us Smarter</h2>
          <p className="text-lg mb-8 opacity-90">Join the platform that learns from every student&apos;s experience.</p>
          <Link href="/register">
            <Button size="lg" variant="secondary" className="text-base px-8">Start Now - It&apos;s Free</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
