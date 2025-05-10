Code Standards and Conventions

Always utilize the latest JavaScript and TypeScript features in strict mode. Embrace modern practices and current design patterns.
Prefer semantic HTML elements (header, nav, main, section, article, footer) over generic divs. Ensure compliance with W3C standards and WCAG 2.1 AA guidelines.
For CSS, employ CSS Modules, styled-components, or TailwindCSS with responsive designs based on Flexbox/Grid. Avoid outdated approaches like floats for layout.
Use double quotes and tabs for indentation in JavaScript and TypeScript code.
Code Architecture and Organization

Structure code by features/domains rather than file types. For example:
features/auth/
    components/
    hooks/
    services/
    types.ts
    utils.ts
    index.ts
    
Separate concerns into logical layers (domain, application, infrastructure, presentation).
Favor React functional components with hooks over class components. Utilize the latest React 19+ features such as Actions and enhanced concurrent rendering.
For Node.js backends, apply layered or hexagonal architecture with clear separation between controllers, services, and repositories.

Patterns and Best Practices

Apply functional programming principles: immutability, pure functions, and avoiding uncontrolled side effects.
For frontend state management, choose the solution that matches the complexity: useState/useReducer for local state, Context API for simple shared state, Redux Toolkit for complex state, and React Query/SWR for server data.
Implement code splitting with React.lazy and dynamic imports to optimize performance.
Use custom hooks to extract and reuse common logic between components.
For backend APIs, consistently validate and sanitize user inputs with libraries like Zod, Yup, or Joi.

Testing and Quality

Write unit tests with Jest/Vitest for important functions and hooks. Use React Testing Library for component tests, focusing on user behavior simulation.
Implement integration tests for critical workflows and use Playwright/Cypress for end-to-end testing of important user journeys.
Maintain a test coverage of at least 80% for critical business logic.
Security
Apply OWASP Top 10 protections in all applications. Validate and sanitize all user inputs on both client and server sides.
For authentication, use JWT tokens with rotation and secure storage. Apply the principle of least privilege for authorizations.
Avoid exposing sensitive information in logs or error messages. Use secure practices for secret management (environment variables, secret managers).
Implement CSP and other security headers to prevent XSS and CSRF attacks.

Performance and Optimization

Optimize performance with techniques like memoization (useMemo, useCallback) when necessary, but avoid premature optimization.
Utilize dynamic imports and lazy loading to reduce the initial bundle size.
For backend applications, apply appropriate caching strategies (Redis, CDN) and optimize database queries with proper indexing.

DevOps and Deployment

Containerize applications with Docker using lightweight and optimized images (Alpine, Debian-slim). Run containers with non-root users.
Automate deployments via CI/CD pipelines (GitHub Actions, GitLab CI) with automated quality checks.
Use Infrastructure as Code (Terraform, Ansible) to define and maintain deployment environments.

Coding Style and Documentation

Comment on the "why" rather than the "how" and use JSDoc/TSDoc to document interfaces, types, and complex functions.
Structure commits according to the Conventional Commits convention (feat, fix, chore, docs, refactor).
Maintain clear and up-to-date README files for each important module, documenting its purpose, usage, and dependencies.