import { API_BASE } from "../env";

export type ApiResponse<T> = {
  status: number;
  data: T | null;
  ok: boolean;
}

const RUNTIME_API_BASE = API_BASE;

export const apiClient = {
  get: async<T = unknown>(endpoint: string, init?: RequestInit) : Promise<ApiResponse<T>> => {
    const headers: HeadersInit = {};
    if (localStorage.getItem("auth_token")) {
      headers["Authorization"] = `Bearer ${localStorage.getItem("auth_token")}`;
    }

    const mergedHeaders = {
      ...headers,
      ...init?.headers,
    }
    const res = await fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "GET",
      ...init,
      headers: mergedHeaders,
    });
    if (res.status === 204) return {data: null, status: res.status, ok: res.ok}
    try {
      const json = await res.json();
      return {data: json as T, status: res.status, ok: res.ok};
    } catch (error) {
      console.error("Error parsing JSON:", error);
      return {data: null, status: res.status, ok: false};
    }
  },

  post: async <TReq>(endpoint: string, data: TReq) => {
    const headers: HeadersInit = {};
    if (localStorage.getItem("auth_token")) {
      headers["Authorization"] = `Bearer ${localStorage.getItem("auth_token")}`;
    }
    headers["Content-Type"] = "application/json";

    const response = await fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(data),
    });

    return response;
  },
  put: async <TReq>(endpoint: string, data: TReq) => {
    const headers: HeadersInit = {};
    if (localStorage.getItem("auth_token")) {
      headers["Authorization"] = `Bearer ${localStorage.getItem("auth_token")}`;
    }
    headers["Content-Type"] = "application/json";

    const response = await fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "PUT",
      headers: headers,
      body: JSON.stringify(data),
    });

    return response;
  },
  delete: async (endpoint: string) => {
    const headers: HeadersInit = {};
    if (localStorage.getItem("auth_token")) {
      headers["Authorization"] = `Bearer ${localStorage.getItem("auth_token")}`;
    }

    const response = await fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "DELETE",
      headers: headers,
    });

    return response;
  },
};
