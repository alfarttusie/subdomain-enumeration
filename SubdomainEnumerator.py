#!/usr/bin/env python3
import os
import subprocess
import requests
import re
import argparse
import shutil
import concurrent.futures
from urllib.parse import urlparse
from pyfiglet import Figlet
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


class SubdomainEnum:
    def __init__(self):
        self.subs = set()
        self.live_subs = set()
        self.detect_tools()
        self.handle_args()
        self.domain_cleaned = self.clean_domain(self.domain)
        self.output_file = f"{self.domain_cleaned}.txt"
        self.show_banner()
        self.run()

    def show_banner(self):
        os.system("cls" if os.name == "nt" else "clear")
        fig = Figlet(font='slant')
        print(fig.renderText("SubEnum"))

    def handle_args(self):
        parser = argparse.ArgumentParser(
            description="Subdomain Enumeration Tool")
        parser.add_argument("-d", "--domain", required=True,
                            help="Target domain (e.g. example.com)")
        parser.add_argument("-t", "--threads", type=int,
                            default=20, help="Thread count (default: 20)")
        args = parser.parse_args()
        self.domain = args.domain.strip()
        self.threads = args.threads

    def detect_tools(self):
        self.tools = {}
        tools = [
            'amass', 'subfinder', 'assetfinder', 'findomain',
            'gau', 'waybackurls', 'hakrawler', 'dnsx',
            'sublist3r', 'theHarvester'
        ]
        for tool in tools:
            self.tools[tool] = shutil.which(tool) is not None

    def clean_domain(self, domain):
        parsed = urlparse(domain if domain.startswith(
            "http") else f"http://{domain}")
        domain = parsed.netloc or parsed.path
        if domain.startswith("www."):
            domain = domain[4:]
        return domain

    def run(self):
        print("[*] Gathering subdomains...")
        self.run_tools()

        print(
            f"[*] {len(self.subs)} raw subdomains collected. Filtering and deduplicating...")
        self.subs = set(self.filter_valid_subs(self.subs))

        print(
            f"[*] {len(self.subs)} unique subdomains. Validating with dnsx if available...")
        if self.tools['dnsx']:
            self.validate_with_dnsx()
        else:
            self.validate_with_http()

        print(f"[✓] {len(self.live_subs)} live subdomains found.")
        self.save_results()

    def run_tools(self):
        if self.tools['amass']:
            self.run_cmd(["amass", "enum", "-passive", "-d",
                         self.domain_cleaned], label="amass")
        if self.tools['subfinder']:
            self.run_cmd(["subfinder", "-d", self.domain_cleaned,
                         "-silent"], label="subfinder")
        if self.tools['assetfinder']:
            self.run_cmd(["assetfinder", "--subs-only",
                         self.domain_cleaned], label="assetfinder")
        if self.tools['findomain']:
            self.run_cmd(["findomain", "-t", self.domain_cleaned,
                         "-q"], label="findomain")
        if self.tools['gau']:
            self.run_cmd(["gau", "--subs", self.domain_cleaned],
                         label="gau", extract_urls=True)
        if self.tools['waybackurls']:
            self.run_cmd(["waybackurls"], input_text=self.domain_cleaned,
                         label="waybackurls", extract_urls=True)
        if self.tools['hakrawler']:
            self.run_cmd(["hakrawler", "-all", "-plain", "-subs", "-insecure",
                         "-domain", self.domain_cleaned], label="hakrawler", extract_urls=True)
        if self.tools['sublist3r']:
            self.run_cmd(["sublist3r", "-d", self.domain_cleaned,
                         "-o", "/tmp/subs_tmp.txt"], label="sublist3r")
            if os.path.exists("/tmp/subs_tmp.txt"):
                with open("/tmp/subs_tmp.txt") as f:
                    self.subs.update(line.strip()
                                     for line in f if self.domain_cleaned in line)
                os.remove("/tmp/subs_tmp.txt")
        if self.tools['theHarvester']:
            self.run_cmd(["theHarvester", "-d", self.domain_cleaned, "-b",
                         "all", "-f", "/tmp/harvest.html"], label="theHarvester")
            if os.path.exists("/tmp/harvest.html"):
                with open("/tmp/harvest.html") as f:
                    for line in f:
                        match = re.findall(
                            rf"[\w\.-]*\.{re.escape(self.domain_cleaned)}", line)
                        self.subs.update(match)

        self.get_from_crtsh()

    def run_cmd(self, cmd, label=None, input_text=None, extract_urls=False):
        try:
            result = subprocess.run(
                cmd,
                input=input_text,
                text=True,
                capture_output=True,
                timeout=90
            )
            output = result.stdout.strip().splitlines()
            if extract_urls:
                for line in output:
                    hostname = urlparse(line).hostname
                    if hostname and self.domain_cleaned in hostname:
                        self.subs.add(hostname.strip())
            else:
                for line in output:
                    if self.domain_cleaned in line:
                        self.subs.add(line.strip())
            if label:
                print(f"[+] {label} ✅ ({len(output)} lines)")
        except Exception as e:
            print(f"[-] {label} failed: {e}")

    def get_from_crtsh(self):
        print("[*] Fetching from crt.sh ...")
        try:
            r = requests.get(
                f"https://crt.sh/?q=%25.{self.domain_cleaned}&output=json", timeout=10)
            if r.status_code == 200:
                for item in r.json():
                    entries = item.get("name_value", "").splitlines()
                    for sub in entries:
                        if self.domain_cleaned in sub:
                            self.subs.add(sub.strip())
        except Exception as e:
            print(f"[-] crt.sh failed: {e}")

    def filter_valid_subs(self, subs):
        valid = set()
        for sub in subs:
            sub = sub.lower().strip()
            if "*" in sub or not self.domain_cleaned in sub:
                continue
            if sub.startswith("www."):
                sub = sub[4:]
            valid.add(sub)
        return valid

    def validate_with_dnsx(self):
        try:
            proc = subprocess.run(
                ["dnsx", "-silent"],
                input="\n".join(self.subs),
                text=True,
                capture_output=True
            )
            self.live_subs = set(proc.stdout.strip().splitlines())
        except Exception as e:
            print(f"[!] dnsx error: {e}")

    def validate_with_http(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.check_http, self.subs)

    def check_http(self, sub):
        for proto in ["http://", "https://"]:
            try:
                url = proto + sub
                r = requests.get(url, timeout=4, verify=True)
                if r.status_code < 500:
                    self.live_subs.add(sub)
                    print(f"[LIVE] {url}")
                    return
            except:
                continue

    def save_results(self):
        if not self.live_subs:
            print("[-] No live subdomains found.")
            return
        with open(self.output_file, "w") as f:
            for sub in sorted(self.live_subs):
                f.write(sub + "\n")
        print(f"[✓] Results saved to: {self.output_file}")


if __name__ == "__main__":
    SubdomainEnum()
