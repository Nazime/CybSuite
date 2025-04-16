# Introduction

## Overview

CyberDB is the core component of the CybSuite tools, responsible for managing all data. Currently, it is primarily utilized by cybs-db for data management. The database is built on PostgreSQL and is designed to be extensible, allowing for easy schema extensions as needed.

CyberDB includes a CLI `cybs-db` that allows users to query and update its data efficiently.

## Key Features

- **Extensible Plugins**: Supports two types of plugins that can be customized and extended:
  - **Ingestors**: Facilitate the import of data into the database from external tools like Masscan, Nmap, BloodHound, etc.
  - **Reporters**: Generate a variety of reports in formats such as HTML, PDF, XLSX, and more.
