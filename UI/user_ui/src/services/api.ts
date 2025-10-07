import { API_BASE } from '../env';


const RUNTIME_API_BASE = (typeof import.meta !== 'undefined' && (import.meta as any).env && (import.meta as any).env.VITE_API_ENDPOINT) || API_BASE || '';
export const apiClient = {
    get: (endpoint: string) => {
        const headers: HeadersInit = {}; 
        if (localStorage.getItem('auth_token')) {
            headers['Authorization'] = `Bearer ${localStorage.getItem('auth_token')}`;
        }
        return fetch(`${RUNTIME_API_BASE}${endpoint}`, {
            method: 'GET',
            headers: headers
        });
    },
    post: (endpoint: string, data: any) => fetch(`${RUNTIME_API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }),
    put: (endpoint: string, data: any) => fetch(`${RUNTIME_API_BASE}${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }),
    delete: (endpoint: string) => fetch(`${RUNTIME_API_BASE}${endpoint}`, {
        method: 'DELETE'
    })
}