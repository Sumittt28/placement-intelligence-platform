"use client";

import { ExperienceForm } from "@/components/experiences/ExperienceForm";

export default function NewExperiencePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Submit Interview Experience</h1>
        <p className="text-muted-foreground">
          Share your interview experience to help others prepare. Your contribution improves the platform for everyone.
        </p>
      </div>
      <ExperienceForm />
    </div>
  );
}
