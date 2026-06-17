"use client";

import { useState, useCallback } from "react";
import { useToast } from "@/hooks/use-toast";

export interface ApiError {
  error: string;
  message?: string;
  code?: string;
  details?: any;
}

export interface UseApiErrorHandlerReturn {
  handleError: (error: unknown, context?: string) => void;
  clearError: () => void;
  error: ApiError | null;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export function useApiErrorHandler(): UseApiErrorHandlerReturn {
  const [error, setError] = useState<ApiError | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleError = useCallback(
    (error: unknown, context?: string) => {
      console.error(`API Error${context ? ` (${context})` : ""}:`, error);

      let apiError: ApiError;

      if (error && typeof error === "object" && "error" in error) {
        // Error from API response
        apiError = error as ApiError;
      } else if (error instanceof Error) {
        // JavaScript Error
        apiError = {
          error: error.message,
          message: error.message,
        };
      } else if (typeof error === "string") {
        // String error
        apiError = {
          error,
          message: error,
        };
      } else {
        // Unknown error
        apiError = {
          error: "An unknown error occurred",
          message: "Something went wrong. Please try again.",
        };
      }

      setError(apiError);

      // Show toast notification
      toast({
        title: "Error",
        description: apiError.message || apiError.error,
        variant: "destructive",
      });
    },
    [toast]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    handleError,
    clearError,
    error,
    isLoading,
    setIsLoading,
  };
}

// Hook for handling API calls with error handling
export function useApiCall<T>() {
  const { handleError, clearError, isLoading, setIsLoading } =
    useApiErrorHandler();

  const execute = useCallback(
    async (apiCall: () => Promise<T>, context?: string): Promise<T | null> => {
      try {
        setIsLoading(true);
        clearError();
        const result = await apiCall();
        return result;
      } catch (error) {
        handleError(error, context);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [handleError, clearError, setIsLoading]
  );

  return {
    execute,
    isLoading,
    clearError,
  };
}

// Utility function to handle fetch errors
export function handleFetchError(response: Response, context?: string): never {
  const errorMessage = `HTTP ${response.status}: ${response.statusText}`;
  const error = new Error(errorMessage);
  error.name = "FetchError";
  throw error;
}

// Utility function to check if response is ok and handle errors
export async function handleApiResponse<T>(
  response: Response,
  context?: string
): Promise<T> {
  if (!response.ok) {
    try {
      const errorData = await response.json();
      const error = new Error(
        errorData.message || errorData.error || `HTTP ${response.status}`
      );
      error.name = "ApiResponseError";
      throw error;
    } catch {
      handleFetchError(response, context);
    }
  }

  return response.json();
}
