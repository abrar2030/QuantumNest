"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Loader2, Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ApiError, useApi } from "@/lib/api";
import type { Portfolio, PortfolioCreateInput, RiskLevel } from "@/lib/types";

const riskLevels: { value: RiskLevel; label: string }[] = [
  { value: "very_low", label: "Very low" },
  { value: "low", label: "Low" },
  { value: "moderate", label: "Moderate" },
  { value: "high", label: "High" },
  { value: "very_high", label: "Very high" },
];

const schema = z.object({
  name: z.string().min(2, "Give your portfolio a name"),
  description: z.string().optional(),
  risk_level: z.enum([
    "very_low",
    "low",
    "moderate",
    "high",
    "very_high",
  ]) satisfies z.ZodType<RiskLevel>,
  investment_strategy: z.string().optional(),
  base_currency: z.string().min(3).max(3),
});

type FormValues = z.infer<typeof schema>;

export function CreatePortfolioDialog({
  onCreated,
}: {
  onCreated: (portfolio: Portfolio) => void;
}) {
  const { post } = useApi();
  const [open, setOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "",
      description: "",
      risk_level: "moderate",
      investment_strategy: "",
      base_currency: "USD",
    },
  });

  async function onSubmit(values: FormValues) {
    setIsSubmitting(true);
    try {
      const payload: PortfolioCreateInput = {
        name: values.name,
        description: values.description || undefined,
        risk_level: values.risk_level,
        investment_strategy: values.investment_strategy || undefined,
        base_currency: values.base_currency.toUpperCase(),
      };
      const created = await post<Portfolio>("/portfolio/", payload);
      toast.success(`"${created.name}" was created.`);
      onCreated(created);
      form.reset();
      setOpen(false);
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not create portfolio.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4" /> New portfolio
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create a portfolio</DialogTitle>
          <DialogDescription>
            Set up a new portfolio to start tracking holdings and performance.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Growth Portfolio" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description (optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Long-term growth across diversified equities"
                      rows={2}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-3">
              <FormField
                control={form.control}
                name="risk_level"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Risk level</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {riskLevels.map((level) => (
                          <SelectItem key={level.value} value={level.value}>
                            {level.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="base_currency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Base currency</FormLabel>
                    <FormControl>
                      <Input maxLength={3} placeholder="USD" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="investment_strategy"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Investment strategy (optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="Growth, value, income..." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                Create portfolio
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
