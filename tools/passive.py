#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import argparse
import json
import time
import random
import requests
import urllib3
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse
import base64
import re
import threading
import copy
# mmh3 moved to function-level to prevent startup crash if missing

# Silence SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
#  GLOBAL CONFIG & CONSTANTS
# ==============================================================================

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KEYS_FILE = os.path.join(SCRIPT_DIR, "keys.json")
DEFAULT_RAPIDDNS_SCRIPT = os.path.join(SCRIPT_DIR, "run_rapiddns.sh")

# Color Codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'

# User-Agents for Scrapers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
]

# Tool Definitions
TOOLS = {
    "binary": [
        {"name": "Subfinder", "bin": ["subfinder"], "cmd": "subfinder -d {target} -all -silent -o {outfile}", "desc": "Fast passive enumeration"},
        {"name": "Assetfinder", "bin": ["assetfinder"], "cmd": "assetfinder --subs-only {target} > {outfile}", "desc": "Finds domains and subdomains"},
        {"name": "Findomain", "bin": ["findomain"], "cmd": "findomain -t {target} -u {outfile}", "desc": "High-performance subdomain discovery"},
        {"name": "Chaos", "bin": ["chaos"], "cmd": "chaos -d {target} -silent -o {outfile}", "desc": "ProjectDiscovery Chaos dataset"},
        {"name": "Amass", "bin": ["amass"], "cmd": "amass enum -passive -d {target} -o {outfile}", "desc": "OWASP Amass (Passive)"},
        {"name": "Github-Subdomains", "bin": ["github-subdomains"], "cmd": "github-subdomains -d {target} -t {github} -o {outfile}", "desc": "Scrapes GitHub (Needs Token)", "req_key": "github"},
        {"name": "Shosubgo", "bin": ["shosubgo"], "cmd": "shosubgo -d {target} -s {shodan} > {outfile}", "desc": "Shodan subdomain finder", "req_key": "shodan"},
        {"name": "Gau", "bin": ["gau", "unfurl"], "cmd": "gau --subs {target} | unfurl -u domains", "desc": "Wayback/AlienVault URL fetcher"},
        {"name": "Cero", "bin": ["cero"], "cmd": "cero -d {target}", "desc": "Certificate Transparency Scraper"},
        {"name": "CSPRecon", "bin": ["csprecon"], "cmd": "echo {target} | csprecon -s", "desc": "CSP Header Scraper"},
        {"name": "Haktrails", "bin": ["haktrails"], "cmd": "echo {target} | haktrails subdomains", "desc": "SecurityTrails Query", "check_file": "~/.config/haktools/haktrails-config.yml"},
        {"name": "AnalyticsRelationships", "bin": ["analyticsrelationships"], "cmd": "analyticsrelationships -u {target}", "desc": "Google Analytics ID Pivot"},
        {"name": "Subdog", "bin": ["subdog"], "cmd": "echo '{target}' | subdog", "desc": "Subdomain enumeration tool"},
        {"name": "Xsubfind3r", "bin": ["xsubfind3r"], "cmd": "xsubfind3r -d {target}", "desc": "Passive subdomain discovery from XSS sources"},
        {"name": "Katana", "bin": ["katana"], "cmd": "katana -u {target} -ps -silent -o {outfile}", "desc": "ProjectDiscovery Katana (Passive Mode)"},
        {"name": "Waymore", "bin": ["waymore"], "cmd": "waymore -i {target} -mode U -oU {outfile}", "desc": "Advanced Wayback/CC URL crawler"},
        {"name": "Waybackurls", "bin": ["waybackurls"], "cmd": "waybackurls {target}", "desc": "OWASP Waybackurls"},
        {"name": "TLSX", "bin": ["tlsx"], "cmd": "echo {target} | tlsx -san -cn -silent -resp-only", "desc": "SSL/TLS SAN/CN Extraction"},
        {"name": "CertInfo", "bin": ["certinfo"], "cmd": "certinfo -d {target} -silent > {outfile}", "desc": "Certificate Info Gathering"},
        {"name": "ASNMap", "bin": ["asnmap"], "cmd": "asnmap -d {target} -silent > {outfile}", "desc": "Map domain to ASN CIDRs"},
        {"name": "IPFinder", "bin": ["ipfinder"], "cmd": "ipfinder -d {target} -silent > {outfile}", "desc": "Find IPs associated with domain"},
        {"name": "ARINRange", "bin": ["arinrange"], "cmd": "echo {target} | arinrange -silent > {outfile}", "desc": "ARIN IP Range Lookup"},
        {"name": "Subwiz", "bin": ["subwiz"], "cmd": "subwiz -d {target} -silent > {outfile}", "desc": "Subdomain prediction tool"},
        {"name": "Whoxysubs", "bin": ["whoxysubs"], "cmd": "whoxysubs -d {target} -silent > {outfile}", "desc": "WHOIS-based subdomain discovery"},
        {"name": "Haktrailsfree", "bin": ["haktrailsfree"], "cmd": "echo {target} | haktrailsfree --silent > {outfile}", "desc": "SecurityTrails (Free) API scraper"},
        {"name": "JSubfinder", "bin": ["jsubfinder"], "cmd": "jsubfinder -d {target} -s -silent > {outfile}", "desc": "Find subdomains in JS files"},
        {"name": "Cspfinder", "bin": ["cspfinder"], "cmd": "cspfinder -d {target} > {outfile}", "desc": "CSP Header scraper"},
        {"name": "Emailfinder", "bin": ["emailfinder"], "cmd": "emailfinder -d {target} > {outfile}", "desc": "Search for emails and related domains"},
        {"name": "Tldscan", "bin": ["tldscan"], "cmd": "tldscan -d {target} -silent > {outfile}", "desc": "Scan for top-level domains"},
        {"name": "BuiltWithSubs", "bin": ["builtwithsubs"], "cmd": "builtwithsubs -d {target} -silent > {outfile}", "desc": "BuiltWith relationship discovery"},
        {"name": "Hakrevdns", "bin": ["hakrevdns"], "cmd": "echo {target} | hakrevdns > {outfile}", "desc": "Reverse DNS lookup on domain"},
        {"name": "Udon", "bin": ["udon"], "cmd": "udon -d {target} -silent > {outfile}", "desc": "Visualization/Enumeration helper"},
        {"name": "SPK", "bin": ["spk"], "cmd": "echo {target} | spk > {outfile}", "desc": "SPK infrastructure discovery"},
        {"name": "IPRanges", "bin": ["ipranges"], "cmd": "echo {target} | ipranges -silent > {outfile}", "desc": "Find IP ranges for domain"},
        {"name": "Cdncheck", "bin": ["cdncheck"], "cmd": "echo {target} | cdncheck -silent > {outfile}", "desc": "CDN infrastructure mapping"},
        {"name": "Github-Endpoints", "bin": ["github-endpoints"], "cmd": "github-endpoints -d {target} -t {github} -o {outfile}", "desc": "Find endpoints in GitHub", "req_key": "github"},
        {"name": "Xurlfind3r", "bin": ["xurlfind3r"], "cmd": "xurlfind3r -d {target} > {outfile}", "desc": "Passive URL discovery"},
    ],
    "heavy": [
        {"name": "BBOT", "bin": ["bbot"], "cmd": "bbot -t {target} -f subdomain-enum -rf passive -o {outdir}/bbot_temp", "desc": "BBOT Recursive Passive"},
    ]
}

# ==============================================================================
#  HELPER CLASSES
# ==============================================================================

def find_binary(name):
    """Checks system PATH and common Go bin locations for a binary."""
    # 1. Check system PATH
    bin_path = shutil.which(name)
    if bin_path: return bin_path
    
    # 2. Check common Go bin locations
    home = os.path.expanduser("~")
    go_paths = [
        os.path.join(home, "go", "bin", name),
        os.path.join(home, "go", "bin", f"{name}.exe"),
        os.path.join(os.environ.get("USERPROFILE", ""), "go", "bin", name),
        os.path.join(os.environ.get("USERPROFILE", ""), "go", "bin", f"{name}.exe")
    ]
    # 3. Check GOPATH
    gopath = os.environ.get("GOPATH")
    if gopath:
        gp = os.path.join(gopath, "bin", name)
        if os.path.exists(gp): return gp
        gp_exe = os.path.join(gopath, "bin", f"{name}.exe")
        if os.path.exists(gp_exe): return gp_exe

    # 4. Check Literal Go Bin Paths
    for p in go_paths:
        if os.path.exists(p): return p

    return None

def manage_resolvers(logger):
    """Auto-refreshes public resolvers if they are older than 24h."""
    res_dir = os.path.join(os.path.expanduser("~"), ".antigravity")
    res_file = os.path.join(res_dir, "resolvers.txt")
    if not os.path.exists(res_dir): os.makedirs(res_dir)
    
    refresh = False
    if not os.path.exists(res_file): refresh = True
    else:
        try:
            age_hours = (time.time() - os.path.getmtime(res_file)) / 3600
            if age_hours > 24: refresh = True
        except: refresh = True
        
    if refresh:
        logger.log(f"Refreshing public resolvers (Trickest dataset)...", "INFO")
        try:
            r = requests.get("https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt", timeout=15)
            if r.status_code == 200:
                with open(res_file, "w") as f: f.write(r.text)
                logger.log(f"Resolvers updated: {res_file}", "SUCCESS")
            else: refresh = False 
        except: refresh = False
    return res_file if os.path.exists(res_file) else None

