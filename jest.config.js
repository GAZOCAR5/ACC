module.exports = {
    collectCoverage: true, // Enable coverage collection
    coverageDirectory: 'coverage', // Output directory for coverage reports
    coverageReporters: ['json', 'lcov', 'text', 'clover'], // Formats of coverage reports
    collectCoverageFrom: [
      'src/**/*.{js,jsx}', // Collect coverage from all JS and JSX files in the src directory
      '!src/index.js', // Exclude specific files (e.g., entry point files)
      '!src/**/*.test.js' // Exclude test files
    ],
    coverageThreshold: { // Enforce coverage thresholds
      global: {
        branches: 80, // Minimum branch coverage
        functions: 80, // Minimum function coverage
        lines: 80, // Minimum line coverage
        statements: 80, // Minimum statement coverage
      },
    },
    transform: {
      '^.+\\.js$': 'babel-jest', // Use babel-jest to transform JS files if using Babel
    },
    testEnvironment: 'node', // Set the test environment (adjust if needed, e.g., 'jsdom' for browser environment)
  };
  