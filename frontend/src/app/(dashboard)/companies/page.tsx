"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { CompanyCard } from "@/components/companies/CompanyCard";
import { useCompanyList } from "@/hooks/useCompany";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { Building2, Search } from "lucide-react";

export default function CompaniesPage() {
  const [search, setSearch] = useState("");
  const { data: companies, isLoading } = useCompanyList(search || undefined);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Company Intelligence</h1>
        <p className="text-muted-foreground">Explore company-specific interview insights</p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search companies..."
          className="pl-10"
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20"><LoadingSpinner /></div>
      ) : !companies || companies.length === 0 ? (
        <EmptyState
          icon={<Building2 className="h-12 w-12" />}
          title="No companies found"
          description={search ? `No companies matching "${search}"` : "Companies will appear as experiences are submitted."}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {companies.map((company) => (
            <CompanyCard key={company.id} company={company} />
          ))}
        </div>
      )}
    </div>
  );
}
