export {};

declare global {
  var __VITE_API_ENDPOINT__: string | undefined;
  var __VITE_GOOGLE_CLIENT_ID__: string | undefined;
  var TextEncoder: typeof import("util").TextEncoder;
  var TextDecoder: typeof import("util").TextDecoder;
}
