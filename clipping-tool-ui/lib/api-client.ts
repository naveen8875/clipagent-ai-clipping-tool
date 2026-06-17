/**
 * API Client utility for making authenticated requests
 * Uses user's API key from profile context
 */

// This will be set by the components that use this client
let userApiKey: string | null = null;

export function setUserApiKey(apiKey: string) {
  userApiKey = apiKey;
}

export interface ApiResponse<T = unknown> {
  data?: T;
  error?: string;
  status: number;
}

/**
 * Makes an authenticated API request with the static API key
 * @param url - The API endpoint URL
 * @param options - Additional fetch options
 * @returns Promise with the response data
 */
export async function authenticatedFetch<T = unknown>(
  url: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  if (!userApiKey) {
    return {
      error: "API key not available",
      status: 401,
    };
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "X-API-Key": userApiKey,
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        error: data.message || data.error || "Request failed",
        status: response.status,
      };
    }

    return {
      data,
      status: response.status,
    };
  } catch (error) {
    console.error("API request failed:", error);
    return {
      error: error instanceof Error ? error.message : "Network error",
      status: 0,
    };
  }
}

/**
 * Fetches an image with authentication and returns a blob URL
 * @param imageUrl - The image URL to fetch
 * @returns Promise with the blob URL or null if failed
 */
export async function fetchAuthenticatedImage(
  imageUrl: string
): Promise<string | null> {
  if (!userApiKey) {
    console.error("API key not available for image fetch");
    return null;
  }

  try {
    const response = await fetch(imageUrl, {
      headers: {
        "X-API-Key": userApiKey,
      },
    });

    if (!response.ok) {
      console.error(
        "Failed to fetch image:",
        response.status,
        response.statusText
      );
      return null;
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
  } catch (error) {
    console.error("Error fetching authenticated image:", error);
    return null;
  }
}

/**
 * Makes a GET request with authentication
 * @param url - The API endpoint URL
 * @returns Promise with the response data
 */
export async function apiGet<T = unknown>(
  url: string
): Promise<ApiResponse<T>> {
  return authenticatedFetch<T>(url, { method: "GET" });
}

/**
 * Makes a POST request with authentication
 * @param url - The API endpoint URL
 * @param body - The request body
 * @returns Promise with the response data
 */
export async function apiPost<T = unknown>(
  url: string,
  body: unknown
): Promise<ApiResponse<T>> {
  return authenticatedFetch<T>(url, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Makes a PUT request with authentication
 * @param url - The API endpoint URL
 * @param body - The request body
 * @returns Promise with the response data
 */
export async function apiPut<T = unknown>(
  url: string,
  body: unknown
): Promise<ApiResponse<T>> {
  return authenticatedFetch<T>(url, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

/**
 * Makes a DELETE request with authentication
 * @param url - The API endpoint URL
 * @returns Promise with the response data
 */
export async function apiDelete<T = unknown>(
  url: string
): Promise<ApiResponse<T>> {
  return authenticatedFetch<T>(url, { method: "DELETE" });
}
