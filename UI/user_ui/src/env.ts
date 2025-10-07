// Test-friendly env wrapper. Do NOT use `import.meta` here so TypeScript/ts-jest
// can parse this file under CommonJS test settings.
// In Vite runtime, main.tsx will set the corresponding global variables if needed.
const g = globalThis as any;

export const API_BASE: string = (
  // prefer an explicit runtime global (set in tests or by main.tsx in production)
  g.__VITE_API_ENDPOINT__ ??
  // fallback to Node env in some server-side setups
  (typeof process !== 'undefined' && process.env && process.env.VITE_API_ENDPOINT) ??
  // final fallback
  'http://localhost:8000'
);

export const GOOGLE_CLIENT_ID: string | undefined = (
  g.__VITE_GOOGLE_CLIENT_ID__ ??
  (typeof process !== 'undefined' && process.env && process.env.VITE_GOOGLE_CLIENT_ID) ??
  undefined
);

export default { API_BASE, GOOGLE_CLIENT_ID };
