# Contributing to ChatCRM

**English** · [Español](#contribuir-a-chatcrm)

Thanks for your interest in ChatCRM. This guide applies to every repository in
[`chat-crm-suite`](https://github.com/chat-crm-suite).

## Before you start

- Search the [issues](https://github.com/issues?q=org%3Achat-crm-suite) first; open one to discuss larger changes before writing code.
- Security problems are never reported in public issues — see [SECURITY.md](SECURITY.md).
- By contributing you agree that your work is licensed under the repository's license
  ([PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)).

## Branches

| Branch | Purpose |
| --- | --- |
| `main` | Production. Receives release merges (`chore(release): merge develop into main`, tagged `vX.Y.Z`) and `hotfix/*` only. |
| `develop` | Integration. All daily work lands here. |
| `feature/*`, `fix/*` | Branch **from `develop`**, merge back with `--no-ff` through a pull request. |
| `hotfix/*` | Branch from `main` for urgent fixes; merged into `main` and back into `develop`. |

Changes that touch both the API and the web app use the **same branch name in both repositories**.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/) in English, with a [gitmoji](https://gitmoji.dev/):

```
feat(chats): ✨ show unread counters per conversation
fix(api): 🐛 persist inbound wamid in messages.external_id
docs(readme): 📝 add quick start
```

Never commit `.env*` files or secrets.

## Pull requests

1. Keep each pull request focused on one change.
2. Run the checks of the repository you touched:
   - **chat-crm-api**: `pnpm lint`, `pnpm test`, and `pnpm docs:check` if contracts changed.
   - **chat-crm-app**: `pnpm lint`, `pnpm test`, `npx tsc -b`.
3. New API payloads are defined once, as Zod schemas in `chat-crm-api/src/contracts/`; the web app imports them — never re-declare them by hand.
4. Code, comments, tests, commits and API docs are written in English; only user-facing translations go in other languages.
5. Fill in the pull request template.

---

# Contribuir a ChatCRM

[English](#contributing-to-chatcrm) · **Español**

Gracias por tu interés en ChatCRM. Esta guía aplica a todos los repositorios de
[`chat-crm-suite`](https://github.com/chat-crm-suite).

## Antes de empezar

- Busca primero en los [issues](https://github.com/issues?q=org%3Achat-crm-suite). Para cambios grandes, abre uno y conversemos antes de programar.
- Los problemas de seguridad nunca se reportan en issues públicos: ver [SECURITY.md](SECURITY.md).
- Al contribuir aceptas que tu trabajo queda bajo la licencia del repositorio
  ([PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)).

## Ramas

| Rama | Para qué |
| --- | --- |
| `main` | Producción. Solo recibe el merge de release (`chore(release): merge develop into main`, con tag `vX.Y.Z`) y `hotfix/*`. |
| `develop` | Integración. Aquí llega todo el trabajo diario. |
| `feature/*`, `fix/*` | Se crean **desde `develop`** y vuelven con `--no-ff` mediante un pull request. |
| `hotfix/*` | Se crean desde `main` para arreglos urgentes; se unen a `main` y de vuelta a `develop`. |

Los cambios que tocan la API y la app web usan **el mismo nombre de rama en ambos repositorios**.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/es/) en inglés, con un [gitmoji](https://gitmoji.dev/):

```
feat(chats): ✨ show unread counters per conversation
fix(api): 🐛 persist inbound wamid in messages.external_id
docs(readme): 📝 add quick start
```

Nunca subas archivos `.env*` ni secretos.

## Pull requests

1. Cada pull request debe enfocarse en un solo cambio.
2. Corre las verificaciones del repositorio que tocaste:
   - **chat-crm-api**: `pnpm lint`, `pnpm test`, y `pnpm docs:check` si cambiaron los contratos.
   - **chat-crm-app**: `pnpm lint`, `pnpm test`, `npx tsc -b`.
3. Los payloads nuevos de la API se definen una sola vez, como esquemas Zod en `chat-crm-api/src/contracts/`; la app web los importa. Nunca los vuelvas a declarar a mano.
4. Código, comentarios, tests, commits y documentación de la API van en inglés; solo las traducciones para el usuario van en otros idiomas.
5. Completa la plantilla del pull request.
