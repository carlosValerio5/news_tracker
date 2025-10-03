const getApiBase = () => {
    if (import.meta.env.DEV) {
        return '/api';
    }
    return import.meta.env.VITE_API_ENDPOINT;
}

export const API_BASE = getApiBase();

export const apiClient = {
    get: (endpoint: string) => {
        const headers: HeadersInit = {}; 
        if (localStorage.getItem('auth_token')) {
            headers['Authorization'] = `Bearer ${localStorage.getItem('auth_token')}`;
        }
        return fetch(`${API_BASE}${endpoint}`, {
            method: 'GET',
            headers: headers
        });
    },
    post: (endpoint: string, data: any) => fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }),
    put: (endpoint: string, data: any) => fetch(`${API_BASE}${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }),
    delete: (endpoint: string) => fetch(`${API_BASE}${endpoint}`, {
        method: 'DELETE'
    })
}