def should_filter(item, target, exclude_list):
    """Returns True if the item should be excluded from results."""
    if not exclude_list: return False # Optimization
    item = item.strip().lower()
    if not item: return True
    # 1. Pattern Exclusion
    if any(pattern in item for pattern in exclude_list): return True
    return False

class DualLogger:
    """Writes logs to both console and a file."""
    _print_lock = threading.Lock() # Global lock for console stability

    def __init__(self, log_file=None):
        self.log_file = log_file
        self.lock = threading.Lock() # Instance lock for file stability
        if log_file and os.path.exists(log_file):
            try: os.remove(log_file) # Start fresh
            except: pass
            
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        with DualLogger._print_lock:
            # 1. Console Output (Colored)
            if level == "INFO": print(f"[{Colors.BLUE}*{Colors.RESET}] {timestamp} - {msg}")
            elif level == "SUCCESS": print(f"[{Colors.GREEN}+{Colors.RESET}] {timestamp} - {msg}")
            elif level == "WARN": print(f"{Colors.YELLOW}[!] {timestamp} - {msg}{Colors.RESET}")
            elif level == "ERR": print(f"{Colors.RED}[x] {timestamp} - {msg}{Colors.RESET}")
            elif level == "HEADER": print(f"{Colors.HEADER}=== {msg} ==={Colors.RESET}")
            
        # 2. File Output (Use instance lock outside of global print lock to prevent deadlock)
        if self.log_file:
            clean_msg = f"[{level}] {timestamp} - {msg}\n"
            with self.lock:
                try:
                    with open(self.log_file, "a") as f:
                        f.write(clean_msg)
                except: pass

class ScanTracker:
    """Tracks the status of each tool for the final summary."""
    def __init__(self):
        self.results = [] 
        self.lock = threading.Lock()

    def add_result(self, name, count, status, error="", duration=0):
        with self.lock:
            self.results.append({
            "name": name,
            "count": count,
            "status": status,
            "error": error,
            "duration": duration
        })

    def generate_summary(self, out_dir):
        # 1. Text Table
        table = []
        table.append(f"{'TOOL NAME':<25} | {'DOMAINS':<10} | {'STATUS':<10} | {'TIME(s)':<8} | {'ERROR'}")
        table.append("-" * 90)
        
        with self.lock:
            for r in self.results:
                status_str = r['status']
                if r['status'] == "FAILED": status_str = "FAILED (!)"
                elif r['count'] == 0 and r['status'] == "SUCCESS": status_str = "No Data"
                
                table.append(f"{r['name']:<25} | {str(r['count']):<10} | {status_str:<10} | {r['duration']:.2f}     | {r['error']}")
            
        summary_path = os.path.join(out_dir, "summary.txt")
        with open(summary_path, "w") as f:
            f.write("\n".join(table))
            
        # 2. JSON Report (for machine parsing/grep)
        json_path = os.path.join(out_dir, "summary.json")
        with open(json_path, "w") as f:
            json.dump(self.results, f, indent=4)
            
        return summary_path
        
