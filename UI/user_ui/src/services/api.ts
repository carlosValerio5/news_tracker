import { API_BASE } from "../env";

const RUNTIME_API_BASE = API_BASE;
export const apiClient = {
  get: (endpoint: string, init?: RequestInit) : Promise<Response> => {
    const headers: HeadersInit = {};
    if (localStorage.getItem("auth_token")) {
      headers["Authorization"] = `Bearer ${localStorage.getItem("auth_token")}`;
    }

    const mergedHeaders = {
      ...headers,
      ...init?.headers,
    }
    return fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "GET",
      ...init,
      headers: mergedHeaders,
    });
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
