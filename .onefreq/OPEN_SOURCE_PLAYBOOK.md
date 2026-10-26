# Open-Source Project Playbook

Apply when a project is intended for public distribution and third-party contributions. This is not a substitute for legal advice or ecosystem-specific packaging rules.

## Governance and ownership

- Explicitly choose a license with the legal rights to publish the code. **No license is automatically granted** by a public repository.
- Identify maintainers, code of conduct expectations, contribution process, support policy, and a channel for private security disclosures.
- Distinguish experimental from stable APIs and explain compatibility/semver policy.
- Document third-party dependencies and their licenses; verify attribution and redistribution obligations.
- Define which issues or PRs need maintainer review, and what changes require design discussion.

## Contributor experience

- State problem, audience, value proposition, supported environments and non-goals in the public README.
- Offer an accurate quickstart that has been executed in a clean environment. Do not promise one-command setup without testing it.
- Supply examples, env variable names **without secrets**, data fixtures and troubleshooting paths appropriate for the actual stack.
- Explain module boundaries, how to run tests, formatting and review requirements.
- Keep PRs scoped and testable; reject breaking changes without migration/documentation strategy.

## Release readiness gates

1. Ownership and legal permission to publish are confirmed.
2. License choice and required notices are actually present in the publishable repository.
3. Secrets, private data, internal domains, unlicensed assets and accidental generated files are reviewed.
4. Dependency provenance/licenses and known security issues are reviewed.
5. Clean installation/build, tests, smoke flows and examples are run in a representative environment.
6. Public docs match actual behavior; limitations, compatibility, data handling and security contact are explicit.
7. Changelog, versioning, migration notes and rollback/recovery path are ready when applicable.
8. A maintainer authorizes publication, tags/releases, package publication or deployment before external effects occur.

## Open-source design quality

- Keep installation and upgrades reproducible; declare supported versions.
- Prefer boring defaults and minimal required services.
- Make integrations optional when possible and degrade clearly when credentials are absent.
- Favor extension points based on observed third-party use cases, not speculative plugin marketplaces.
- Handle errors openly and avoid vendor-locking users to an undeclared external service.

## Status to fill

- Intended license: `UNSET`
- Maintainers: `UNSET`
- Security contact/process: `UNSET`
- Versioning/support policy: `UNSET`
- Supported platforms: `UNSET`
- Publication authorization: `UNSET`
