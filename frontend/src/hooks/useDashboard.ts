"use client";

import { useQuery } from "@tanstack/react-query";
import { dashboardAPI, weaknessAPI, recommendationAPI, readinessAPI } from "@/lib/api";
import type { DashboardData, Weakness, Recommendation, CompanyReadiness } from "@/types";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const res = await dashboardAPI.get();
      return res.data.data as DashboardData;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useWeaknesses() {
  return useQuery({
    queryKey: ["weaknesses"],
    queryFn: async () => {
      const res = await weaknessAPI.list();
      return res.data.data as Weakness[];
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useRecommendations() {
  return useQuery({
    queryKey: ["recommendations"],
    queryFn: async () => {
      const res = await recommendationAPI.list();
      return res.data.data as Recommendation[];
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useOverallReadiness() {
  return useQuery({
    queryKey: ["readiness"],
    queryFn: async () => {
      const res = await readinessAPI.overall();
      return res.data.data as {
        overall_readiness: number;
        companies: CompanyReadiness[];
      };
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCompanyReadiness(companyId: string) {
  return useQuery({
    queryKey: ["readiness", companyId],
    queryFn: async () => {
      const res = await readinessAPI.company(companyId);
      return res.data.data as CompanyReadiness;
    },
    enabled: !!companyId,
    staleTime: 5 * 60 * 1000,
  });
}