class Config:
    def __init__(self):
        self.keys = {
            "github": "", "shodan": "", "virustotal": "", "otx": "", 
            "securitytrails": "", "censys_id": "", "censys_secret": "", "facebook": "", "chaos": "",
            "binaryedge": "", "fullhunt": "", "intelx": "", "leakix": "", "fofa_email": "", "fofa_key": "",
            "quake": "", "criminalip": "", "bitdiscovery": "", "passivetotal_user": "", "passivetotal_key": "",
            "zoomeye": "", "whoisxmlapi": "", "hunter": "", "clearbit": "", "urlscan": "",
            "discord_webhook": "", "slack_webhook": ""
        }
        self.load_keys()

    def load_keys(self):
        if os.path.exists(KEYS_FILE):
            try:
                with open(KEYS_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.keys.update(loaded)
            except Exception as e:
                print(f"[!] Error loading keys.json: {e}")

    def save_keys(self):
        with open(KEYS_FILE, 'w') as f:
            json.dump(self.keys, f, indent=4)

    def get(self, key):
        return self.keys.get(key, "")

class APIScraper:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()

    def fetch(self, url, headers=None, params=None, timeout=15, auth=None):
        req_headers = {"User-Agent": random.choice(USER_AGENTS)}
        if headers: req_headers.update(headers)
        
        max_retries = 3
        backoff = 2
        for attempt in range(max_retries):
            try:
                resp = self.session.get(url, headers=req_headers, params=params, timeout=timeout, verify=False, auth=auth)
                if resp.status_code == 429:
                    wait = backoff ** (attempt + 1)
                    self.logger.log(f"Rate limited (429) on {urlparse(url).netloc}. Retrying in {wait}s...", "WARN")
                    time.sleep(wait)
                    continue
                return resp
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1: break
                time.sleep(backoff ** (attempt + 1))
        return None

    def post(self, url, headers=None, data=None, json=None, timeout=15, auth=None):
        """POST version of fetch() with identical retry/rate-limit logic."""
        req_headers = {"User-Agent": random.choice(USER_AGENTS)}
        if headers: req_headers.update(headers)
        
        max_retries = 3
        backoff = 2
        for attempt in range(max_retries):
            try:
                resp = self.session.post(url, headers=req_headers, data=data, json=json, timeout=timeout, verify=False, auth=auth)
                if resp.status_code == 429:
                    wait = backoff ** (attempt + 1)
                    self.logger.log(f"Rate limited (429) on {urlparse(url).netloc}. Retrying in {wait}s...", "WARN")
                    time.sleep(wait)
                    continue
                return resp
            except requests.exceptions.RequestException:
                if attempt == max_retries - 1: break
                time.sleep(backoff ** (attempt + 1))
        return None

    def capture_results(self, target, tracker, mode="medium"):
        scrapers = [
            ("OTX", self.scrape_otx, "otx"),
            ("CertSpotter", self.scrape_certspotter, None),
            ("UrlScan", self.scrape_urlscan, "urlscan"),
            ("Crt.sh", self.scrape_crtsh, None),
            ("Anubis", self.scrape_anubis, None),
            ("HackerTarget", self.scrape_hackertarget, None),
            ("VirusTotal", self.scrape_virustotal, "virustotal"),
            ("ShodanAPI", self.scrape_shodan, "shodan"),
            ("BugBountyData", self.scrape_bugbountydata, None),
            ("SecurityTrails", self.scrape_securitytrails, "securitytrails"),
            ("BinaryEdge", self.scrape_binaryedge, "binaryedge"),
            ("FullHunt", self.scrape_fullhunt, "fullhunt"),
            ("LeakIX", self.scrape_leakix, "leakix"),
            ("Fofa", self.scrape_fofa, "fofa_key"), # Note: Also needs fofa_email
            ("Quake", self.scrape_quake, "quake"),
            ("CriminalIP", self.scrape_criminalip, "criminalip"),
            ("IntelX", self.scrape_intelx, "intelx"),
            ("PassiveTotal", self.scrape_passivetotal, "passivetotal_key"),
            ("ZoomEye", self.scrape_zoomeye, "zoomeye"),
            ("WhoisXMLAPI", self.scrape_whoisxmlapi, "whoisxmlapi"),
            ("BitDiscovery", self.scrape_bitdiscovery, "bitdiscovery"),
            ("Hunter", self.scrape_hunter, "hunter"),
            ("Clearbit", self.scrape_clearbit, "clearbit"),
            ("Kaeferjaeger", self.scrape_kaeferjaeger, None),
            ("WebArchive", self.scrape_webarchive, None),
            ("Riddler", self.scrape_riddler, None),
            ("Crobat", self.scrape_crobat, None),
            ("Censys", self.scrape_censys, "censys_id"),
            ("Facebook", self.scrape_facebook, "facebook")
        ]

        def run_single(name, func, req_key):
            if req_key and not self.config.get(req_key):
                tracker.add_result(name, 0, "SKIPPED", "No API Key")
                return name, [], []

            start = time.time()
            try:
                res = func(target)
                if isinstance(res, tuple):
                    data, assets = res
                else:
                    data, assets = res, []
                
                count = len(data) if data else 0
                tracker.add_result(name, count, "SUCCESS", "", time.time() - start)
                if count > 0: self.logger.log(f"[{name}] Found {count} subdomains", "SUCCESS")
                return name, data, assets
            except Exception as e:
                tracker.add_result(name, 0, "FAILED", str(e), time.time() - start)
                self.logger.log(f"[{name}] Failed: {e}", "ERR")
                return name, [], []

        # Dynamic Workers based on mode
        workers = 5 if mode == "low" else 15 if mode == "medium" else 30
        self.logger.log(f"Running cloud scrapers in parallel ({workers} workers)...", "INFO")
        results = {}
        all_assets = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_name = {executor.submit(run_single, name, func, key): name for name, func, key in scrapers}
            for future in concurrent.futures.as_completed(future_to_name):
                name, data, assets = future.result()
                results[name] = data
                if assets: all_assets.extend(assets)

        # Post-processing Shodan
        if results.get("ShodanAPI"):
             results["ShodanAPI"] = [f"{s}.{target}" if isinstance(s, str) and not s.endswith(target) else str(s) for s in results["ShodanAPI"] if s]
        
        return results, all_assets

    def scrape_otx(self, target):
        key = self.config.get("otx")
        if not key: return [], []
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{target}/passive_dns"
        resp = self.fetch(url, headers={"X-OTX-API-KEY": key})
        if resp:
            try: return [x['hostname'] for x in resp.json().get('passive_dns', [])], []
            except: pass
        return [], []

    def scrape_certspotter(self, target):
        url = f"https://api.certspotter.com/v1/issuances"
        resp = self.fetch(url, params={"domain": target, "include_subdomains": "true", "expand": "dns_names"})
        if resp:
            try:
                data = resp.json()
                if not isinstance(data, list): return [], []
                res = []
                for item in data: res.extend(item.get('dns_names', []))
                return res, []
            except: pass
        return [], []

    def scrape_urlscan(self, target):
        key = self.config.get("urlscan")
        url = f"https://urlscan.io/api/v1/search/?q=domain:{target}"
        headers = {"API-Key": key} if key else {}
        resp = self.fetch(url, headers=headers)
        if resp:
            try: return [x['page']['domain'] for x in resp.json().get('results', [])], []
            except: pass
        return [], []

    def scrape_crtsh(self, target):
        url = f"https://crt.sh/?q=%.{target}&output=json"
        resp = self.fetch(url, timeout=45) # Higher timeout for crt.sh
        if resp:
            try: 
                data = resp.json()
                if isinstance(data, list):
                    subs = []
                    for x in data:
                        nv = x.get('name_value', '')
                        # Split by newline (crt.sh returns multi-domain fields)
                        for name in nv.split('\n'):
                            subs.append(name.replace('*.', '').strip())
                    return list(set(subs)), []
            except: pass
        return [], []

    
    def scrape_hackertarget(self, target):
        url = f"https://api.hackertarget.com/hostsearch/?q={target}"
        resp = self.fetch(url)
        if resp and resp.status_code == 200: return [line.split(',')[0] for line in resp.text.splitlines() if line], []
        return [], []

    def scrape_virustotal(self, target):
        key = self.config.get("virustotal")
        if not key: return [], []
        url = f"https://www.virustotal.com/api/v3/domains/{target}/subdomains?limit=100"
        resp = self.fetch(url, headers={"x-apikey": key})
        if resp:
            try: return [x['id'] for x in resp.json().get('data', [])], []
            except: pass
        return [], []

    def scrape_shodan(self, target):
        key = self.config.get("shodan")
        if not key: return [], []
        url = f"https://api.shodan.io/dns/domain/{target}?key={key}"
        resp = self.fetch(url)
        subs = []
        assets = []
        if resp:
            try:
                data = resp.json()
                for item in data.get('data', []):
                    ip = item.get('value')
                    sub = item.get('subdomain')
                    if ip and sub:
                        assets.append({"host": f"{sub}.{target}", "ip": ip, "source": "Shodan"})
                subs = data.get('subdomains', [])
            except: pass
        return subs, assets
    
    def scrape_bugbountydata(self, target):
        url = f"https://raw.githubusercontent.com/rix4uni/BugBountyData/main/data/{target}.txt"
        resp = self.fetch(url)
        if resp and resp.status_code == 200: return resp.text.splitlines(), []
        return [], []

    def scrape_securitytrails(self, target):
        key = self.config.get("securitytrails")
        if not key: return [], []
        url = f"https://api.securitytrails.com/v1/domain/{target}/subdomains"
        resp = self.fetch(url, headers={"apikey": key})
        if resp:
            try: return [f"{s}.{target}" for s in resp.json().get('subdomains', [])], []
            except: pass
        return [], []

    def scrape_binaryedge(self, target):
        key = self.config.get("binaryedge")
        if not key: return [], []
        url = f"https://api.binaryedge.io/v2/query/domains/subdomain/{target}"
        resp = self.fetch(url, headers={"X-Key": key})
        subs = []
        assets = []
        if resp:
            try:
                data = resp.json()
                subs = data.get('subs', [])
                # BinaryEdge often provides IP data in their fuller 'search' API, 
                # but for 'subdomain' it's mostly names. Adding placeholder for consistency.
            except: pass
        return subs, assets

    def scrape_fullhunt(self, target):
        key = self.config.get("fullhunt")
        if not key: return [], []
        url = f"https://fullhunt.io/api/v1/domain/{target}/subdomains"
        resp = self.fetch(url, headers={"X-API-KEY": key})
        if resp:
            try: return resp.json().get('hosts', []), []
            except: pass
        return [], []

    def scrape_intelx(self, target):
        key = self.config.get("intelx")
        if not key: return [], []
        url = "https://public-api.intelx.io/phonebook/search"
        headers = {"x-key": key, "User-Agent": random.choice(USER_AGENTS)}
        data = {"term": target, "maxresults": 100, "media": 0, "target": 1}
        try:
            r = self.post(url, headers=headers, json=data, timeout=15)
            if r and r.status_code == 200:
                sid = r.json().get('id')
                if not sid: return [], []
                time.sleep(2)
                res_url = f"https://public-api.intelx.io/phonebook/search/result?id={sid}"
                res = self.fetch(res_url, headers=headers)
                if not res: return [], []
                selectors = res.json().get('selectors', [])
                if not isinstance(selectors, list): return [], []
                return [x.get('selector') for x in selectors if x.get('selector') and target in x.get('selector', '')], []
        except: pass
        return [], []

    def scrape_leakix(self, target):
        key = self.config.get("leakix")
        if not key: return [], []
        url = f"https://leakix.net/search"
        resp = self.fetch(url, headers={"api-key": key, "Accept": "application/json"}, params={"q": target, "scope": "leak"})
        if resp:
            try: return list(set([x.get('hostname') for x in resp.json() if x.get('hostname')])), []
            except: pass
        return [], []

    def scrape_fofa(self, target):
        email = self.config.get("fofa_email")
        key = self.config.get("fofa_key")
        if not email or not key: return [], []
        qbase64 = base64.b64encode(f'domain="{target}"'.encode()).decode()
        url = f"https://fofa.info/api/v1/search/all?email={email}&key={key}&qbase64={qbase64}"
        resp = self.fetch(url)
        if resp:
            try: return list(set([x[0] for x in resp.json().get('results', [])])), []
            except: pass
        return [], []

    def scrape_quake(self, target):
        key = self.config.get("quake")
        if not key: return [], []
        url = "https://quake.360.net/api/v3/search/quake_service"
        data = {"query": f"domain:\"{target}\"", "start": 0, "size": 100}
        subs = []
        assets = []
        try:
            r = self.post(url, headers={"X-QuakeToken": key}, json=data, timeout=15)
            if not r or r.status_code != 200: return subs, assets
            results = r.json().get('data', [])
            for x in results:
                host = x.get('service', {}).get('hostname')
                ip = x.get('ip')
                port = x.get('port')
                if host:
                    subs.append(host)
                    if ip: assets.append({"host": host, "ip": ip, "port": port, "source": "Quake"})
            return list(set(subs)), assets
        except: pass
        return subs, assets

    def scrape_criminalip(self, target):
        key = self.config.get("criminalip")
        if not key: return [], []
        url = f"https://api.criminalip.io/v1/asset/search?query=domain:{target}"
        resp = self.fetch(url, headers={"x-api-key": key})
        subs = []
        assets = []
        if resp:
            try:
                results = resp.json().get('data', [])
                for x in results:
                    host = x.get('hostname')
                    ip = x.get('ip_address') # Correct field for CriminalIP
                    if host:
                        subs.append(host)
                        if ip: assets.append({"host": host, "ip": ip, "source": "CriminalIP"})
                return list(set(subs)), assets
            except: pass
        return subs, assets

    def scrape_passivetotal(self, target):
        user = self.config.get("passivetotal_user")
        key = self.config.get("passivetotal_key")
        url = f"https://api.passivetotal.org/v2/enrichment/subdomains"
        if not user or not key: return [], []
        resp = self.fetch(url, auth=(user, key), params={"query": target})
        if resp:
            try: return [f"{s}.{target}" for s in resp.json().get('subdomains', [])], []
            except: pass
        return [], []

    def scrape_zoomeye(self, target):
        key = self.config.get("zoomeye")
        if not key: return [], []
        url = f"https://api.zoomeye.org/domain/search?q={target}&type=1"
        resp = self.fetch(url, headers={"API-KEY": key})
        if resp:
            try: return [x.get('name') for x in resp.json().get('list', []) if x.get('name')], []
            except: pass
        return [], []

    def scrape_whoisxmlapi(self, target):
        key = self.config.get("whoisxmlapi")
        if not key: return [], []
        url = f"https://subdomains.whoisxmlapi.com/api/v1?apiKey={key}&domainName={target}"
        resp = self.fetch(url)
        if resp:
            try: return [x.get('domain') for x in resp.json().get('result', {}).get('records', [])], []
            except: pass
        return [], []

    def scrape_bitdiscovery(self, target):
        key = self.config.get("bitdiscovery")
        if not key: return [], []
        url = f"https://api.bitdiscovery.com/v1/endpoint/search?query=domain={target}"
        resp = self.fetch(url, headers={"Authorization": key})
        if resp:
            try: return [x.get('hostname') for x in resp.json().get('nodes', []) if x.get('hostname')], []
            except: pass
        return [], []

    def scrape_hunter(self, target):
        key = self.config.get("hunter")
        if not key: return [], []
        url = f"https://api.hunter.io/v2/domain-search?domain={target}&api_key={key}"
        resp = self.fetch(url)
        if resp:
            try: return [f"{s.get('value')}.{target}" for s in resp.json().get('data', {}).get('subdomains', [])], []
            except: pass
        return [], []

    def scrape_clearbit(self, target):
        key = self.config.get("clearbit")
        if not key: return [], []
        url = f"https://company.clearbit.com/v2/companies/find?domain={target}"
        try:
            resp = self.fetch(url, auth=(key, ''))
            if not resp: return [], []
            data = resp.json()
            subs = data.get('site', {}).get('subdomains', [])
            return [s for s in subs if target in s], []
        except: pass
        return [], []


    def get_favicon_hash(self, target):
        """Native MurmurHash3 calculation for favicon matching."""
        try:
            import mmh3
            url = f"https://{target}/favicon.ico"
            r = self.session.get(url, timeout=10, verify=False)
            if r.status_code == 200:
                favicon = base64.encodebytes(r.content)
                hash_val = mmh3.hash(favicon)
                return hash_val
        except ImportError:
            self.logger.log("Library 'mmh3' missing. Favicon hashing skipped. (pip install mmh3)", "WARN")
        except Exception as e:
            self.logger.log(f"Favicon hash failed: {e}", "ERR")
        return None

    def verify_bucket_access(self, bucket_url):
        """Advanced check for cloud bucket accessibility and directory listing."""
        try:
            # 1. HEAD check for basic access
            r = self.session.head(bucket_url, timeout=5, verify=False)
            status = f"Status {r.status_code}"
            if r.status_code == 200:
                # 2. GET check for Public Listing
                r_get = self.session.get(bucket_url, timeout=5, verify=False)
                if "<Contents>" in r_get.text and "<Key>" in r_get.text:
                    return "Publicly Accessible (200) - LISTING ENABLED 📂"
                return "Publicly Accessible (200)"
            elif r.status_code in [403, 401]: return "Protected (403/401)"
            return status
        except: return "Unknown/Timeout"

    def certificate_pivot(self, ips, target):
        """Pivots from IP addresses to subdomains using tlsx certificates."""
        if not ips: return []
        tlsx_path = find_binary("tlsx")
        if not tlsx_path: return []
        
        self.logger.log(f"Certificate Pivot: Extracting SANs from {len(ips)} IPs...", "INFO")
        hosts = []
        log_dir = os.path.dirname(self.logger.log_file) if self.logger.log_file else os.getcwd()
        ip_file = os.path.join(log_dir, "pivot_ips.txt")
        with open(ip_file, "w") as f: f.write("\n".join(ips))
        
        cmd = f'"{tlsx_path}" -l {ip_file} -san -cn -silent'
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            for line in res.stdout.splitlines():
                clean = line.strip().lower()
                if clean == target or clean.endswith(f".{target}"):
                    hosts.append(clean)
        except: pass
        return list(set(hosts))

    def scrape_webarchive(self, target):
        url = f"https://web.archive.org/cdx/search/xd?url=*.{target}/*&output=json&fl=original&collapse=urlkey"
        try:
            resp = self.fetch(url, timeout=30)
            if resp:
                data = resp.json()
                if not isinstance(data, list): return [], []
                subs = set()
                for item in data[1:]: # Skip header
                    domain = urlparse(item[0]).netloc
                    if ":" in domain: domain = domain.split(":")[0]
                    if target in domain: subs.add(domain)
                return list(subs), []
        except: pass
        return [], []

    def scrape_anubis(self, target):
        url = f"https://jldc.me/anubis/subdomains/{target}"
        resp = self.fetch(url)
        if resp:
             try:
                 data = resp.json()
                 if isinstance(data, list): return data, []
             except: pass
        return [], []

    def scrape_kaeferjaeger(self, target):
        url = f"https://api.kaeferjaeger.gay/v1/subdomains/{target}"
        resp = self.fetch(url)
        if resp:
            try:
                data = resp.json()
                if isinstance(data, dict): return data.get('subdomains', []), []
            except: pass
        return [], []

    def scrape_riddler(self, target):
        url = f"https://riddler.io/search/exportcsv?q=pld:{target}"
        try:
            resp = self.fetch(url)
            if resp: 
                subs = []
                for line in resp.text.splitlines():
                    parts = line.split(',')
                    if len(parts) > 5 and target in line:
                        subs.append(parts[5].strip())
                return list(set(subs)), []
        except: pass
        return [], []


    def scrape_crobat(self, target):
        url = f"https://sonar.omnisint.io/subdomains/{target}"
        resp = self.fetch(url)
        if resp:
            try:
                data = resp.json()
                if isinstance(data, list): return data, []
            except: pass
        return [], []

    def scrape_censys(self, target):
        uid = self.config.get("censys_id")
        secret = self.config.get("censys_secret")
        if not uid or not secret: return [], []
        url = f"https://search.censys.io/api/v1/search/certificates"
        data = {"query": f"parsed.names: {target}", "fields": ["parsed.names", "ip"]}
        subs = set()
        assets = []
        try:
            r = self.post(url, auth=(uid, secret), json=data, timeout=15)
            if r and r.status_code == 200:
                results = r.json().get('results', [])
                for res in results:
                    names = res.get('parsed.names', [])
                    ip = res.get('ip') # Censys often links certificates to IPs
                    for name in names:
                        if name == target or name.endswith(f".{target}"): 
                            subs.add(name)
                            if ip: assets.append({"host": name, "ip": ip, "source": "Censys"})
                return list(subs), assets
        except: pass
        return list(subs), assets

    def scrape_facebook(self, target):
        token = self.config.get("facebook")
        if not token: return [], []
        url = f"https://graph.facebook.com/certificates?query={target}&access_token={token}"
        resp = self.fetch(url)
        if resp:
            try:
                subs = set()
                data = resp.json().get('data', [])
                if not isinstance(data, list): return [], []
                for item in data:
                    domains = item.get('domains', [])
                    if isinstance(domains, list):
                        for domain in domains:
                            if target in domain: subs.add(domain)
                return list(subs), []
            except: pass
        return [], []

# ==============================================================================
#  CORE FUNCTIONS
# ==============================================================================

def check_tool(tool_name):
    """Checks if a tool is available in PATH. Returns Path or None."""
    return shutil.which(tool_name)

def send_notification(webhook_url, message):
    try:
        data = {"content": message} if "discord" in webhook_url else {"text": message}
        requests.post(webhook_url, json=data, timeout=5)
    except: pass



def print_setup_info():
    print(f"\n{Colors.HEADER}=== SETUP & USAGE GUIDE ==={Colors.RESET}")
    print(f"{Colors.BOLD}1. API Key Configuration:{Colors.RESET}")
    print(f"   Run {Colors.CYAN}python3 tools/passive.py --configure{Colors.RESET} to add keys for 25+ sources.")
    print(f"   Supports: Shodan, Virustotal, BinaryEdge, FullHunt, SecurityTrails, etc.")
    
    print(f"\n{Colors.BOLD}2. New Feature Highlights:{Colors.RESET}")
    print(f"   - {Colors.CYAN}--new{Colors.RESET}:     Differential Recon. Only shows subdomains NOT found in the last scan.")
    print(f"   - {Colors.CYAN}--favicon{Colors.RESET}: Favicon Hashing. Pulls icons and pivots to Shodan to find related IP/Hosts.")
    print(f"   - {Colors.CYAN}--org{Colors.RESET}:     Organization Recon. Uses 'Maelstrom' logic (org2asn -> asnmap -> amass).")
    print(f"   - {Colors.CYAN}--validate{Colors.RESET}: Uses 'dnsx' to filter dead/wildcard domains (High Accuracy).")

    print(f"\n{Colors.BOLD}3. Supercharging External Tools:{Colors.RESET}")
    print(f"   Some tools use their own config files. Add keys to:")
    print(f"   - {Colors.CYAN}Subfinder{Colors.RESET}: ~/.config/subfinder/provider-config.yaml")
    print(f"   - {Colors.CYAN}Amass{Colors.RESET}:     ~/.config/amass/config.ini")
    print(f"   - {Colors.CYAN}Chaos{Colors.RESET}:     Set PDCP_API_KEY environment variable")

    print(f"\n{Colors.BOLD}4. Recommended Workflow:{Colors.RESET}")
    print(f"   Standard Scan:  {Colors.CYAN}python3 tools/passive.py -d target.com --validate{Colors.RESET}")
    print(f"   Continuous:     {Colors.CYAN}python3 tools/passive.py -d target.com --new --validate --notify{Colors.RESET}")
    print(f"   Deep Recon:     {Colors.CYAN}python3 tools/passive.py -d target.com --mode high --favicon --org 'Company Name'{Colors.RESET}")
    print("")

def print_recon_advice(logger):
    """Checks for hybrid tools and suggests adding keys for better results."""
    if os.name == 'nt':
        appdata = os.environ.get('APPDATA', os.path.expanduser("~"))
        subfinder_config = os.path.join(appdata, "subfinder", "provider-config.yaml")
        amass_config = os.path.join(appdata, "amass", "config.ini")
    else:
        subfinder_config = os.path.expanduser("~/.config/subfinder/provider-config.yaml")
        amass_config = os.path.expanduser("~/.config/amass/config.ini")
    
    advice = []
    if shutil.which("subfinder") and not os.path.exists(subfinder_config):
        advice.append(f"Subfinder (Path: {subfinder_config})")
    if shutil.which("amass") and not os.path.exists(amass_config):
        advice.append(f"Amass (Path: {amass_config})")
    
    if advice:
        logger.log(f"{Colors.YELLOW}RECON TIP:{Colors.RESET} You can get 3x more results by adding API keys to:", "INFO")
        for a in advice:
            logger.log(f"  -> {a}", "INFO")
        logger.log("Add keys to these files to 'supercharge' your passive recon.", "INFO")

def check_dependencies(missing):
    """Checks for required external binaries."""
    for tool_group in TOOLS.values():
        for tool in tool_group:
            # Check each individual binary required by the tool
            for b in tool.get("bin", []):
                if find_binary(b) is None:
                    if b not in missing: missing.append(b)

def auto_install_tools(missing, logger):
    """Attempts to install missing tools (Go, Pip) automatically."""
    go_tools = {
        "subfinder": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder",
        "katana": "github.com/projectdiscovery/katana/cmd/katana",
        "dnsx": "github.com/projectdiscovery/dnsx/cmd/dnsx",
        "assetfinder": "github.com/tomnomnom/assetfinder",
        "gau": "github.com/lc/gau/v2/cmd/gau",
        "waybackurls": "github.com/tomnomnom/waybackurls",
        "unfurl": "github.com/tomnomnom/unfurl",
        "hakrevdns": "github.com/hakluke/hakrevdns",
        "haktrails": "github.com/hakluke/haktrails",
        "tlsx": "github.com/projectdiscovery/tlsx/cmd/tlsx",
        "cero": "github.com/glebarez/cero",
        "asnmap": "github.com/projectdiscovery/asnmap/cmd/asnmap",
        "cdncheck": "github.com/projectdiscovery/cdncheck/cmd/cdncheck",
        "certinfo": "github.com/projectdiscovery/certinfo/cmd/certinfo",
        "jsubfinder": "github.com/ThreatUnknown/jsubfinder",
        "xsubfind3r": "github.com/hueristiq/xsubfind3r/cmd/xsubfind3r",
        "xurlfind3r": "github.com/hueristiq/xurlfind3r/cmd/xurlfind3r",
        "chaos": "github.com/projectdiscovery/chaos-client/cmd/chaos",
        "subdog": "github.com/Screetsec/subdog",
        "csprecon": "github.com/praveenreghu/csprecon",
        "ipfinder": "github.com/rix4uni/ipfinder",
        "whoxysubs": "github.com/rix4uni/whoxysubs",
        "arinrange": "github.com/rix4uni/arinrange",
        "subwiz": "github.com/rix4uni/subwiz",
        "cspfinder": "github.com/rix4uni/cspfinder",
        "udon": "github.com/rix4uni/udon",
        "spk": "github.com/rix4uni/spk",
        "ipranges": "github.com/rix4uni/ipranges",
        "tldscan": "github.com/rix4uni/tldscan",
        "builtwithsubs": "github.com/rix4uni/builtwithsubs",
        "github-endpoints": "github.com/rix4uni/github-endpoints",
        "haktrailsfree": "github.com/rix4uni/haktrailsfree"
    }
    pipx_tools = {
        "emailfinder": "emailfinder",
        "waymore": "waymore",
        "bbot": "bbot"
    }
    
    logger.log(f"Auto-Installer: Attempting to install {len(missing)} tools...", "INFO")
    installed_now = []
    
    for tool in missing:
        cmd = None
        current_env = os.environ.copy()
        if tool in go_tools:
            if not find_binary("go"):
                logger.log(f"Skipping {tool}: 'go' command missing.", "ERR")
                continue
            logger.log(f"Installing {tool} via go install...", "INFO")
            cmd = f"go install {go_tools[tool]}@latest"
            # Bypass timed-out proxy
            current_env["GOPROXY"] = "direct"
            current_env["GOSUMDB"] = "off"
        elif tool in pipx_tools:
            if not find_binary("pipx"):
                logger.log(f"Skipping {tool}: 'pipx' missing. Recommendation: 'pip install pipx' then 'pipx ensurepath'.", "ERR")
                continue
            logger.log(f"Installing {tool} via pipx...", "INFO")
            cmd = f"pipx install {pipx_tools[tool]} --force"
            
        if cmd:
            try:
                # Use longer timeout for Go/Pipx builds (5 mins)
                proc = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, timeout=300, env=current_env)
                logger.log(f"{tool} installed successfully!", "SUCCESS")
                installed_now.append(tool)
            except subprocess.TimeoutExpired:
                logger.log(f"Installation of {tool} timed out (300s). Command: {cmd}", "ERR")
            except subprocess.CalledProcessError as e:
                err_snippet = e.stderr.strip().split('\n')[-1] if e.stderr else "Unknown error"
                logger.log(f"Failed to install {tool}: {err_snippet}", "ERR")
                logger.log(f"Manual command: {cmd}", "INFO")
        else:
            logger.log(f"No auto-install recipe for {tool}. Skip.", "WARN")
    
    still_missing = [t for t in missing if t not in installed_now]
    if still_missing:
        print(f"{Colors.YELLOW}[!] Remaining missing tools: {', '.join(set(still_missing))}{Colors.RESET}")
        logger.log("TIP: Go tools are installed to ~/go/bin. Pipx tools are isolated in ~/.local/bin.", "INFO")
        logger.log("Make sure your PATH includes these bin folders.", "INFO")
    
    if installed_now:
        logger.log(f"Installed {len(installed_now)} tools. Restart your terminal for changes to take effect.", "SUCCESS")
        print(f"{Colors.GREEN}[+] All core tools found.{Colors.RESET}")

