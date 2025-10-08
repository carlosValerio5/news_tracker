This project adds Jest + React Testing Library unit tests for the UI.

What's included

- jest.config.cjs: Jest configuration using ts-jest and jsdom.
- src/setupTests.ts: jest-dom setup.
- src/**tests**/: basic unit tests for NavBar, RegisterButton and LatestNewsSection.
- tsconfig.test.json: TypeScript configuration for tests (includes jest types).

Install and run tests (locally on your machine)

Make sure Node.js and npm are installed. From the `UI/user_ui` folder run:

```powershell
npm install
npm test
```

Notes

- The test setup installs dev dependencies: jest, ts-jest, @testing-library/react, @testing-library/jest-dom, @types/jest, identity-obj-proxy.
- I couldn't run npm in this environment so please run the install & tests locally. If you'd like, I can add a GitHub Actions workflow next to run tests on push/PR.
