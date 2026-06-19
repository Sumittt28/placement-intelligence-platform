"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { companyAPI } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Building2, Search } from "lucide-react";
import type { Company } from "@/types";

export default function CompaniesPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["companies", search],
    queryFn: async () => { const res = await companyAPI.list(search || undefined); return res.data.data as Company[]; },
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Company Intelligence</h2>
        <p className="text-muted-foreground">Explore interview patterns and insights for each company</p>
      </div>
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Search companies..." className="pl-10" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>
      {isLoading ? <p>Loading...</p> : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(data || []).map((company) => (
            <Link key={company.id} href={`/companies/${company.id}`}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Building2 className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{company.name}</h3>
                      {company.industry && <p className="text-xs text-muted-foreground">{company.industry}</p>}
                    </div>
                  </div>
                  {company.description && <p className="text-sm text-muted-foreground line-clamp-2">{company.description}</p>}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