def configure_interactive():
    config = Config()
    print(f"\n{Colors.HEADER}=== API KEY WIZARD ==={Colors.RESET}")
    for key in config.keys:
        current = config.get(key)
        # Mask key for privacy
        display = "****" + current[-4:] if len(current) > 4 else "****" if current else ""
        val = input(f"{key.upper()} [{display}]: ").strip()
        if val: config.keys[key] = val
    config.save_keys()


def find_rapiddns_script():
    candidates = [DEFAULT_RAPIDDNS_SCRIPT, "./run_rapiddns.sh", os.path.expanduser("~/run_rapiddns.sh")]
    for path in candidates:
        if os.path.exists(path): return path
    return None

def run_system_command(cmd, outfile, timeout=None):
    """Runs a shell command. Managed redirection handles stdout."""
    try:
        proc_timeout = (timeout * 60) if timeout else None
        
        # Determine if we need to redirect manually
        if outfile:
            if ">" not in cmd and "-o" not in cmd and "--output" not in cmd:
                # Use "w" with text=True for cross-platform stability
                with open(outfile, "w", encoding="utf-8", errors="ignore") as f:
                    result = subprocess.run(
                        cmd, shell=True, check=False, 
                        stdout=f, stderr=subprocess.PIPE, 
                        text=True, timeout=proc_timeout
                    )
                return True, ""
            else:
                # Command handles its own output
                result = subprocess.run(
                    cmd, shell=True, check=False, 
                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, 
                    text=True, timeout=proc_timeout
                )
        else:
            # No outfile provided, capture output and check return code
            result = subprocess.run(
                cmd, shell=True, check=False, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                text=True, timeout=proc_timeout
            )
        
        if not outfile: return (result.returncode == 0), result.stderr.strip()
        if os.path.exists(outfile) and os.path.getsize(outfile) > 0:
            return True, ""
        return True, "No subdomains found"
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout or 15} minutes"
    except Exception as e:
        return False, str(e)

