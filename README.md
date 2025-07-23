# Subdomain Enumeration

![banner](https://img.shields.io/badge/Tool-Subdomain%20Enum-blue.svg)
![python](https://img.shields.io/badge/Python-3.6+-brightgreen.svg)
![license](https://img.shields.io/badge/License-MIT-lightgrey.svg)

> 🕵️‍♂️ A powerful and automated subdomain enumeration tool that leverages multiple OSINT and recon tools to gather, filter, and validate live subdomains for any target domain.

---

## 🔍 Overview

**Subdomain Enumeration** is a Python-based reconnaissance tool that automates the process of collecting subdomains from various sources and tools, then filters and validates them using DNS and HTTP probes.

It supports integration with a wide range of enumeration tools like:
- `amass`, `subfinder`, `assetfinder`, `findomain`
- `gau`, `waybackurls`, `hakrawler`
- `sublist3r`, `theHarvester`, `crt.sh`
- Validation via `dnsx` or fallback HTTP probing

---

## ⚙️ Features

- 🔎 Passive and OSINT-based subdomain collection
- 🧪 Live subdomain validation with `dnsx` or `requests`
- 🧵 Multithreaded HTTP probing for fast checking
- 💾 Saves results to a clean, deduplicated `.txt` file
- ✅ Automatically detects installed tools
- 🎨 Stylish CLI banner using `pyfiglet`

---

## 🚀 Installation

1. **Clone the repo:**

```bash
git clone https://github.com/yourusername/subdomain-enumeration.git
cd subdomain-enumeration
```

2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

3. **Ensure external tools are installed:**

Install any of the following you want the tool to use:

```bash
# Examples:
sudo apt install amass subfinder dnsx assetfinder findomain sublist3r
go install github.com/hakluke/hakrawler@latest
go install github.com/tomnomnom/gau@latest
```

> ✅ The script will detect which tools are available on your system.

---

## 🧪 Usage

```bash
python sub_enum.py -d example.com
```

### Options:

| Option | Description | Default |
|--------|-------------|---------|
| `-d`, `--domain` | Target domain to enumerate | **Required** |
| `-t`, `--threads` | Number of threads for HTTP probing | 20 |

---

## 📦 Output

- All **live subdomains** will be saved to a file named:

```
example.com.txt
```

---

## 🧰 Supported Tools

| Tool         | Usage |
|--------------|-------|
| amass        | Passive enumeration |
| subfinder    | Passive OSINT |
| assetfinder  | Subdomain enumeration |
| findomain    | Fast subdomain finding |
| gau          | Historical URLs (extract subdomains) |
| waybackurls  | Archive URLs |
| hakrawler    | Web crawling for URLs |
| sublist3r    | Traditional OSINT |
| theHarvester | Passive information gathering |
| crt.sh       | Public certificate database |
| dnsx         | Live subdomain validation |

---

## 🛡 Disclaimer

This tool is intended **only for educational and authorized penetration testing** purposes. Unauthorized usage against domains you don't own is strictly prohibited.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📷 Screenshot

<p align="center">
  <img src="https://alfarttusie.com/uploads/Screenshot.png" width="100%">
</p>

---

Happy Hunting! 🕵️‍♀️
