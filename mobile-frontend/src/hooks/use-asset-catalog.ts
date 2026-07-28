"use client";

import { useCallback, useEffect, useState } from "react";
import { useApi } from "@/lib/api";
import type { Asset } from "@/lib/types";

export function useAssetCatalog() {
  const { get } = useApi();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await get<Asset[]>("/market/assets/", { limit: 200 });
      setAssets(data);
    } catch {
      setError("Unable to load the asset catalog.");
    } finally {
      setIsLoading(false);
    }
  }, [get]);

  useEffect(() => {
    load();
  }, [load]);

  const byId = new Map(assets.map((asset) => [asset.id, asset]));
  const bySymbol = new Map(assets.map((asset) => [asset.symbol, asset]));

  return { assets, byId, bySymbol, isLoading, error, reload: load };
}
