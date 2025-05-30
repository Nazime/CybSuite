# CybSuite

This project is in Alpha and still under active development.


**CybSuite** is a suite of security tools focused on configuration review, with penetration testing capabilities planned for future releases. The following tools are available:

- [**cybs-review**]: A framework for configuration review that performs post-analysis of extracted configurations. Currently working for Windows systems, with Linux support coming soon.
- [**cybs-db**]: An extensible database designed to store all security-related information.

## Installation

PostgreSQL is required for CybSuite. You can easily set it up using Docker:

```bash
# Pull and run PostgreSQL container
sudo docker run --name postgres \
    -e POSTGRES_PASSWORD=postgres \
    -p 5432:5432 \
    -d postgres
```

Install CybSuite using pipx:

```bash
pipx install cybsuite
```

## Cybs-review quick demo

Quick demonstration to review Windows hosts:

1. Generate the extraction script:
```bash
cybs-review script windows > windows.ps1
```

2. Run the script on your target Windows host (with root privileges for full extraction)

3. For demonstration, download sample extracts:
```bash
mkdir extracts && cd extracts
wget https://github.com/Nazime/CybSuite/releases/download/v0.1/extracts_WIN-ALPHA.zip
wget https://github.com/Nazime/CybSuite/releases/download/v0.1/extracts_WIN-BETA.zip
```

4. Run the review and open the report:
```bash
cybs-review review extracts_WIN-ALPHA.zip extracts_WIN-BETA.zip --open-report
```

![Report Summary](https://raw.githubusercontent.com/Nazime/CybSuite/main/images/cybs-review_report_summary.png)

![Report Controls](https://raw.githubusercontent.com/Nazime/CybSuite/main/images/cybs-review_report_controls.png)

## Cybs-db

Query the database from your previous review run:

```bash
cybs-db request windows_user --format json
```
