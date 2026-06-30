"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { userAPI } from "@/lib/api";
import { toast } from "sonner";

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => {
      const res = await userAPI.getMe();
      return res.data.data as {
        email: string;
        auth_provider: string;
        created_at: string;
        profile: {
          full_name: string;
          kalvium_id: string;
          batch: string;
          graduation_year: number;
          linkedin_url: string;
          github_url: string;
        } | null;
      };
    },
  });

  const { register, handleSubmit, reset } = useForm();

  const mutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => {
      // Coerce graduation_year to number
      if (data.graduation_year !== undefined && data.graduation_year !== "") {
        const num = Number(data.graduation_year);
        data.graduation_year = isNaN(num) ? undefined : num;
      } else {
        delete data.graduation_year;
      }
      return userAPI.updateProfile(data);
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["profile"] }); toast.success("Profile updated!"); },
    onError: () => toast.error("Update failed"),
  });

  if (isLoading) return <p>Loading...</p>;
  const profile = data?.profile;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-2xl font-bold">Profile</h2>

      <Card>
        <CardHeader><CardTitle>Personal Information</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Full Name</Label>
                <Input defaultValue={profile?.full_name || ""} {...register("full_name")} />
              </div>
              <div className="space-y-2">
                <Label>Kalvium ID</Label>
                <Input defaultValue={profile?.kalvium_id || ""} {...register("kalvium_id")} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Batch</Label>
                <Input defaultValue={profile?.batch || ""} {...register("batch")} />
              </div>
              <div className="space-y-2">
                <Label>Graduation Year</Label>
                <Input type="number" defaultValue={profile?.graduation_year || ""} {...register("graduation_year")} />
              </div>
            </div>
            <div className="space-y-2">
              <Label>LinkedIn URL</Label>
              <Input defaultValue={profile?.linkedin_url || ""} {...register("linkedin_url")} />
            </div>
            <div className="space-y-2">
              <Label>GitHub URL</Label>
              <Input defaultValue={profile?.github_url || ""} {...register("github_url")} />
            </div>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Account Info</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm"><span className="font-medium">Email:</span> {data?.email}</p>
          <p className="text-sm"><span className="font-medium">Auth Provider:</span> {data?.auth_provider}</p>
          <p className="text-sm"><span className="font-medium">Member Since:</span> {data?.created_at ? new Date(data.created_at).toLocaleDateString() : "N/A"}</p>
        </CardContent>
      </Card>
    </div>
  );
}
