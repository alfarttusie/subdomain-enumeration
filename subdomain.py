import subprocess
import os
import requests
import re
import concurrent.futures
import argparse
import pyfiglet
import shutil


class subdomain:
    url = ''
    subs = []

    @property
    def Logo(self):
        figlet = pyfiglet.Figlet(font="banner")
        text_art = figlet.renderText("subdomain enumeration")
        terminal_width = shutil.get_terminal_size().columns
        centered_text_art = "\n".join(
            line.center(terminal_width) for line in text_art.split("\n")
        )

        return centered_text_art

    def args_handler(self):
        try:
            parser = argparse.ArgumentParser(description="subdomain finder")  # noQa
            parser.add_argument('-d', '--domain name', required=True, help="website url")  # noQa
            parser.add_argument('-t', '--threads', type=int, default=4, help="Number of threads (default: 4)")  # noQa
            args = parser.parse_args()
            self.url = args.domain
            self.threads = int(args.threads)
        except Exception as error:
            print(error)

    @property
    def cleaned(self):
        domain = self.url
        if domain.startswith("http"):
            domain = domain.split("//")[1]
        if domain.startswith("www"):
            domain = domain.split(".")
            domain.remove("www")
            domain = '.'.join(map(str, domain))
        return domain

    def __init__(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.Logo)
        self.args_handler()
        print("running... amass")
        # self.amass()
        print("running... crt.sh")
        self.crtsh()
        print("running... subfinder")
        self.subfinder()
        print("running... dnsgen")
        self.dnsgen()
        print("running... assetfinder")
        self.assetfinder()
        print("running... findomain")
        self.findomain()
        temp = self.subs
        self.subs = []
        for subdomain in temp:
            if subdomain.startswith("www"):
                subdomain = subdomain.replace("www.", '')
            self.subs.append(subdomain)
        del (temp)
        unique_items = set(self.subs)
        self.subs = list(unique_items)
        print("last checking...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executer:
            executer.map(self.sendRequest, self.subs)

    def amass(self):
        try:
            command = ["amass", "enum", "-d", self.cleaned]
            result = subprocess.run(command, capture_output=True, text=True)  # noQa
            for sub in result.stdout.splitlines():
                self.subs.append(sub)
        except:
            print("amass Not Found")

    def crtsh(self):
        headers = {
            'Host': 'crt.sh',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Referer': 'https://crt.sh/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1'}

        sendRequset = requests.get(
            f"https://crt.sh/?q={self.cleaned}", headers=headers)
        if sendRequset.status_code == 200:
            matches = re.findall(
                r'<TD>([^<]+)</TD>', sendRequset.text, flags=re.IGNORECASE)
            for line in matches:
                self.subs.append(line)

    def subfinder(self):
        try:
            command = ["subfinder", "-d", self.cleaned]
            result = subprocess.run(command, capture_output=True, text=True)  # noQa
            for sub in result.stdout.splitlines():
                self.subs.append(sub)
        except:
            print("subfinder Not Found")

    def dnsgen(self):
        try:
            sublist = "\n".join(str(item) for item in self.subs)
            command = ['dnsgen', '-f', '-']
            output = subprocess.run(command, input=sublist,
                                    capture_output=True, text=True, check=True)
            for sub in output.stdout.splitlines():
                self.subs.append(sub)
        except:
            print("dnsgen Not Found")

    def assetfinder(self):
        try:
            command = ['assetfinder', self.cleaned]
            output = subprocess.run(command, capture_output=True, text=True)
            for sub in output.stdout.splitlines():
                self.subs.append(sub)
        except:
            print("assetfinder Not Found")

    def findomain(self):
        try:
            command = ['findomain', '-t', self.url, '-q']
            output = subprocess.run(command, capture_output=True, text=True)
            for sub in output.stdout.splitlines():
                self.subs.append(sub)
        except:
            print("findomain Not Found")

    def sendRequest(self, sub):
        try:
            try:
                headers = {
                    'Host': f'{sub}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1'
                }

                response = requests.get(f"http://{sub}", headers=headers, timeout=4)  # noQa
                if response.status_code == 200:
                    self.writeFile(str(sub)+"\n")
                    print("Found ==> ", sub)
                    return True
                else:
                    return False
            except:
                return False
        except Exception as error:
            print(error)
            return

    def writeFile(self, text):
        file = open(f"{self.cleaned}.txt", '+a')
        file.write(text)


subdomain()
