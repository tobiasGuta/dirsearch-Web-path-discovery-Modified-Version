dirsearch - Web path discovery (Modified Version)
=========

> **Note:** This repository is a modified version of the original [dirsearch](https://github.com/maurosoria/dirsearch) by Mauro Soria. It contains custom enhancements including WAF detection and bypass capabilities.

odifications
------------
This version includes the following enhancements:
- **WAF Detection**: Automatically detects if a WAF (Web Application Firewall) is present (e.g., Cloudflare, CloudFront, Incapsula, AWS WAF) and warns the user.
  - **Smart Fingerprinting**: Distinguishes between "True WAF Blocks" and "Application Logic Errors" (e.g., a 403 from Cloudflare vs. a 403 from the backend app).
  - **Server Detection**: Identifies Nginx, Apache, and IIS server blocks.
- **WAF Bypass**: Added `--bypass-waf` flag to use `cloudscraper` for bypassing WAF protections like Cloudflare's "Under Attack Mode".
  - **Browser Emulation**: Initializes a real Chrome browser profile to solve JavaScript challenges.
  - **Header Synchronization**: Automatically syncs headers between the solver and the scanner to prevent detection.
- **Smart Calibration**: Added `--calibration` to detect "Soft 403/404" responses where WAFs return 200 OK or 403 Forbidden for everything.
- **Mutation Fuzzing**: Added `--mutation` to automatically generate variations of found paths (e.g., `admin` -> `admin.bak`, `v1` -> `v2`).
- **Wildcard Control**: Added `--no-wildcard` to disable wildcard filtering and show all results (useful for debugging WAFs).
- **Enhanced Crawling**: Improved JavaScript and text crawling capabilities.
