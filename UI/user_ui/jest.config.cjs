module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  moduleNameMapper: {
    "\\.(css|less|sass|scss)$": "identity-obj-proxy",
    "\\.(jpg|jpeg|png|gif|svg|webp|ico|bmp|tiff)$": "jest-transform-stub",
    "\\.(ttf|eot|woff|woff2|otf)$": "jest-transform-stub", 
    "\\.(mp4|webm|wav|mp3|m4a|aac|oga)$": "jest-transform-stub",
    "^@/(.*)$": "<rootDir>/src/$1",
    "^/src/(.*)$": "<rootDir>/src/$1", 
  },
  setupFilesAfterEnv: ["<rootDir>/src/setupTests.ts"],
  transform: {
    "^.+\\.(ts|tsx)$": ["ts-jest", { tsconfig: "tsconfig.test.json" }],
  },
  globals: {},
  testPathIgnorePatterns: ["/node_modules/", "/dist/"],
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
};
