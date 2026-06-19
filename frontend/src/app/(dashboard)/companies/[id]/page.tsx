"use client";

import { useParams } from "next/navigation";
import { CompanyIntelligence } from "@/components/companies/CompanyIntelligence";
import { useCompanyIntelligence } from "@/hooks/useCompany";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function CompanyIntelligencePage() {
  const { id } = useParams();
  const { data, isLoading, error } = useCompanyIntelligence(id as string);

  return (
    <div className="space-y-6">
      <Link href="/companies">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="mr-1 h-4 w-4" /> Back to Companies
        </Button>
      </Link>

      {isLoading ? (
        <div className="flex justify-center py-20"><LoadingSpinner /></div>
      ) : error || !data ? (
        <div className="text-center py-20 text-muted-foreground">Company not found.</div>
      ) : (
        <CompanyIntelligence data={data} />
      )}
    </div>
  );
}
