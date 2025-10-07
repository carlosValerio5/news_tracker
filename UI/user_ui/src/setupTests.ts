import '@testing-library/jest-dom';

// Polyfill TextEncoder/TextDecoder for environments where it's not defined (Node.js < 11 or some Jest configs)
if (typeof (globalThis as any).TextEncoder === 'undefined') {
    // use Node's util if available
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const util = require('util');
    (globalThis as any).TextEncoder = util.TextEncoder;
    (globalThis as any).TextDecoder = util.TextDecoder;
}

// Provide a basic fetch mock to avoid accidental network calls in tests (tests can override with jest.fn())
if (typeof (globalThis as any).fetch === 'undefined') {
    // minimal Response shim
    if (typeof (globalThis as any).Response === 'undefined') {
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
        (globalThis as any).Response = SimpleResponse;
    }
    (globalThis as any).fetch = () => Promise.resolve(new (globalThis as any).Response('{}'));
}


;(globalThis as any).__VITE_API_ENDPOINT__ = 'http://localhost:8000';
;(globalThis as any).__VITE_GOOGLE_CLIENT_ID__ = 'test-client-id';