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
    --raw=PATH          Load raw HTTP request from file (use '--scheme' flag
                        to set the scheme)
    --nmap-report=PATH  Load targets from nmap report (Ensure the inclusion of
                        the -sV flag during nmap scan for comprehensive
                        results)
    -s SESSION_FILE, --session=SESSION_FILE
                        Session file
    --config=PATH       Path to configuration file (Default:
                        'DIRSEARCH_CONFIG' environment variable, otherwise
                        'config.ini')

  Dictionary Settings:
    -w WORDLISTS, --wordlists=WORDLISTS
                        Wordlist files or directories contain wordlists
                        (separated by commas)
    -e EXTENSIONS, --extensions=EXTENSIONS
                        Extension list, separated by commas (e.g. php,asp)
    -f, --force-extensions
                        Add extensions to the end of every wordlist entry. By
                        default dirsearch only replaces the %EXT% keyword with
                        extensions
    --overwrite-extensions
                        Overwrite other extensions in the wordlist with your
                        extensions (selected via `-e`)
    --exclude-extensions=EXTENSIONS
                        Exclude extension list, separated by commas (e.g.
                        asp,jsp)
    --prefixes=PREFIXES
                        Add custom prefixes to all wordlist entries (separated
                        by commas)
    --suffixes=SUFFIXES
                        Add custom suffixes to all wordlist entries, ignore
                        directories (separated by commas)
    --mutation          Mutate found paths to discover more
    -U, --uppercase     Uppercase wordlist
    -L, --lowercase     Lowercase wordlist
    -C, --capital       Capital wordlist

  General Settings:
    -t THREADS, --threads=THREADS
                        Number of threads
    -a, --async         Enable asynchronous mode
    -r, --recursive     Brute-force recursively
    --deep-recursive    Perform recursive scan on every directory depth (e.g.
                        api/users -> api/)
    --force-recursive   Do recursive brute-force for every found path, not
                        only directories
    -R DEPTH, --max-recursion-depth=DEPTH
                        Maximum recursion depth
    --recursion-status=CODES
                        Valid status codes to perform recursive scan, support
                        ranges (separated by commas)
    --filter-threshold=THRESHOLD
                        Maximum number of results with duplicate responses
                        before getting filtered out
    --subdirs=SUBDIRS   Scan sub-directories of the given URL[s] (separated by
                        commas)
    --exclude-subdirs=SUBDIRS
                        Exclude the following subdirectories during recursive
                        scan (separated by commas)
    -i CODES, --include-status=CODES
                        Include status codes, separated by commas, support
                        ranges (e.g. 200,300-399)
    -x CODES, --exclude-status=CODES
                        Exclude status codes, separated by commas, support
                        ranges (e.g. 301,500-599)
    --exclude-sizes=SIZES
                        Exclude responses by sizes, separated by commas (e.g.
                        0B,4KB)
    --exclude-text=TEXTS
                        Exclude responses by text, can use multiple flags
    --exclude-regex=REGEX
                        Exclude responses by regular expression
    --exclude-redirect=STRING
                        Exclude responses if this regex (or text) matches
                        redirect URL (e.g. '/index.html')
    --exclude-response=PATH
                        Exclude responses similar to response of this page,
                        path as input (e.g. 404.html)
    --no-wildcard       Disable wildcard detection (show all results)
    --skip-on-status=CODES
                        Skip target whenever hit one of these status codes,
                        separated by commas, support ranges
    --min-response-size=LENGTH
                        Minimum response length
    --max-response-size=LENGTH
                        Maximum response length
    --max-time=SECONDS  Maximum runtime for the scan
    --target-max-time=SECONDS
                        Maximum runtime for a target
    --exit-on-error     Exit whenever an error occurs
    --bypass-waf        Try to bypass WAF using cloudscraper (requires
                        cloudscraper installed)
    --calibration       Perform calibration to detect soft 403/404 responses

  Request Settings:
    -m METHOD, --http-method=METHOD
                        HTTP method (default: GET)
    -d DATA, --data=DATA
                        HTTP request data
    --data-file=PATH    File contains HTTP request data
    -H HEADERS, --header=HEADERS
                        HTTP request header, can use multiple flags
    --headers-file=PATH
                        File contains HTTP request headers
    -F, --follow-redirects
                        Follow HTTP redirects
    --random-agent      Choose a random User-Agent for each request
    --auth=CREDENTIAL   Authentication credential (e.g. user:password or
                        bearer token)
    --auth-type=TYPE    Authentication type (basic, digest, bearer, ntlm, jwt)
    --cert-file=PATH    File contains client-side certificate
    --key-file=PATH     File contains client-side certificate private key
                        (unencrypted)
    --user-agent=USER_AGENT
    --cookie=COOKIE     

  Connection Settings:
    --timeout=TIMEOUT   Connection timeout
    --delay=DELAY       Delay between requests
    -p PROXY, --proxy=PROXY
                        Proxy URL (HTTP/SOCKS), can use multiple flags
    --proxies-file=PATH
                        File contains proxy servers
    --proxy-auth=CREDENTIAL
                        Proxy authentication credential
    --replay-proxy=PROXY
                        Proxy to replay with found paths
    --tor               Use Tor network as proxy
    --scheme=SCHEME     Scheme for raw request or if there is no scheme in the
                        URL (Default: auto-detect)
    --max-rate=RATE     Max requests per second
    --retries=RETRIES   Number of retries for failed requests
    --ip=IP             Server IP address
    --interface=NETWORK_INTERFACE
                        Network interface to use

  Advanced Settings:
    --crawl             Crawl for new paths in responses

  View Settings:
    --full-url          Full URLs in the output (enabled automatically in
                        quiet mode)
    --redirects-history
                        Show redirects history
    --no-color          No colored output
    -q, --quiet-mode    Quiet mode
    --disable-cli       Turn off command-line output

  Output Settings:
    -O FORMAT, --output-formats=FORMAT
                        Report formats, separated by commas (Available:
                        simple, plain, json, xml, md, csv, html, sqlite)
    -o PATH, --output-file=PATH
                        Output file location
    --mysql-url=URL     Database URL for MySQL output (Format:
                        mysql://[username:password@]host[:port]/database-name)
    --postgres-url=URL  Database URL for PostgreSQL output (Format:
                        postgres://[username:password@]host[:port]/database-
                        name)
    --log=PATH          Log file
```

---

*Original dirsearch by Mauro Soria. Modifications by me.*
