import "@testing-library/jest-dom";
import { TextEncoder, TextDecoder } from "util";

// Polyfill TextEncoder/TextDecoder for environments where it's not defined (Node.js < 11 or some Jest configs)
if (typeof globalThis.TextEncoder === "undefined") {
  // use Node's util if available

  globalThis.TextEncoder =
    TextEncoder as unknown as typeof globalThis.TextEncoder;
  globalThis.TextDecoder =
    TextDecoder as unknown as typeof globalThis.TextDecoder;
}

// Provide a basic fetch mock to avoid accidental network calls in tests (tests can override with jest.fn())
if (typeof globalThis.fetch === "undefined") {
  // minimal Response shim
  if (typeof globalThis.Response === "undefined") {
    class SimpleResponse {
      body: string;
      constructor(body: string) {
        this.body = body;
      }
      async json() {
        try {
          return JSON.parse(this.body);
        } catch {
          return {};
        }
      }
      async text() {
        return this.body;
      }
      get ok() {
        return true;
      }
      get status() {
        return 200;
      }
    }
    (globalThis as { Response: new (body: string) => unknown }).Response =
      SimpleResponse;
  }
  globalThis.fetch = () => Promise.resolve(new globalThis.Response("{}"));
}

globalThis.__VITE_API_ENDPOINT__ = "http://localhost:8000";
globalThis.__VITE_GOOGLE_CLIENT_ID__ = "test-client-id";