def print_manual_helpers(target):
    print(f"\n{Colors.HEADER}=== MANUAL HELPER LINKS (Ctrl+Click) ==={Colors.RESET}")
    print(f"{Colors.BOLD}Google Dorks:{Colors.RESET}")
    print(f"  - site:{target} ext:php | ext:aspx | ext:jsp")
    print(f"  - site:{target} \"choose file\"")
    print(f"  - site:s3.amazonaws.com \"{target}\"")
    
    print(f"\n{Colors.BOLD}Manual Crt.sh CLI Extraction (Backup):{Colors.RESET}")
    crt_cmd = f'curl -s "https://crt.sh/?q=%.{target}&output=json" | grep -oE "\\"name_value\\":\\"[^\\"]+\\"" | cut -d\'"\' -f4 | sed "s/\\*\\.//g" | sort -u > crtsh_manual.txt'
    print(f"  {Colors.CYAN}{crt_cmd}{Colors.RESET}")
    
    print("\n" + "="*60)

# ==============================================================================
#  MAIN SCAN LOGIC
# ==============================================================================

def is_valid_domain(domain):
    """Simple regex to prevent shell injection and ensure basic domain format."""
    if not domain: return False
    pattern = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$")
    return bool(pattern.match(domain))

def process_domain(target, args, config, scraper, tools_to_run=None):
    if not is_valid_domain(target):
        print(f"{Colors.RED}[x] Invalid domain format: {target}. Skipping.{Colors.RESET}")
        return

    out_dir = os.path.join(args.output, target)
    os.makedirs(out_dir, exist_ok=True)
    
    # Initialize Logger & Tracker
    logger = DualLogger(os.path.join(out_dir, "scan.log"))
    tracker = ScanTracker()
    
    logger.log(f"Starting passive scan for: {target}", "INFO")
    start_time = time.time()

    # 1. API Key Check
    missing_keys = [k for k, v in config.keys.items() if not v and k not in ["discord_webhook", "slack_webhook"]]
    if len(missing_keys) > 5:
        logger.log(f"Many API keys are missing ({len(missing_keys)}). Results may be limited.", "WARN")
        logger.log("Run 'python3 tools/passive.py --configure' to add them.", "WARN")

    # 2. Scope & Differential Setup
    final_path = os.path.join(out_dir, "all_passive_subs.txt")
    existing_subs = set()
    if args.new:
        if os.path.exists(final_path):
            try:
                with open(final_path, 'r', errors='ignore') as fh:
                    for line in fh:
                        if line.strip(): existing_subs.add(line.strip().lower())
                logger.log(f"Differential Recon enabled. Loaded {len(existing_subs)} existing subdomains.", "INFO")
            except: pass

    exclude_list = set()
    if args.exclude:
        if os.path.exists(args.exclude):
            try:
                with open(args.exclude, 'r', errors='ignore') as fh:
                    for line in fh:
                        if line.strip(): exclude_list.add(line.strip().lower())
                logger.log(f"Scope Exclusion: Loaded {len(exclude_list)} patterns from {args.exclude}.", "INFO")
            except: pass
        else:
            exclude_list = set([x.strip().lower() for x in args.exclude.split(",")])
            if args.exclude and not any(is_valid_domain(x) for x in exclude_list):
                logger.log(f"Scope Exclusion: File not found ({args.exclude}). Using as CLI pattern.", "WARN")
            else:
                logger.log(f"Scope Exclusion: Loaded {len(exclude_list)} patterns from CLI.", "INFO")

    # 3. API Scrapers
    api_results, api_assets = scraper.capture_results(target, tracker, args.mode)

    # 4. Favicon Recon
    if args.favicon:
        logger.log(f"Running Native Favicon Recon for: {target}", "INFO")
        fav_hash = scraper.get_favicon_hash(target)
        if fav_hash:
            logger.log(f"Favicon Hash: {fav_hash}", "SUCCESS")
            shodan_key = config.get("shodan")
            if shodan_key:
                logger.log("Pivoting Shodan using favicon hash...", "INFO")
                shodan_url = f"https://api.shodan.io/shodan/host/search?key={shodan_key}&query=http.favicon.hash:{fav_hash}"
                try:
                    resp = scraper.fetch(shodan_url)
                    if resp:
                        matches = resp.json().get('matches', [])
                        logger.log(f"Shodan pivot found {len(matches)} associated hosts.", "SUCCESS")
                        pivot_file = os.path.join(out_dir, "favicon_pivot_hosts.txt")
                        ips = []
                        with open(pivot_file, "w") as f:
                            for m in matches: 
                                ip = m.get('ip_str')
                                if ip: ips.append(ip)
                                f.write(f"{ip} ({m.get('hostnames', [])})\n")
                        
                        if ips and check_tool("hakrevdns"):
                            logger.log(f"Performing Reverse DNS on {len(ips)} pivot IPs...", "INFO")
                            rdns_out = os.path.join(out_dir, "favicon_pivot_rdns.txt")
                            with open(os.path.join(out_dir, "pivot_ips_temp.txt"), "w") as f:
                                f.write("\n".join(ips))
                            cmd = f"cat {os.path.join(out_dir, 'pivot_ips_temp.txt')} | hakrevdns > {rdns_out}"
                            if os.name == 'nt':
                                cmd = f"type {os.path.join(out_dir, 'pivot_ips_temp.txt')} | hakrevdns > {rdns_out}"
                            run_system_command(cmd, rdns_out)
                    
                    if 'ips' not in locals(): ips = []
                    pivot_hosts = scraper.certificate_pivot(ips, target)
                    if pivot_hosts:
                        logger.log(f"Certificate Pivot found {len(pivot_hosts)} extra subdomains via TLSX!", "SUCCESS")
                        with open(os.path.join(out_dir, "tlsx_pivot_hosts.txt"), "w") as f:
                            f.write("\n".join(pivot_hosts))
                except: pass
        else:
            logger.log("Could not extract/hash favicon. Use 'favinfo' as manual fallback.", "WARN")

    # 5. Cloud Scrapers (Process results)
    for name, data in api_results.items():
        if data:
            # Special parsing: ShodanAPI results are already handled in capture_results
            with open(os.path.join(out_dir, f"{name.lower()}.txt"), 'w') as f:
                f.write('\n'.join(str(d) for d in data if d))
    
    # 6. Binary Tools
    if not tools_to_run: tools_to_run = TOOLS["binary"] # Fallback
        
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.tool_threads) as executor:
        for tool in tools_to_run:
            if "req_key" in tool and not config.get(tool["req_key"]): continue
            if "check_file" in tool and not os.path.exists(os.path.expanduser(tool["check_file"])): continue

            name = tool["name"]
            outfile = os.path.join(out_dir, f"{name.lower().replace(' ', '_')}.txt")
            # Safe formatting to avoid KeyError on typos
            cmd_kwargs = {**config.keys, "target": target, "outfile": outfile, "outdir": out_dir, "timeout": args.amass_timeout}
            try:
                cmd = tool["cmd"].format(**cmd_kwargs)
            except KeyError as e:
                logger.log(f"[{name}] Format error: Missing placeholder {e}. Skipping.", "ERR")
                continue
            
            # Use pre-found bin_path or fallback to cmd name
            bin_to_check = tool.get("bin_path") or tool.get("bin", [""])[0]
            if not bin_to_check or shutil.which(bin_to_check) is None:
                logger.log(f"[{name}] Skipped (Binary not found: {bin_to_check})", "WARN")
                tracker.add_result(name, 0, "SKIPPED", f"Binary missing: {bin_to_check}")
                continue

            # Use absolute path if found
            if "bin_path" in tool and tool["bin_path"]:
                original_bin = tool["bin"][0]
                cmd = cmd.replace(original_bin, f'"{tool["bin_path"]}"', 1)

            logger.log(f"Running binary tool: {name}...", "INFO")
            futures.append(executor.submit(run_system_command, cmd, outfile, None))
            futures[-1].tool_name = name
            futures[-1].outfile = outfile
            futures[-1].start = time.time()

        for future in concurrent.futures.as_completed(futures):
            name = future.tool_name
            duration = time.time() - future.start
            try:
                success, error_msg = future.result()
                
                # Special handling for BBOT (Output is in a specific folder)
                if name == "BBOT" and success:
                    bbot_file = os.path.join(out_dir, "bbot_temp", "output", "subdomains.txt")
                    if os.path.exists(bbot_file):
                        shutil.copy(bbot_file, future.outfile)
                
                count = 0
                if success and os.path.exists(future.outfile):
                    with open(future.outfile, errors='ignore') as fh:
                        count = sum(1 for _ in fh)
                
                tracker.add_result(name, count, "SUCCESS" if success else "FAILED", error_msg, duration)
                if success: logger.log(f"[{name}] Found {count} subdomains", "SUCCESS")
                else: logger.log(f"[{name}] Failed: {error_msg}", "ERR")
            except Exception as e:
                tracker.add_result(name, 0, "CRASHED", str(e), duration)
                logger.log(f"[{name}] Crashed: {e}", "ERR")

    # 7. RapidDNS
    rapiddns_script = find_rapiddns_script()
    if rapiddns_script and args.mode != "low":
        rdns_out = os.path.join(out_dir, "rapiddns.txt")
        # On Windows, we try to run it directly; on Linux, it will use the hashbang.
        cmd = f"{rapiddns_script} -d {target} -o {rdns_out}"
        if os.name != 'nt': # If not Windows, we can use bash explicitly or chmod
            if not os.access(rapiddns_script, os.X_OK): os.chmod(rapiddns_script, 0o755)
            cmd = f"bash {rapiddns_script} -d {target} -o {rdns_out}"
        
        logger.log("Running RapidDNS scraper...", "INFO")
        start = time.time()
        success, err = run_system_command(cmd, rdns_out)
        count = 0
        if success and os.path.exists(rdns_out):
            with open(rdns_out, errors='ignore') as fh:
                count = sum(1 for _ in fh)
        tracker.add_result("RapidDNS", count, "SUCCESS" if success else "FAILED", err, time.time() - start)

    # 8. Org Recon (Maelstrom Logic)
    if args.org:
        logger.log(f"Running Organization Recon for: {args.org}", "INFO")
        org_out = os.path.join(out_dir, "org_recon_summary.txt")
        # Methodology: org2asn -> asnmap -> amass intel
        if check_tool("org2asn"):
            cmd = f"org2asn -org '{args.org}' -silent > {os.path.join(out_dir, 'org_asns.txt')}"
            run_system_command(cmd, os.path.join(out_dir, 'org_asns.txt'))
        
        cmd = f"amass intel -org '{args.org}' -whois -d {target} -o {org_out}"
        run_system_command(cmd, org_out)

    # 9. Merge & Validation
    all_subs = set() 
    infrastructure = {} # Init early to avoid NameError in finally block (Fix 17)
    try:
        logger.log("Merging results...", "INFO")
        
        all_excluded = [
            "all_passive_subs.txt", "summary.txt", "scan.log", "passive_assets.json", 
            "cloud_buckets.txt", "potential_takeovers.txt", "summary.json", "full_report.json",
            "all_passive_subs_validated.json", "new_passive_subs.txt", "favicon_pivot_hosts.txt",
            "favicon_pivot_rdns.txt", "tlsx_pivot_hosts.txt", "org_recon_summary.txt", "org_asns.txt",
            "pivot_ips.txt", "pivot_ips_temp.txt", "org_asns_temp.txt"
        ]
        all_files = [os.path.join(out_dir, f) for f in os.listdir(out_dir) if (f.endswith(".txt") or f.endswith(".json")) and f not in all_excluded]
        
        # Track infra data
        buckets = []
        cdn_file = os.path.join(out_dir, "cdncheck.txt")
        if os.path.exists(cdn_file):
            try:
                with open(cdn_file, errors='ignore') as fh:
                    for line in fh:
                        if ":" in line: infrastructure[line.split(":")[0].strip()] = line.split(":")[1].strip()
            except: pass

        for fpath in all_files:
            try:
                # Robust URL detection (regex for protocol or specific tool names)
                is_url_file = any(x in fpath.lower() for x in ["katana", "waybackurls", "gau", "waymore"])
                # We also check the first few lines for "://"
                if not is_url_file:
                    try:
                        with open(fpath, "r", errors="ignore") as tf:
                            head = [tf.readline() for _ in range(5)]
                            if any("://" in l for l in head): is_url_file = True
                    except: pass
                with open(fpath, 'r', errors='ignore') as fh:
                    for line in fh:
                        clean = line.strip().lower()
                        
                        # Proactive Filtering
                        if should_filter(clean, target, exclude_list): continue
                        
                        # Detect potential cloud buckets
                        if any(x in clean for x in ["s3.amazonaws.com", "storage.googleapis.com", "azureedge.net"]):
                            if clean.startswith("http"): buckets.append(clean)
                            else: buckets.append(f"https://{clean}")
    
                        if is_url_file:
                            try: 
                                clean = urlparse(clean).netloc or clean.split('/')[0]
                                # Strip port if present
                                if ":" in clean: clean = clean.split(":")[0]
                            except: pass
                        
                        clean = clean.replace("http://", "").replace("https://", "").replace("*.", "")
                        # Extract domain from email if present
                        if "@" in clean: clean = clean.split("@")[-1]
                        
                        if clean and (clean == target or clean.endswith(f".{target}")): 
                            all_subs.add(clean)
            except: pass
        
        # --- DIFFERENTIAL CALCULATION ---
        new_subs = all_subs - existing_subs if args.new and existing_subs else all_subs
        
        with open(final_path, 'w') as f:
            f.write('\n'.join(sorted(all_subs)))

        # --- Cloud Bucket Verification ---
        if buckets:
            logger.log(f"Verifying {len(set(buckets))} potential cloud buckets...", "INFO")
            verified_buckets = []
            for b in list(set(buckets))[:20]: # Check top 20 to keep it fast
                status = scraper.verify_bucket_access(b)
                verified_buckets.append(f"{b} -> {status}")
            
            if verified_buckets:
                with open(os.path.join(out_dir, "cloud_buckets.txt"), "w") as bf:
                    bf.write("\n".join(verified_buckets))
                infrastructure["Cloud Buckets Found"] = f"{len(verified_buckets)} found (see cloud_buckets.txt)"
            
        if args.new and existing_subs:
            diff_path = os.path.join(out_dir, "new_passive_subs.txt")
            with open(diff_path, 'w') as f:
                f.write('\n'.join(sorted(new_subs)))
            logger.log(f"Differential Recon: {len(new_subs)} NEW subdomains found.", "SUCCESS")
            final_count = len(new_subs)
        else:
            final_count = len(all_subs)
        
        logger.log(f"Total Unique Subdomains Found: {len(all_subs)}", "SUCCESS")
        
        # --- VALIDATION Phase ---
        if args.validate:
            logger.log("Validating results with dnsx (filtering dead/wildcards)...", "HEADER")
            
            # --- Resolvers (NOW Conditional) ---
            resolvers = manage_resolvers(logger)
            
            if check_tool("dnsx"):
                validated_json = os.path.join(out_dir, "all_passive_subs_validated.json")
                takeover_file = os.path.join(out_dir, "potential_takeovers.txt")
                
                # Standardize on reliable public DNS if resolver list is missing/empty (Fix 9)
                if not resolvers: 
                    resolvers_val = "8.8.8.8,1.1.1.1,9.9.9.9"
                elif os.path.exists(resolvers) and os.path.getsize(resolvers) == 0:
                    resolvers_val = "8.8.8.8,1.1.1.1,9.9.9.9"
                else:
                    resolvers_val = resolvers
                
                # -cname for extraction, -wd for wildcard filtering, -resp for removing non-resolvable
                cmd = f"dnsx -l {final_path} -r {resolvers_val} -wd -resp -cname -json -retry 3 -o {validated_json} -silent"
                try:
                    subprocess.run(cmd, shell=True, check=True)
                    if os.path.exists(validated_json):
                        val_count = 0
                        takeovers = []
                        # Fingerprints for potential takeovers
                        fingerprints = ["s3.amazonaws.com", "herokudns.com", "azurewebsites.net", "wpengine.com", "ghs.google.com", "bitbucket.io", "github.io", "pages.dev"]
                        
                        with open(validated_json, "r", errors="ignore") as jfile:
                            for line in jfile:
                                try:
                                    data = json.loads(line)
                                    val_count += 1
                                    cnames = data.get("cname", [])
                                    if cnames:
                                        for cn in cnames:
                                            if any(fp in cn for fp in fingerprints):
                                                takeovers.append(f"{data.get('host')} -> {cn}")
                                except: pass
                        
                        logger.log(f"Validated {val_count} live domains (JSON saved).", "SUCCESS")
                        if takeovers:
                            logger.log(f"Detected {len(takeovers)} potential subdomain takeovers!", "WARN")
                            with open(takeover_file, "w") as tf:
                                tf.write("\n".join(takeovers))
                            # Store in infrastructure for summary
                            infrastructure["Subdomain Takeover Risk"] = f"{len(takeovers)} found (see potential_takeovers.txt)"
                except Exception as e:
                    logger.log(f"dnsx validation failed: {e}", "ERR")
            else:
                logger.log("dnsx not found. Skipping validation.", "WARN")

        # --- NOTIFICATIONS Phase ---
        if args.notify:
            webhook = config.get("discord_webhook") or config.get("slack_webhook")
            if webhook:
                send_notification(webhook, f"Passive Scan Finished for {target}. Found {final_count} subdomains.")
            else:
                logger.log("No webhook configured for notifications.", "WARN")
                
        # --- CLEANUP Phase ---
        if args.clean:
             logger.log("Cleaning up intermediate files...", "INFO")
             for f in all_files:
                 try: os.remove(f)
                 except: pass
             logger.log("Cleanup complete.", "SUCCESS")

    except Exception as e:
        logger.log(f"Merge/Report failed: {e}", "ERR")
        tracker.add_result("Merge", 0, "CRASHED", str(e))
    
    finally:
        summary_file = tracker.generate_summary(out_dir)
        
        # Asset Mapping Summary
        if api_assets:
            # Enrich assets with cdncheck data if available
            if infrastructure:
                for asset in api_assets:
                    host = asset.get("host")
                    if host in infrastructure:
                        asset["tags"] = asset.get("tags", []) + [infrastructure[host]]
            
            # Global Deduplication
            unified_assets = []
            seen_assets = set()
            for a in api_assets:
                # Dedupe by Host + IP key
                key = f"{a.get('host')}|{a.get('ip')}"
                if key not in seen_assets:
                    unified_assets.append(a)
                    seen_assets.add(key)
            
            asset_path = os.path.join(out_dir, "passive_assets.json")
            with open(asset_path, "w") as f:
                json.dump(unified_assets, f, indent=4)
            logger.log(f"Passive Asset Map saved to: {asset_path} ({len(unified_assets)} assets)", "SUCCESS")
            infrastructure["Passive Assets Found"] = f"{len(unified_assets)} (see passive_assets.json)"

        # Infrastructure Summary
        if infrastructure:
            logger.log("Detected Infrastructure:", "HEADER")
            for k, v in infrastructure.items():
                logger.log(f"  {k}: {v}", "SUCCESS")

        if args.json:
            export_path = os.path.join(out_dir, "full_report.json")
            with open(export_path, "w") as jf:
                json.dump({
                    "target": target,
                    "subdomains": sorted(list(all_subs)),
                    "infrastructure": infrastructure,
                    "tool_stats": tracker.results
                }, jf, indent=4)
            logger.log(f"Exported JSON report to: {export_path}", "SUCCESS")

        logger.log(f"Scan Summary saved to: {summary_file}", "INFO")
        elapsed = time.time() - start_time
        logger.log(f"Scan Finished in {elapsed:.2f} seconds.", "SUCCESS")
        print_manual_helpers(target)

