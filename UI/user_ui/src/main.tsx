import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { GoogleOAuthProvider } from '@react-oauth/google';
import { GOOGLE_CLIENT_ID as ENV_GOOGLE_CLIENT_ID } from './env';

// Prefer the Vite-provided value at runtime (import.meta.env) so the dev server
// and production builds get the real client id. Fall back to env wrapper (used in tests).
const RUNTIME_GOOGLE_CLIENT_ID = import.meta.env?.VITE_GOOGLE_CLIENT_ID || ENV_GOOGLE_CLIENT_ID || '';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={RUNTIME_GOOGLE_CLIENT_ID}>
      <App />
    </GoogleOAuthProvider>
  </StrictMode>,
)
