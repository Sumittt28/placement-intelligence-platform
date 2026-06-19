"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { companyAPI, searchAPI } from "@/lib/api";
import type { Company, CompanyIntelligence, SearchResult } from "@/types";

export function useCompanyList(search?: string) {
  return useQuery({
    queryKey: ["companies", search],
    queryFn: async () => {
      const res = await companyAPI.list(search);
      return res.data.data as Company[];
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCompanyIntelligence(id: string) {
  return useQuery({
    queryKey: ["companies", id],
    queryFn: async () => {
      const res = await companyAPI.get(id);
      return res.data.data as CompanyIntelligence;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; industry?: string; website?: string }) =>
      companyAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["companies"] });
    },
  });
}

export function useKnowledgeBaseSearch(params: {
  q: string;
  type?: string;
  company?: string;
  round_type?: string;
  difficulty?: string;
  page?: number;
}) {
  return useQuery({
    queryKey: ["search", params],
    queryFn: async () => {
      const res = await searchAPI.search(params);
      return res.data.data as SearchResult[];
    },
    enabled: !!params.q && params.q.length >= 2,
    staleTime: 60 * 1000,
  });
}
