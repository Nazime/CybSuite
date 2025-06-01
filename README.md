# CybSuite

This project is currently in Alpha stage and under active development. While core functionality is implemented and tested, the API and features may change significantly between versions.

**CybSuite** is a collection of security tools and scripts for penetration testing, configuration review, and reconnaissance. The following tools are available:

- [**cybs-db**]: A centralized database for penetration testing, configuration review, and security assessments. Features built-in ingestors for common security tools (Nmap, Masscan, etc.), passive vulnerability scanning capabilities, reporting capabilities, and a planned web interface.
- [**cybs-review**]: A framework for configuration review that performs post-analysis of extracted configurations. Currently working for Windows systems, with Linux support coming soon.


## Installation

PostgreSQL is required for CybSuite. You can easily set it up using Docker:

```bash
# Pull and run PostgreSQL container
sudo docker run --name postgres \
    -e POSTGRES_PASSWORD=postgres \
    -p 5432:5432 \
    -d postgres
```

The default PostgreSQL connection settings can be modified in `~/cybsuite/conf.toml`:

Install CybSuite using pipx:

```bash
pipx install cybsuite
```

## Cybs-db quick demo

Cybs-db can ingest various types of security scans, including Nmap and Masscan results:

```bash
# Ingest scan results
cybs-db ingest nmap scans/nmap/*.xml
cybs-db ingest masscan scans/masscan/*

# Request data in different formats
cybs-db request host --format json > hosts.json
cybs-db request service --format ipport --protocol tcp > ipport_tcp.txt
cybs-db request service --port 445 --format ip > smb.txt

# Report identified vulnerabilities
cybs-db report html
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

Query the database from your previous review run:

```bash
cybs-db request windows_user --format json
```
