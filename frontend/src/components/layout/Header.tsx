"use client";

import { usePathname } from "next/navigation";

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/profile": "Profile",
  "/experiences": "Interview Experiences",
  "/experiences/new": "Submit Experience",
  "/companies": "Company Intelligence",
  "/interviews": "Mock Interviews",
  "/interviews/new": "New Interview",
  "/resume": "Resume Intelligence",
  "/weaknesses": "Weakness Analysis",
  "/recommendations": "Recommendations",
  "/readiness": "Placement Readiness",
  "/search": "Knowledge Base",
};

export function Header() {
  const pathname = usePathname();
  const title = pageTitles[pathname] || "Placement Intelligence";

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center border-b bg-background/95 backdrop-blur px-6">
      <h1 className="text-xl font-semibold">{title}</h1>
    </header>
  );
}
