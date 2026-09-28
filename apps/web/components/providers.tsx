"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { setAuthTokenResolver } from "@/lib/api/client";

function AuthInterceptor() {
  const { getToken } = useAuth();
  
  useEffect(() => {
    setAuthTokenResolver(async () => {
      try {
        return await getToken();
      } catch (e) {
        console.error("Failed to get Clerk token", e);
        return null;
      }
    });
  }, [getToken]);

  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // With SSR, we usually want to set some default staleTime
            // above 0 to avoid refetching immediately on the client
            staleTime: 60 * 1000,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthInterceptor />
      {children}
    </QueryClientProvider>
  );
}
