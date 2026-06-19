"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, ArrowRight, MessageSquare } from "lucide-react";
import type { Company } from "@/types";

interface CompanyCardProps {
  company: Company;
  experienceCount?: number;
}

export function CompanyCard({ company, experienceCount }: CompanyCardProps) {
  return (
    <Link href={`/companies/${company.id}`}>
      <Card className="hover:border-primary/50 transition-colors cursor-pointer h-full">
        <CardContent className="pt-6">
          <div className="flex items-start justify-between">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                {company.logo_url ? (
                  <img src={company.logo_url} alt={company.name} className="h-8 w-8 rounded" />
                ) : (
                  <div className="flex h-8 w-8 items-center justify-center rounded bg-primary/10">
                    <Building2 className="h-4 w-4 text-primary" />
                  </div>
                )}
                <h3 className="font-semibold">{company.name}</h3>
              </div>
              {company.industry && (
                <Badge variant="outline" className="text-xs">{company.industry}</Badge>
              )}
            </div>
            <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
          </div>

          {company.description && (
            <p className="mt-3 text-sm text-muted-foreground line-clamp-2">{company.description}</p>
          )}

          {experienceCount !== undefined && (
            <div className="mt-3 flex items-center gap-1 text-xs text-muted-foreground">
              <MessageSquare className="h-3 w-3" />
              {experienceCount} experience(s)
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
