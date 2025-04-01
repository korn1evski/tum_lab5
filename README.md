# go2web

A simple command-line web client that can make HTTP requests and perform web searches without using built-in HTTP libraries.

## Features

- Make HTTP requests to specified URLs
- Search the web using DuckDuckGo
- HTTP redirect support
- Response caching
- Content negotiation (HTML and JSON)
- Human-readable output

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd go2web
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Make the script executable and create a symbolic link:

```bash
sudo make install
```

## Usage

The program supports the following commands:

```bash
go2web -u <URL>         # Make an HTTP request to the specified URL and print the response
go2web -s <search-term> # Search the term using DuckDuckGo and print top 10 results
go2web -h               # Show help message
```

### Examples

1. Fetch a webpage:

```bash
go2web -u example.com
```

2. Search the web:

```bash
go2web -s "python programming"
```

3. Show help:

```bash
go2web -h
```

## Implementation Details

- The program implements its own HTTP client using raw sockets
- Supports both HTTP and HTTPS protocols
- Implements HTTP redirects (301, 302)
- Caches responses for 1 hour in `~/.go2web_cache`
- Uses BeautifulSoup4 for HTML parsing
- Supports content negotiation for HTML and JSON responses

## Uninstallation

To remove the program:

```bash
sudo make clean
```

## Requirements

- Python 3.6+
- beautifulsoup4
- argparse
