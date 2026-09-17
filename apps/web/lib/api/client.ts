export class ApiError extends Error {
  status: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  constructor(message: string, status: number, data?: any) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

export async function fetchApi<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { params, ...customOptions } = options;
  
  const headers = new Headers(customOptions.headers);
  if (!headers.has('Content-Type') && customOptions.body && typeof customOptions.body === 'string') {
    headers.set('Content-Type', 'application/json');
  }

  // Construct URL, ensuring endpoint is formatted correctly
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Use relative URL on the client to hit the Next.js proxy and avoid CORS.
  // Use absolute URL on the server since relative fetch is not supported in Node without a base URL.
  const isServer = typeof window === 'undefined';
  const baseUrl = isServer ? API_BASE_URL : '';
  const url = baseUrl ? new URL(path, baseUrl) : new URL(path, window.location.origin);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, value);
      }
    });
  }

  const response = await fetch(url.toString(), {
    ...customOptions,
    headers,
  });

  if (!response.ok) {
    let errorMessage = response.statusText;
    let errorData = null;

    const text = await response.text();
    
    if (text) {
      try {
        const data = JSON.parse(text);
        errorData = data;
        if (data && typeof data.detail === 'string') {
          errorMessage = data.detail;
        } else if (data && data.detail) {
          errorMessage = JSON.stringify(data.detail);
        } else if (data && data.message) {
          errorMessage = data.message;
        }
      } catch {
        errorMessage = text;
      }
    }

    throw new ApiError(errorMessage, response.status, errorData);
  }

  if (response.status === 204) {
    return null as unknown as T;
  }

  const text = await response.text();
  if (!text) {
    return null as unknown as T;
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error('Failed to parse API response as JSON');
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: Omit<FetchOptions, 'method'>) => 
    fetchApi<T>(endpoint, { ...options, method: 'GET' }),
  
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  post: <T>(endpoint: string, data?: any, options?: Omit<FetchOptions, 'method' | 'body'>) => {
    let body;
    if (data !== undefined) {
      body = data instanceof FormData ? data : JSON.stringify(data);
    }
    return fetchApi<T>(endpoint, { 
      ...options, 
      method: 'POST', 
      body,
    });
  },
    
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  patch: <T>(endpoint: string, data?: any, options?: Omit<FetchOptions, 'method' | 'body'>) => 
    fetchApi<T>(endpoint, { 
      ...options, 
      method: 'PATCH', 
      body: data ? JSON.stringify(data) : undefined,
    }),
    
  delete: <T>(endpoint: string, options?: Omit<FetchOptions, 'method'>) => 
    fetchApi<T>(endpoint, { ...options, method: 'DELETE' }),
};
