import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "./supabase";

// ── Types ────────────────────────────────────────────────────────────────────

export interface Ward {
  id: string;
  ward_name: string;
  total_beds: number;
  occupied_beds: number;
  hospital_id?: string | null;
}

export interface NewWardInput {
  ward_name: string;
  total_beds: number;
  occupied_beds: number;
  hospital_id?: string | null;
}

export interface Hospital {
  id: string;
  name: string;
  code: string;
  city: string;
  lat: number;
  lng: number;
  beds_capacity: number;
  icu_beds: number;
  status: string;
  occupancy: number; // Inferred or joined from beds
  stock: number;     // Inferred or joined from inventory
  waitTime: number;  // Inferred from emergency
  risk: number;      // Calculated by AI engine
  level: "critical" | "high" | "moderate" | "low";
  phone: string;
}

export interface Recommendation {
  id: string;
  hospital_id: string;
  hospitalName: string;
  category: "RISK" | "FORECASTING" | "OPTIMIZATION" | "SURVEILLANCE";
  title: string;
  description: string;
  action_items: string[];
  confidence: number;
  risk_level: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  created_at: string;
  explanation?: {
    model_name: string;
    confidence: number;
    summary_text: string;
    features: Array<{ feature_name: string; shap_value: number; importance_rank: number; description: string }>;
  };
}

export interface NewHospitalInput {
  name: string;
  district: string;
  address: string;
  phone: string | null;
  email: string | null;
  latitude: number | null;
  longitude: number | null;
}

// ── Hooks ────────────────────────────────────────────────────────────────────

export function useHospitals() {
  return useQuery({
    queryKey: ["hospitals"],
    queryFn: async (): Promise<Hospital[]> => {
      try {
        const { data, error } = await supabase
          .from("hospitals")
          .select(`
            id, name, district,
            beds (total_beds, occupied_beds),
            inventory (stock_level, min_threshold),
            incidents (severity, status)
          `);
        if (error) throw error;

        const transformed = (data || []).map((h: any) => {
          const totalBeds = h.beds?.reduce((a: number, b: any) => a + b.total_beds, 0) || 0;
          const occupiedBeds = h.beds?.reduce((a: number, b: any) => a + b.occupied_beds, 0) || 0;
          const occupancy = totalBeds ? occupiedBeds / totalBeds : 0;

          const totalStock = h.inventory?.reduce((a: number, b: any) => a + b.stock_level, 0) || 0;
          const totalMin = h.inventory?.reduce((a: number, b: any) => a + b.min_threshold, 0) || 1;
          const stockRatio = totalStock / totalMin;
          const stockScore = stockRatio > 1.5 ? 0.9 : stockRatio > 1 ? 0.6 : 0.3;

          const activeIncidents = h.incidents?.filter((i: any) => i.status === "Active") || [];
          const hasCritical = activeIncidents.some((i: any) => i.severity === "critical");
          const hasHigh = activeIncidents.some((i: any) => i.severity === "high");

          let risk = (occupancy * 0.6) + ((1 - stockScore) * 0.4);
          let level = "low";
          if (hasCritical || risk > 0.8) {
            level = "critical";
            risk = Math.max(risk, 0.9);
          } else if (hasHigh || risk > 0.6) {
            level = "high";
            risk = Math.max(risk, 0.7);
          } else if (risk > 0.4) {
            level = "moderate";
          }

          return {
            id: h.id,
            name: h.name,
            code: h.id,
            city: h.district,
            lat: 0,
            lng: 0,
            beds_capacity: totalBeds,
            icu_beds: 0,
            status: "active",
            occupancy,
            stock: stockScore,
            waitTime: level === "critical" ? 85 : level === "high" ? 45 : 15,
            risk,
            level,
            phone: "+91 12345 67890",
            beds: totalBeds,
            icu: 0
          } as any;
        });

        return transformed;
      } catch (e) {
        console.error("Failed to fetch hospitals data:", e);
        throw e;
      }
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useAddHospital() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (hospital: NewHospitalInput): Promise<Hospital> => {
      const { data, error } = await supabase
        .from("hospitals")
        .insert(hospital)
        .select()
        .single();
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hospitals"] });
    },
  });
}

// ── Ward hooks ───────────────────────────────────────────────────────────────

export function useWards() {
  return useQuery({
    queryKey: ["wards"],
    queryFn: async (): Promise<Ward[]> => {
      try {
        const { data, error } = await supabase
          .from("beds")
          .select("id, ward_name, total_beds, occupied_beds, hospital_id")
          .order("ward_name", { ascending: true });
        if (error) throw error;
        return data || [];
      } catch (e) {
        console.error("Failed to fetch wards data:", e);
        throw e;
      }
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

export function useAddWard() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (ward: NewWardInput): Promise<Ward> => {
      const { data, error } = await supabase
        .from("beds")
        .insert(ward)
        .select()
        .single();
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wards"] });
      // Also invalidate hospitals since occupancy is derived from beds
      queryClient.invalidateQueries({ queryKey: ["hospitals"] });
    },
  });
}

export function useRecommendations() {
  return useQuery({
    queryKey: ["recommendations"],
    queryFn: async (): Promise<Recommendation[]> => {
      // Return empty since recommendations table does not exist in seed
      return [];
    },
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useApproveRecommendation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from('recommendations').update({ status: 'APPROVED' }).eq('id', id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });
}

export function useRejectRecommendation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason: string }) => {
      // Assuming there's a reason column in your recommendations table if you want to save it
      const { error } = await supabase.from('recommendations').update({ status: 'REJECTED' }).eq('id', id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });
}