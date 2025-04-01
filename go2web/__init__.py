#!/usr/bin/env python3
import socket
import argparse
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

class HTTPClient:
    def __init__(self):
        self.cache_dir = os.path.expanduser("~/.go2web_cache")
        self.cache_duration = timedelta(hours=1)
        os.makedirs(self.cache_dir, exist_ok=True)

    def _parse_url(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        parsed = urlparse(url)
        return parsed

    def _create_socket(self, host, port, is_https=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if is_https:
            import ssl
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)
        sock.connect((host, port))
        return sock

    def _get_cached_response(self, url):
        cache_file = os.path.join(self.cache_dir, re.sub(r'[^\w]', '_', url))
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
                if datetime.fromisoformat(cached_data['timestamp']) + self.cache_duration > datetime.now():
                    return cached_data['content']
        return None

    def _cache_response(self, url, content):
        cache_file = os.path.join(self.cache_dir, re.sub(r'[^\w]', '_', url))
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'content': content
            }, f)

    def get(self, url):
        # Check cache first
        cached_content = self._get_cached_response(url)
        if cached_content:
            return cached_content

        parsed_url = self._parse_url(url)
        is_https = parsed_url.scheme == 'https'
        port = 443 if is_https else 80
        host = parsed_url.netloc

        sock = self._create_socket(host, port, is_https)
        
        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query

        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "User-Agent: go2web/1.0\r\n"
        request += "Accept: text/html,application/json\r\n"
        request += "Accept-Encoding: gzip, deflate\r\n"
        request += "Connection: close\r\n"
        request += "\r\n"

        sock.send(request.encode())
        
        response = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data

        sock.close()

        header_end = response.find(b"\r\n\r\n")
        if header_end == -1:
            return "Error: Invalid response"

        headers = response[:header_end].decode('utf-8', errors='ignore')
        body = response[header_end + 4:]

        # Check if response is gzipped
        if 'Content-Encoding: gzip' in headers:
            import gzip
            try:
                body = gzip.decompress(body)
            except:
                pass

        try:
            # Try UTF-8 first
            body = body.decode('utf-8')
        except UnicodeDecodeError:
            try:
                body = body.decode('iso-8859-1')
            except UnicodeDecodeError:
                body = body.decode('utf-8', errors='ignore')

        # Handle redirects
        if "301" in headers or "302" in headers:
            location = re.search(r"Location: (.+)\r\n", headers)
            if location:
                redirect_url = location.group(1)
                if not redirect_url.startswith(('http://', 'https://')):
                    redirect_url = urljoin(url, redirect_url)
                return self.get(redirect_url)

        # Parse HTML and extract text
        soup = BeautifulSoup(body, 'html.parser')
        
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'noscript', 'iframe', 'form', 'button', 'input', 'select', 'textarea', 'meta', 'link', 'aside', 'menu', 'menuitem', 'dialog', 'dialog', 'details', 'summary', 'figure', 'figcaption', 'picture', 'source', 'track', 'video', 'audio', 'embed', 'object', 'param', 'canvas', 'svg', 'math', 'map', 'area', 'optgroup', 'option', 'fieldset', 'legend', 'label', 'datalist', 'output', 'progress', 'meter', 'time', 'mark', 'ruby', 'rt', 'rp', 'bdi', 'bdo', 'wbr', 'slot', 'template', 'portal']):
            element.decompose()
            
        for element in soup.find_all(class_=re.compile(r'menu|nav|header|footer|sidebar|banner|ad|cookie|popup|modal|tooltip|dropdown|button|link|social|share|comment|related|widget|sidebar|footer|header|navigation|breadcrumb|pagination|search|form|login|signup|subscribe|newsletter|cookie-notice|banner|advertisement|social-share|related-posts|comments-section|widget-area|sidebar-widget|footer-widget|header-widget|navigation-menu|breadcrumbs|pagination-links|search-form|login-form|signup-form|subscribe-form|newsletter-form')):
            element.decompose()
            
        main_content = None
        for tag in ['main', 'article', 'div']:
            main_content = soup.find(tag, class_=re.compile(r'main|content|article|post|entry|text|body|description|summary|excerpt'))
            if main_content:
                break
                
        if not main_content:
            main_content = soup.find('body')
            
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            
            text = re.sub(r'\s+', ' ', text)
            
            text = re.sub(r'Menu|Navigation|Search|Login|Sign up|Subscribe|Follow us|Share|More|Close|Open|Next|Previous|Back|Forward|Home|About|Contact|Terms|Privacy|Cookie|Settings|Options|Help|Support|Feedback|Report|Download|Upload|Save|Delete|Edit|Update|Refresh|Reload|Cancel|Submit|Send|Post|Comment|Reply|Like|Share|Follow|Subscribe|Unsubscribe|Register|Sign in|Log in|Log out|Profile|Account|Settings|Options|Help|Support|Feedback|Report|Download|Upload|Save|Delete|Edit|Update|Refresh|Reload|Cancel|Submit|Send|Post|Comment|Reply|Like|Share|Follow|Subscribe|Unsubscribe|Register|Sign in|Log in|Log out|Profile|Account', '', text)
            
            paragraphs = text.split('.')
            
            # Clean up each paragraph
            cleaned_paragraphs = []
            for para in paragraphs:
                para = para.strip()
                if para and len(para) > 10:  # Only keep meaningful paragraphs
                    cleaned_paragraphs.append(para + '.')
            
            text = '\n\n'.join(cleaned_paragraphs)
            
            # Cache the response
            self._cache_response(url, text)
            
            return text
        else:
            return "Error: Could not extract content from the page"

    def search(self, query):
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        response = self.get(search_url)
        
        soup = BeautifulSoup(response, 'html.parser')
        results = []
        
        for result in soup.select('.result')[:10]:
            title_elem = result.select_one('.result__title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                link = title_elem.find('a')
                if link:
                    redirect_url = link.get('href', '')
                    if redirect_url.startswith('//duckduckgo.com/l/?uddg='):
                        import urllib.parse
                        actual_url = urllib.parse.unquote(redirect_url.split('uddg=')[1])
                        if '&rut=' in actual_url:
                            actual_url = actual_url.split('&rut=')[0]
                        results.append(f"{title}\n{actual_url}\n")
                    else:
                        results.append(f"{title}\n{redirect_url}\n")
        
        return "\n".join(results) if results else "No results found."

def main():
    parser = argparse.ArgumentParser(description='go2web - a simple web client')
    parser.add_argument('-u', '--url', help='Make an HTTP request to the specified URL')
    parser.add_argument('-s', '--search', help='Search the term using DuckDuckGo')
    
    args = parser.parse_args()
    
    client = HTTPClient()
    
    if args.url:
        try:
            response = client.get(args.url)
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
    elif args.search:
        try:
            results = client.search(args.search)
            print(results)
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 