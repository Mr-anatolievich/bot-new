# GitHub Copilot Instructions — Arbitrage Bot (FastAPI + React Migration)

## ⚙️ Code Standards and Conventions

* Use **modern TypeScript and JavaScript (strict mode)** in all frontend code.
* **React 19+ with functional components and hooks** is the default. Prefer modern APIs like `useEffect`, `useState`, `useReducer`, and `useContext`.
* Use **semantic HTML** (`header`, `main`, `section`, etc.) for accessibility and structure.
* For styling, use **TailwindCSS** with mobile-first, responsive layouts using Flexbox/Grid. Avoid outdated layout models (e.g., floats).
* Use **double quotes** and **tabs** for indentation.

## 🧱 Code Architecture and Organization

* Organize frontend code by **features/domains**, e.g.:

  ```
  features/arbitrage/
    components/
    hooks/
    services/
    types.ts
    utils.ts
    index.ts
  ```

* Backend (FastAPI) should follow **layered or hexagonal architecture**:

  ```
  app/
    api/           # route definitions
    models/        # Pydantic and DB models
    services/      # business logic
    repositories/  # DB interactions
    core/          # config, security
    utils/         # helpers
  ```

## 🧩 Patterns and Best Practices

* Use **functional programming principles** where appropriate: immutability, pure functions, avoid side effects.
* Frontend state management:

  * `useState`/`useReducer` for local state
  * `Context API` for simple shared state
  * `Redux Toolkit` for complex state
  * `React Query` or `SWR` for server state
* Use **React.lazy** and **dynamic imports** for code splitting.
* Create **custom hooks** for reusable logic.
* Backend: use `Pydantic` for request/response validation and sanitize all user inputs.

## ✅ Testing and Quality

* **Jest** or **Vitest** for unit testing functions/hooks.
* **React Testing Library** for UI/component behavior.
* Use **Playwright** or **Cypress** for end-to-end testing.
* Target **80%+ test coverage** for critical logic.

## 🔐 Security

* Apply **OWASP Top 10** protections.
* Sanitize and validate all inputs client-side and server-side.
* Use **JWT tokens** with secure storage and rotation.
* Use `.env` and secret managers to store sensitive credentials.
* Enable **CSP**, **HSTS**, and other secure headers.

## 🚀 Performance and Optimization

* Optimize rendering with `useMemo` and `useCallback` where necessary.
* Use **lazy loading**, **dynamic imports**, and **bundle splitting**.
* Apply caching (e.g., **Redis**) on backend and use **indexed queries** in DB.

## ⚙️ DevOps and Deployment

* **Containerize** with Docker using Alpine or Debian-slim.
* Run containers as **non-root users**.
* Automate tests and builds via **GitHub Actions**.
* Define infrastructure with **Terraform** or **Ansible**.

## ✍️ Coding Style and Documentation

* Comment code to explain **why**, not just how.
* Use `JSDoc`/`TSDoc` in frontend and Python docstrings in backend.
* Use **Conventional Commits** (`feat`, `fix`, `chore`, `docs`, `refactor`).
* Maintain up-to-date `README.md` files per feature/module.
