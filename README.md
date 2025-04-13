# CybSuite

**CybSuite** is a set of tools primarily focused on configuration review, with penetration testing capabilities planned for future releases. It is actively under development and currently includes only configuration review. The following tools are available:

- [**cybsuite-review**]: A framework for configuration review that works in two phases: first extracting system configurations, then analyzing them for security issues.
- [**cybsuite-db**]: An extensible database designed to store all security-related information.

## Install


PostgreSQL is required for CybSuite. You can easily set it up using Docker:

```bash
# Modify the password as needed
sudo docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

Install CybSuite using pipx (recommended for Python package installation):

```bash
pipx install cybsuite
```
