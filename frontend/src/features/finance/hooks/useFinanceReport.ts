import { useQuery } from "@tanstack/react-query";

import apiClient from "@/api/client";
import { IResponseEnvelope } from "@/types/api";

export interface IPeriodSummary {
  period: string;
  total_income: number;
  total_expense: number;
  balance: number;
}

export interface IReport {
  year: number;
  period_type: string;
  items: IPeriodSummary[];
}

export function useFinanceReport(year: number, period: "monthly" | "quarterly" = "monthly") {
  return useQuery({
    queryKey: ["finance", "report", year, period],
    queryFn: async () => {
      const { data } = await apiClient.get<IResponseEnvelope<IReport>>("/finance/report", {
        params: { year, period },
      });
      return data.data;
    },
  });
}
