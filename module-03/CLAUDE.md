# Stack
- TypeScript 5.4 strict; local Node 25; Lambda runtime Node 22 ARM_64 (esbuild-bundled, not tsc)
- npm workspaces — never yarn/pnpm; `packages/core` · `packages/lambdas` · `packages/cli` · `packages/infra` · `packages/frontend`
- Frontend: React 18 + Vite 5 + Cytoscape.js; excluded from root tsconfig project references
- Infra: AWS CDK v2 (`NodejsFunction` bundles lambdas via esbuild with `externalModules: []`)
- Tests: vitest + `fast-check` for property-based tests

# Conventions
- Prettier: single quotes, semicolons, trailing commas, printWidth 100, tabWidth 2
- Imports: builtin → external → internal → parent → sibling → index; newlines between; alphabetized — enforced by eslint-plugin-import
- Unused args prefixed with `_`; `no-explicit-any` is a warn — avoid and never suppress silently
- Unit tests: `*.spec.ts`; integration/handler tests: `*.test.ts`; property tests: `*.property.spec.ts`
- Cross-package imports use aliases: `@blast-radius/core`, `@blast-radius/lambdas`, `@blast-radius/cli`
- DynamoDB table names follow `BlastRadius-*` convention (e.g. `BlastRadius-AdapterRegistry`)
- Lambda function names follow `BlastRadius-*` convention (e.g. `BlastRadius-RiskAssessor`)

# Commands
- Build all: `npm run build` (root — runs `tsc --build` per workspace via project references)
- Build one package: `npm run build -w packages/<name>`
- Run all tests: `npm test`
- Lint: `npm run lint`
- Format write: `npm run format` / check: `npm run format:check`
- Frontend dev server: `npm run dev -w packages/frontend` (reads `VITE_API_BASE_URL`, falls back to `/api`)
- CDK synth/deploy: `cd packages/infra && npx cdk synth|deploy`
- CLI (after build): `BLAST_RADIUS_API_URL=<url> node packages/cli/dist/index.js analyze --input <file> --threshold <0-100>`

# Do-not
- Never add a dependency without asking first
- Never edit files under `packages/*/dist/`, `packages/infra/cdk.out/`, or `examples/*/cdk.out/`
- Never use `any` without justification; never silence the lint warning with inline disable comments
- Never run `cdk deploy` without confirming the target AWS account/region with the user
- Never commit `cdk.context.json` changes without asking — they pin resolved account/AZ lookups
- Never set `enableAuth: false` in CDK props without the user explicitly requesting it (disables SigV4)
- Do not modify the Step Functions pipeline order (Ingestion → AdapterConversion → Discovery → Scoring → VisualizationPrep → SummaryGeneration) without understanding downstream state shape dependencies

# Glossary
- **RCM (Resource Change Manifest)**: canonical IaC-neutral JSON schema for a proposed changeset; all adapters output this
- **Adapter**: Lambda that converts a native IaC artifact (CDK diff, Terraform plan, CF changeset) into an RCM; registered in `BlastRadius-AdapterRegistry` DynamoDB table by `formatId`
- **Blast Radius**: the set of downstream AWS resources transitively affected by resources in the RCM
- **DependencyGraph**: directed graph of AWS resource relationships traversed recursively (default maxDepth 5) via AWS Config + Resource Explorer; circular references detected via visited-set; nodes carry `dependencyCoverage` (full/partial/unknown)
- **ImpactScore**: integer 0–100; formula: `round((depthScore×0.30) + (criticalityScore×0.40) + (changeTypeSeverity×0.30))`
- **CriticalityClassification**: static resource-type label (Critical/High/Medium/Low) from `criticality-map.ts`
- **RiskCategory**: final bucket from ImpactScore (≥75 Critical, ≥50 High, ≥25 Medium, else Low)
- **Verdict**: CLI pass/fail/error result; exit codes 0 (pass), 1 (fail — resource exceeds `--threshold`), 2 (error)
- **AccessScoper**: extracts requesting principal IAM ARN from SigV4 context; scopes graph/results to authorized accounts+regions; omitted resources appear in `exclusionSummary`
- **Manifest Group**: optional hierarchical grouping inside an RCM (e.g., CDK stack → nested stacks)
- **VisualizationPrep**: Lambda that writes final graph+scores to the S3 results bucket for frontend consumption
