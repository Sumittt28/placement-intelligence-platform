"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { companyAPI } from "@/lib/api";
import { toast } from "sonner";
import { Plus } from "lucide-react";

export default function AdminCompaniesPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [website, setWebsite] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["admin-companies"],
    queryFn: async () => {
      const res = await companyAPI.list();
      return (res.data.data || []) as { id: string; name: string; industry?: string; website?: string; is_active: boolean }[];
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: { name: string; industry?: string; website?: string }) => companyAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-companies"] });
      toast.success("Company created!");
      setShowForm(false);
      setName("");
      setIndustry("");
      setWebsite("");
    },
    onError: () => toast.error("Failed to create company"),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Manage Companies</h2>
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="h-4 w-4 mr-2" /> Add Company
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader><CardTitle>New Company</CardTitle></CardHeader>
          <CardContent>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                createMutation.mutate({ name, industry: industry || undefined, website: website || undefined });
              }}
              className="space-y-4"
            >
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Company Name *</Label>
                  <Input value={name} onChange={(e) => setName(e.target.value)} required />
                </div>
                <div className="space-y-2">
                  <Label>Industry</Label>
                  <Input value={industry} onChange={(e) => setIndustry(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Website</Label>
                  <Input value={website} onChange={(e) => setWebsite(e.target.value)} />
                </div>
              </div>
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create Company"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <p className="text-muted-foreground">Loading companies...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(data || []).map((company) => (
            <Card key={company.id}>
              <CardContent className="pt-6">
                <h3 className="font-semibold text-lg">{company.name}</h3>
                {company.industry && <p className="text-sm text-muted-foreground mt-1">{company.industry}</p>}
                {company.website && (
                  <a href={company.website} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
                    {company.website}
                  </a>
                )}
                <div className="mt-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${company.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {company.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
