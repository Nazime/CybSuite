# Introduction

## Overview

Arguard is a configuration review framework designed for security assessments and privilege escalation (privesc) detection. It can audit multiple systems in a single execution. Arguard allows users to extend and customize its capabilities through a plugin system.

Arguard operates by first extracting the configuration of the audited system using platform-specific scripts. The extracted data is then transferred for analysis, where Arguard performs post-review processing and generates reports, such as HTML reports.

Currently, Arguard supports Windows systems as the first implementation, with planned support for Linux, cloud environments, and services such as SQL databases, and web servers.


## Key Features

- The existing plugins are customizable, and users can develop and integrate their own custom plugins.
- Extraction can be performed with administrator privileges for a comprehensive configuration extract, or with limited privileges to identify potential privilege escalation vectors.
- Plugins can be filtered to review individual files or search for specific controls.
