# dirsearch - Web Path Discovery (Modified Version)

> **Note:** This is a highly modified version of the original [dirsearch](https://github.com/maurosoria/dirsearch). It has been enhanced with forensic-grade output, advanced WAF detection, and smart fuzzing capabilities.

## Key Features

### 1. Forensic-Grade Output
Gone are the emojis and messy text. This version features a strict, pipe-separated table designed for professional analysis.
*   **TIME**: Timestamp of the request.
*   **CODE**: HTTP Status Code (Colored by category).
*   **TYPE**: 3-Letter Classification Code.
    *   `WAF`: Active WAF Block (Red).
    *   `APP`: Application Logic / False Positive (Cyan).
    *   `SYS`: Server/Infrastructure Message (Grey).
    *   `OK `: Successful Response (Green).
*   **SIZE**: Response size.
*   **SOURCE**: Specific detection (e.g., "Cloudflare WAF", "AWS (App Logic)", "Nginx Default").
*   **URL**: The discovered path (Redirects highlighted with `->`).

### 2. Advanced WAF Fingerprinting
Instead of just saying "403 Forbidden", this tool analyzes the response body and headers to tell you **why** it was blocked:
*   **Infrastructure vs. App Logic**: Distinguishes between a block from Cloudflare/AWS and a standard 403 from the backend application.
*   **Server Detection**: Identifies default pages from Nginx, Apache, and IIS.

### 3. Smart Capabilities
*   **`--calibration`**: Automatically detects "Soft 403/404" responses (wildcards) to reduce false positives.
*   **`--mutation`**: Automatically generates variations of found paths (e.g., finding `admin`, it checks `admin.bak`, `admin.old`, `v1` -> `v2`).
*   **`--no-wildcard`**: Option to disable wildcard filtering completely for debugging WAFs.
*   **`--bypass-waf`**: Integrated `cloudscraper` to bypass anti-bot protections.
*   **Smart User-Agents**: Uses `fake-useragent` library (if available) to generate realistic, up-to-date User-Agent strings.

### 4. Dynamic Dashboard
The startup banner is now a dynamic dashboard that confirms **exactly** what is running. It displays active headers, proxy settings, WAF modes, and filters in a clean key-value grid.

---

## Installation

**Requirement: Python 3.9 or higher**

1.  Clone this repository:
    ```bash
    git clone https://github.com/tobiasGuta/dirsearch-Web-path-discovery-Modified-Version.git
    cd dirsearch-Web-path-discovery-Modified-Version
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

```bash
python3 dirsearch.py -u <URL> [options]
```

### New & Important Flags

| Flag | Description |
| :--- | :--- |
| `--calibration` | Perform calibration to detect soft 403/404 responses. |
| `--mutation` | Apply mutation techniques to discovered paths (e.g. backups, versions). |
| `--no-wildcard` | Disable wildcard detection (show all results). |
| `--bypass-waf` | Try to bypass WAF using cloudscraper. |
| `--random-agent` | Use `fake-useragent` to rotate User-Agents for every request. |

### Common Examples

**Simple Scan:**
```bash
python3 dirsearch.py -u https://target.com -e php,html,js
```

**WAF Bypass Scan with Random Agents:**
```bash
python3 dirsearch.py -u https://target.com --bypass-waf --random-agent
```

**Forensic Scan (Calibration + Mutation):**
```bash
python3 dirsearch.py -u https://target.com --calibration --mutation
```

**Custom Headers & Filters:**
```bash
python3 dirsearch.py -u https://target.com -H "Authorization: Bearer 123" -i 200,403 --exclude-sizes 0B
```

---

## Understanding the Output

The output is designed to be parsed visually or by tools.

```text
[+] TARGET       : https://example.com/
[+] METHOD       : GET
[+] THREADS      : 25
[+] EXTENSIONS   : php, asp, html
[+] MODE         : WAF Bypass Active

14:20:05 | 403  | WAF  | 520B     | Cloudflare WAF        | /admin/login
14:20:06 | 403  | APP  | 12.5KB   | AWS (App Logic)       | /api/v1/users
14:20:07 | 404  | SYS  | 152B     | Nginx Default         | /hidden_file
14:20:08 | 200  | OK   | 4.2KB    |                       | /public/images
14:20:09 | 301  | RED  | 0B       |                       | /redirect -> /login
```

*   **WAF**: The request was blocked by a security solution (Cloudflare, AWS, etc.).
*   **APP**: The application itself denied access (likely a valid endpoint that requires auth).
*   **SYS**: A default server page or infrastructure error.

---

## Full Options

```text
Usage: dirsearch.py [-u|--url] target [-e|--extensions] extensions [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit

  Mandatory:
    -u URL, --url=URL   Target URL(s), can use multiple flags
    -l PATH, --urls-file=PATH
                        URL list file
    --stdin             Read URL(s) from STDIN
    --cidr=CIDR         Target CIDR
    --raw=PATH          Load raw HTTP request from file
    --config=PATH       Path to configuration file

  Dictionary Settings:
    -w WORDLISTS, --wordlists=WORDLISTS
                        Wordlist files (separated by commas)
    -e EXTENSIONS, --extensions=EXTENSIONS
                        Extension list (e.g. php,asp)
    -f, --force-extensions
                        Add extensions to the end of every wordlist entry
    --mutation          Mutate found paths to discover more
    -U, --uppercase     Uppercase wordlist
    -L, --lowercase     Lowercase wordlist

  General Settings:
    -t THREADS, --threads=THREADS
                        Number of threads
    -r, --recursive     Brute-force recursively
    --deep-recursive    Perform recursive scan on every directory depth
    --force-recursive   Do recursive brute-force for every found path
    --recursion-status=CODES
                        Valid status codes to perform recursive scan
    --subdirs=SUBDIRS   Scan sub-directories of the given URL[s]
    -i CODES, --include-status=CODES
                        Include status codes
    -x CODES, --exclude-status=CODES
                        Exclude status codes
    --exclude-sizes=SIZES
                        Exclude responses by sizes
    --exclude-text=TEXTS
                        Exclude responses by text
    --exclude-regex=REGEX
                        Exclude responses by regular expression
    --no-wildcard       Disable wildcard detection (show all results)
    --bypass-waf        Try to bypass WAF using cloudscraper
    --calibration       Perform calibration to detect soft 403/404 responses

  Request Settings:
    -m METHOD, --http-method=METHOD
                        HTTP method (default: GET)
    -d DATA, --data=DATA
                        HTTP request data
    -H HEADERS, --header=HEADERS
                        HTTP request header
    --random-agent      Choose a random User-Agent for each request
    --auth=CREDENTIAL   Authentication credential (user:password or bearer)
    --cookie=COOKIE     Cookie

  Connection Settings:
    --timeout=TIMEOUT   Connection timeout
    --delay=DELAY       Delay between requests
    -p PROXY, --proxy=PROXY
                        Proxy URL (HTTP/SOCKS)
    --tor               Use Tor network as proxy
    --max-rate=RATE     Max requests per second
    --retries=RETRIES   Number of retries for failed requests

  View Settings:
    --full-url          Full URLs in the output
    --redirects-history Show redirects history
    --no-color          No colored output
    -q, --quiet-mode    Quiet mode

  Output Settings:
    -o PATH, --output-file=PATH
                        Output file location
    --format=FORMAT     Report format (simple, plain, json, xml, md, csv, html)
```

---

*Original dirsearch by Mauro Soria. Modifications by me.*
