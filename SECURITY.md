# Security

This project modifies Unity project files when its CLI is run. Treat integration recipes like code.

## Reporting

If you find a security issue, open a private report through GitHub Security Advisories if available, or contact the repository owner directly.

## Safety Expectations

- Review recipes before running them on production projects.
- Use source control before applying integrations.
- Do not commit secrets, Firebase config files, API keys, keystores, or private SDK licenses.
- Verify redistribution rights before publishing any vendored Unity Asset Store plugin.
- Use `--no-report` when validating projects where writing report files is not desired.
