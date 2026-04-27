---
description: Common error handling traps — empty catches, wrong status codes, retry cascades, missing correlation IDs
globs: ["**/*.kt", "**/*.ts", "**/*.vue", "**/*.js", "**/*.groovy"]
alwaysApply: false
type: "auto"
---

# Error Handling — Gotchas

Quick reference for the most common traps. Full detail: `engineering-codex/facets/error-handling/gotchas.md`

- **Empty catch blocks** — Swallowed exceptions become production mysteries. At minimum log the error; better, handle explicitly or re-throw.
- **200 with error body** — `{"success": false}` on HTTP 200 breaks clients, proxies, and monitoring. Use 4xx/5xx with RFC 9457 error format.
- **Exposing stack traces** — Stack traces reveal internals to attackers. Log full detail server-side; return a generic message to the client.
- **Catching `Exception` instead of specific types** — Catches things you didn't mean to (e.g. `OutOfMemoryError`). Catch the narrowest type you can handle.
- **Unhandled async errors** — Promise rejections and unhandled async errors silently fail. Always `.catch()` or `try/await/catch`.
- **Retry without backoff** — Hammering a failing service makes recovery harder. Use exponential backoff with jitter; cap retries.
- **Error messages that help attackers** — "User not found" vs "Wrong password" enables username enumeration. Return a single generic message for auth failures.
- **Inconsistent error format** — Each endpoint returning a different shape forces consumers to write per-endpoint error handling. Standardise on one format across all APIs.
- **Not testing error paths** — Most production bugs live on the error path. Every happy-path test should have a corresponding error-path test.
- **Frontend error boundary too high/low** — Too high = blank screen for minor errors. Too low = dozens of tiny isolated failures. Scope boundaries to meaningful UI sections.
- **Not propagating correlation IDs** — Losing the trace ID at a service boundary makes distributed debugging nearly impossible. Pass `traceparent` / correlation headers on every outbound call.