def banner():
    print(f"{Colors.HEADER}")
    print(r"""
    ____  ___   _____ _____ _________    __  __
   / __ \/   | / ___// ___//  _/ | |  / / /_/ /
  / /_/ / /| | \__ \ \__ \ / / | | /| / / __  / 
 / ____/ ___ |___/ /___/ // /  | |/ |/ / /_/ /  
/_/   /_/  |_/____//____/___/  |__/|__/\____/   
                                                
    PASSIVE RECON TOOL v3.46 (Final-Form)
    """)
    print(f"{Colors.CYAN}    [!] TIP: Run 'active.py' NEXT using these results for maximum coverage!{Colors.RESET}")
    print(f"{Colors.YELLOW}    [+] VALIDATION: Use --validate to filter dead domains using dnsx.{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Passive Recon Tool (Refactored)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
EXAMPLES:
  1. Standard Scan (Recommended):
     python tools/passive.py -d example.com --validate
  
  2. Full Automation (Notifications + Cleanup + Validation):
     python tools/passive.py -d example.com --validate --notify --clean

  3. List Scan:
     python tools/passive.py -l targets.txt -o results --mode low
"""
    )
    parser.add_argument("-d", "--domain", help="Target domain")
    parser.add_argument("-l", "--list", help="List of domains")
    parser.add_argument("-o", "--output", default="recon_results", help="Output directory")
    parser.add_argument("--mode", choices=["low", "medium", "high"], default="medium", help="Resource usage mode")
    parser.add_argument("--org", help="Organization name for ASN/WHOIS recon")
    parser.add_argument("--validate", action="store_true", help="Run dnsx validation (Recommended for 100% resolution)")
    parser.add_argument("--notify", action="store_true", help="Send Discord/Slack notification upon completion")
    parser.add_argument("--clean", action="store_true", help="Remove intermediate files after merging")
    parser.add_argument("--new", action="store_true", help="Differential Recon: Only output subdomains NOT seen in previous 'all_passive_subs.txt'")
    parser.add_argument("--favicon", action="store_true", help="Favicon Recon: Extract favicon hash and query Shodan for related infrastructure")
    parser.add_argument("--configure", action="store_true", help="Run interactive API Key Wizard (25+ keys supported)")
    parser.add_argument("--json", action="store_true", help="Export full report as machine-readable JSON")
    parser.add_argument("--resume", action="store_true", help="Batch Resume: Skip targets that already have a successful scan.log")
    parser.add_argument("--install", action="store_true", help="Auto-Installer: Attempt to build missing Go-based tools")
    parser.add_argument("--exclude", help="Scope Exclusion: File or comma-separated list of domains/patterns to filter out")
    parser.add_argument("--info", action="store_true", help="Show setup/usage info")
    parser.add_argument("--check", action="store_true", help="Check dependencies")
    parser.add_argument("--amass-timeout", type=int, default=15, help="Amass timeout (min)")
    parser.add_argument("--tool-threads", type=int, default=5, help="Parallel tools")
    
    args = parser.parse_args()
    
    if args.info:
        banner()
        print_setup_info()
        sys.exit(0)
    if args.configure:
        configure_interactive()
        sys.exit(0)
    if args.check:
        banner()
        missing = []
        check_dependencies(missing)
        if missing:
             print(f"{Colors.RED}[x] Missing Dependencies: {', '.join(set(missing))}{Colors.RESET}")
        else:
             print(f"{Colors.GREEN}[+] All Dependencies Found.{Colors.RESET}")
        sys.exit(0)
    if args.install:
        banner()
        missing = []
        check_dependencies(missing)
        if missing:
            temp_logger = DualLogger()
            auto_install_tools(missing, temp_logger)
        else:
            print(f"{Colors.GREEN}[+] All dependencies already installed.{Colors.RESET}")
        if not args.domain and not args.list:
            sys.exit(0)

    if not args.domain and not args.list:
        parser.print_help(sys.stderr)
        print(f"\n{Colors.YELLOW}[!] No arguments provided. See examples above.{Colors.RESET}")
        sys.exit(1)
        
    banner()
    if args.mode == "low": args.tool_threads = 1
        
    targets = []
    if args.domain: targets.append(args.domain)
    if args.list:
        if os.path.exists(args.list):
            with open(args.list) as f: 
                raw_targets = [x.strip() for x in f if x.strip()]
                # Filter early to avoid log noise
                valid_from_list = [t for t in raw_targets if is_valid_domain(t)]
                targets.extend(valid_from_list)
                if len(valid_from_list) < len(raw_targets):
                    print(f"{Colors.YELLOW}[!] Filtered out {len(raw_targets) - len(valid_from_list)} invalid domains from list.{Colors.RESET}")
            
    print(f"{Colors.BOLD}Mode: {args.mode.upper()} | Targets: {len(targets)} | Output: {args.output}{Colors.RESET}")
    print("-" * 60)
            
    # Move advice to main so it prints once
    logger = DualLogger()
    print_recon_advice(logger)
    
    # --- GLOBAL DEPENDENCY CHECK (Fix 6) ---
    tools_to_run = []
    if args.mode == "low":
        skip_list = ["Amass", "Waymore", "BBOT"]
        tools_to_run = [t for t in TOOLS["binary"] if t["name"] not in skip_list]
    elif args.mode == "high":
        tools_to_run = TOOLS["binary"] + TOOLS["heavy"]
        args.tool_threads = 20
        args.amass_timeout = 30
    else:
        tools_to_run = TOOLS["binary"]
        args.tool_threads = 10

    missing_tools = []
    # Clone to avoid mutating global TOOLS dict in parallel (Thread Safety Fix)
    tools_to_run = copy.deepcopy(tools_to_run)
    
    for tool in tools_to_run:
        for b in tool.get("bin", []):
            path = find_binary(b)
            if path: tool['bin_path'] = path
            else: missing_tools.append(b)
    
    if missing_tools and not args.list:
        logger.log(f"Missing tools: {', '.join(set(missing_tools))}", "WARN")
        choice = input(f"{Colors.YELLOW}[?] Some tools are missing. Proceed? (Y/n): {Colors.RESET}").lower().strip()
        if choice == 'n': sys.exit(0)
    
    config = Config()
    global_scraper = APIScraper(config, logger) # Global session pooling
    
    def run_process(t):
        if args.resume:
            log_file = os.path.join(args.output, t, "scan.log")
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r") as f:
                        if "Scan Summary saved to" in f.read():
                            print(f"{Colors.YELLOW}[!] Target {t} already scanned. Skipping (Resume Mode).{Colors.RESET}")
                            return
                except: pass
        process_domain(t, args, config, global_scraper, tools_to_run=tools_to_run)

    # Batch Processing Parallelism
    if len(targets) > 1:
        target_workers = 2 # Keep it conservative to avoid local exhaustion
        print(f"[*] Processing {len(targets)} targets in parallel ({target_workers} targets at once)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=target_workers) as executor:
            executor.map(run_process, targets)
    else:
        for t in targets:
            run_process(t)

if __name__ == "__main__":
    main()

# ## Audit Trail
# | Date | Source | Changes |
# |---|---|---|
# | 2026-03-10 | Antigravity | v3.31: Audit Fixes (Data integrity overhaul, IntelX activation, UrlScan key integration). |
# | 2026-03-10 | Antigravity | v3.32: Round 11 Audit Fixes (Key masking in wizard, Quake guard, section numbering tune-up). |
# | 2026-03-10 | Antigravity | v3.33: Round 12 Audit Fixes (post() helper with retry/429 logic, fixed list counting UX bug). |
# | 2026-03-10 | Antigravity | v3.34: Round 14 Audit Fixes (9 missing key guards, re-numbered all scan sections 1-9, PEP 8 fixes). |
# | 2026-03-10 | Antigravity | v3.35: Round 15 Audit Fixes (Anubis/Crobat type checking, refined run_system_command exit codes). |
# | 2026-03-10 | Antigravity | v3.36: Round 16 Audit Fixes (Kaeferjaeger/HackerTarget hardening, legacy comment cleanup). |
# | 2026-03-10 | Antigravity | v3.37: Round 17 Audit Fixes (Restored critical email extraction regression, CertSpotter hardening). |
# | 2026-03-10 | Antigravity | v3.38: Round 18 Final Fixes (WebArchive type guard, last legacy comments cleaned). 86 bugs total. |
# | 2026-03-10 | Antigravity | v3.39: UX Fix (Enabled --install as a standalone command without requiring -d). |
# | 2026-03-10 | Antigravity | v3.40: Installer Expansion (Added 10+ new recipes, improved path awareness & feedback). |
# | 2026-03-10 | Antigravity | v3.41: Installer UX (Display manual install command upon failure). |
# | 2026-03-10 | Antigravity | v3.42: Installer Expansion (Added rix4uni ecosystem: ipfinder, arinrange, subwiz, udon, spk, etc.). |
# | 2026-03-11 | Antigravity | v3.43: Installer Perfection (Fixed jsubfinder typo, added missing cspfinder recipe). |
# | 2026-03-11 | Antigravity | v3.44: Installer Categories (Split Go/Pip, added stderr reporting, 300s build timeouts). |
# | 2026-03-11 | Antigravity | v3.45: Installer Resilience (GOPROXY=direct fallback for timeouts, --break-system-packages for Pip). |
# | 2026-03-11 | Antigravity | v3.46: Installer Safety (Migrated Python tools to pipx for isolated installation). |
