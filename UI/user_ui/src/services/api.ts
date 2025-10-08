import { API_BASE } from "../env";

const RUNTIME_API_BASE = API_BASE;
export const apiClient = {
  get: (endpoint: string) => {
    const headers: HeadersInit = {};
    if (localStorage.getItem("auth_token")) {
      headers["Authorization"] = `Bearer ${localStorage.getItem("auth_token")}`;
    }
    return fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "GET",
      headers: headers,
    });
  },
  post: <TReq>(endpoint: string, data: TReq) =>
    fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }),
  put: <TReq>(endpoint: string, data: TReq) =>
    fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  delete: (endpoint: string) =>
    fetch(`${RUNTIME_API_BASE}${endpoint}`, {
      method: "DELETE",
    }),
};
