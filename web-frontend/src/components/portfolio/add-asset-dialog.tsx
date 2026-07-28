"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Check, ChevronsUpDown, Loader2, Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
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
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ApiError, useApi } from "@/lib/api";
import { cn, formatCurrency } from "@/lib/utils";
import type {
  Asset,
  PortfolioAsset,
  PortfolioAssetCreateInput,
} from "@/lib/types";

const schema = z.object({
  assetId: z.number({ invalid_type_error: "Choose an asset" }).int().positive(),
  quantity: z.coerce.number().positive("Quantity must be greater than 0"),
  purchasePrice: z.coerce.number().nonnegative("Enter a purchase price"),
  targetWeight: z.coerce.number().min(0).max(100).optional(),
});

type FormValues = z.infer<typeof schema>;

export function AddAssetDialog({
  portfolioId,
  assets,
  isLoadingAssets,
  onAdded,
}: {
  portfolioId: number;
  assets: Asset[];
  isLoadingAssets: boolean;
  onAdded: (holding: PortfolioAsset) => void;
}) {
  const { post } = useApi();
  const [open, setOpen] = useState(false);
  const [comboOpen, setComboOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      assetId: undefined,
      quantity: undefined,
      purchasePrice: undefined,
      targetWeight: undefined,
    },
  });

  const selectedAssetId = form.watch("assetId");
  const selectedAsset = assets.find((a) => a.id === selectedAssetId);

  async function onSubmit(values: FormValues) {
    setIsSubmitting(true);
    try {
      const payload: PortfolioAssetCreateInput = {
        portfolio_id: portfolioId,
        asset_id: values.assetId,
        quantity: values.quantity,
        purchase_price: values.purchasePrice,
        target_weight: values.targetWeight,
      };
      const holding = await post<PortfolioAsset>("/portfolio/assets/", payload);
      toast.success("Asset added to portfolio.");
      onAdded(holding);
      form.reset();
      setOpen(false);
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not add this asset.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="h-4 w-4" /> Add asset
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add a holding</DialogTitle>
          <DialogDescription>
            Search the asset catalog and record your position.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="assetId"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Asset</FormLabel>
                  <Popover open={comboOpen} onOpenChange={setComboOpen}>
                    <PopoverTrigger asChild>
                      <FormControl>
                        <Button
                          variant="outline"
                          role="combobox"
                          className="justify-between font-normal"
                          disabled={isLoadingAssets}
                        >
                          {selectedAsset
                            ? `${selectedAsset.symbol} · ${selectedAsset.name}`
                            : isLoadingAssets
                              ? "Loading assets..."
                              : "Select an asset"}
                          <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
                        </Button>
                      </FormControl>
                    </PopoverTrigger>
                    <PopoverContent className="w-[360px] p-0">
                      <Command>
                        <CommandInput placeholder="Search symbol or name..." />
                        <CommandList>
                          <CommandEmpty>No assets found.</CommandEmpty>
                          <CommandGroup>
                            {assets.map((asset) => (
                              <CommandItem
                                key={asset.id}
                                value={`${asset.symbol} ${asset.name}`}
                                onSelect={() => {
                                  field.onChange(asset.id);
                                  setComboOpen(false);
                                }}
                              >
                                <Check
                                  className={cn(
                                    "mr-2 h-4 w-4",
                                    asset.id === field.value
                                      ? "opacity-100"
                                      : "opacity-0",
                                  )}
                                />
                                <span className="font-medium">
                                  {asset.symbol}
                                </span>
                                <span className="ml-2 truncate text-muted-foreground">
                                  {asset.name}
                                </span>
                                {asset.current_price != null && (
                                  <span className="ml-auto shrink-0 text-xs text-muted-foreground">
                                    {formatCurrency(asset.current_price)}
                                  </span>
                                )}
                              </CommandItem>
                            ))}
                          </CommandGroup>
                        </CommandList>
                      </Command>
                    </PopoverContent>
                  </Popover>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid grid-cols-2 gap-3">
              <FormField
                control={form.control}
                name="quantity"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Quantity</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="any"
                        placeholder="10"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="purchasePrice"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Purchase price</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="any"
                        placeholder="150.00"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="targetWeight"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Target allocation % (optional)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="any"
                      placeholder="15"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                Add holding
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
