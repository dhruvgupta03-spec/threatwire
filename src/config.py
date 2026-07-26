"""Central configuration: the newsroom masthead and the wire sources.

Add or remove feeds here — everything downstream adapts automatically.
"""

# --- Masthead / site identity -------------------------------------------------
SITE = {
    "name": "THREATWIRE",
    "tagline": "Threat Intelligence Daily",
    "motto": "The world's cyber threats, clipped and ranked — updated on the loop.",
    "base_url": "",  # set to your full site URL, e.g. "https://threatwire.news"
    "domain": "",    # set a bare custom domain (e.g. "threatwire.news") to emit a CNAME file
}

# How many stories to render on the front page.
MAX_ITEMS = 90
# Only keep items newer than this many days (keeps the front page "latest").
MAX_AGE_DAYS = 21

# --- The wire: curated threat-intelligence sources ----------------------------
# name        : shown as the byline/source
# url         : RSS/Atom feed
# category    : coarse section hint used for grouping
# group: "news" (media wires) · "vendor" (top-player research labs) · "ai" (niche AI security)
FEEDS = [
    {"name": "Krebs on Security",   "url": "https://krebsonsecurity.com/feed/",                     "category": "Investigations", "group": "news"},
    {"name": "BleepingComputer",    "url": "https://www.bleepingcomputer.com/feed/",                "category": "Breaking",       "group": "news"},
    {"name": "The Hacker News",     "url": "https://feeds.feedburner.com/TheHackersNews",           "category": "Breaking",       "group": "news"},
    {"name": "Dark Reading",        "url": "https://www.darkreading.com/rss.xml",                   "category": "Analysis",       "group": "news"},
    {"name": "SANS ISC",            "url": "https://isc.sans.edu/rssfeed_full.xml",                 "category": "Advisories",     "group": "news"},
    {"name": "The Record",          "url": "https://therecord.media/feed/",                         "category": "Analysis",       "group": "news"},
    {"name": "Schneier on Security","url": "https://www.schneier.com/feed/atom/",                   "category": "Analysis",       "group": "news"},
    {"name": "SecurityWeek",        "url": "https://www.securityweek.com/feed/",                    "category": "Breaking",       "group": "news"},
    {"name": "Graham Cluley",       "url": "https://grahamcluley.com/feed/",                        "category": "Analysis",       "group": "news"},
    # Top-player vendor research labs
    {"name": "Google Security",     "url": "https://security.googleblog.com/feeds/posts/default",   "category": "Research",       "group": "vendor"},
    {"name": "Microsoft Security",  "url": "https://www.microsoft.com/en-us/security/blog/feed/",   "category": "Research",       "group": "vendor"},
    {"name": "Unit 42",             "url": "https://unit42.paloaltonetworks.com/feed/",             "category": "Research",       "group": "vendor"},
    {"name": "Cisco Talos",         "url": "https://blog.talosintelligence.com/rss/",               "category": "Research",       "group": "vendor"},
    {"name": "Securelist",          "url": "https://securelist.com/feed/",                          "category": "Research",       "group": "vendor"},
    {"name": "WeLiveSecurity",      "url": "https://www.welivesecurity.com/en/rss/feed/",           "category": "Analysis",       "group": "vendor"},
    {"name": "CrowdStrike",         "url": "https://www.crowdstrike.com/blog/feed/",                "category": "Research",       "group": "vendor"},
    {"name": "SentinelOne Labs",    "url": "https://www.sentinelone.com/labs/feed/",                "category": "Research",       "group": "vendor"},
    {"name": "Check Point Research","url": "https://research.checkpoint.com/feed/",                 "category": "Research",       "group": "vendor"},
    {"name": "Rapid7",              "url": "https://www.rapid7.com/blog/rss/",                      "category": "Research",       "group": "vendor"},
    # Niche AI-security intel
    {"name": "Prompt Security",     "url": "https://www.prompt.security/blog/rss.xml",              "category": "AI Security",    "group": "ai"},
    {"name": "Legit Security",      "url": "https://www.legitsecurity.com/blog/rss.xml",            "category": "AI Security",    "group": "ai"},
    {"name": "OWASP GenAI",         "url": "https://genai.owasp.org/feed/",                         "category": "AI Security",    "group": "ai"},
]

# Roster for the "Product of the Day" feature — one is featured per day (rotates by
# day-of-year) and replaced the next day. Curated; the LLM (if enabled) expands the
# blurb into a full deep-dive.
PRODUCTS = [
    {"name": "CrowdStrike Falcon", "vendor": "CrowdStrike", "category": "Endpoint / XDR", "url": "https://www.crowdstrike.com/platform/",
     "one_liner": "Cloud-native endpoint protection built around a single lightweight agent.",
     "why": "Popularized the EDR-as-a-service model; its threat graph correlates trillions of events to catch behavior signatures miss.",
     "capabilities": ["Behavioral EDR/XDR", "Managed threat hunting (OverWatch)", "Identity threat detection", "Single-agent architecture"]},
    {"name": "Microsoft Defender XDR", "vendor": "Microsoft", "category": "XDR / SIEM", "url": "https://www.microsoft.com/security/business/microsoft-defender-xdr",
     "one_liner": "Unified pre- and post-breach defense across endpoints, identities, email, and cloud apps.",
     "why": "Its reach across the Microsoft estate gives unmatched telemetry; deeply tied to Entra identity signals.",
     "capabilities": ["Cross-domain correlation", "Automated attack disruption", "Copilot for Security", "Native M365 integration"]},
    {"name": "Palo Alto Cortex XDR", "vendor": "Palo Alto Networks", "category": "XDR", "url": "https://www.paloaltonetworks.com/cortex/cortex-xdr",
     "one_liner": "Analytics-driven detection stitching endpoint, network, and cloud data.",
     "why": "Pioneered the 'XDR' category; strong at reducing alert fatigue via causality chains.",
     "capabilities": ["Behavioral analytics", "Root-cause analysis", "Managed detection (Unit 42)", "Host firewall & disk encryption"]},
    {"name": "SentinelOne Singularity", "vendor": "SentinelOne", "category": "Endpoint / XDR", "url": "https://www.sentinelone.com/",
     "one_liner": "Autonomous endpoint protection with on-agent AI and one-click rollback.",
     "why": "On-device models allow detection/response without cloud round-trips; ransomware rollback is a standout.",
     "capabilities": ["On-agent AI static/behavioral", "Storyline attack visualization", "Ransomware rollback", "Purple AI analyst"]},
    {"name": "Wiz", "vendor": "Wiz", "category": "Cloud Security (CNAPP)", "url": "https://www.wiz.io/",
     "one_liner": "Agentless cloud security that graphs toxic combinations of risk.",
     "why": "Redefined CNAPP with an agentless graph; fastest enterprise software to $100M ARR.",
     "capabilities": ["Agentless scanning", "Security graph / attack paths", "CSPM + CWPP + CIEM", "Cloud detection & response"]},
    {"name": "Zscaler Zero Trust Exchange", "vendor": "Zscaler", "category": "SSE / Zero Trust", "url": "https://www.zscaler.com/",
     "one_liner": "Cloud-delivered secure access that never puts users on the network.",
     "why": "Brokered zero-trust access removes the attack surface of VPNs and public-facing apps.",
     "capabilities": ["Secure Web Gateway", "Zero Trust Network Access", "Cloud DLP", "Inline threat inspection"]},
    {"name": "Okta", "vendor": "Okta", "category": "Identity (IAM)", "url": "https://www.okta.com/",
     "one_liner": "Identity as the control plane for workforce and customer access.",
     "why": "Identity is the modern perimeter; Okta is the neutral hub — and thus a prime attacker target.",
     "capabilities": ["SSO & MFA", "Adaptive/risk-based auth", "Lifecycle management", "Identity threat protection"]},
    {"name": "Snyk", "vendor": "Snyk", "category": "Developer / AppSec", "url": "https://snyk.io/",
     "one_liner": "Developer-first security across code, dependencies, containers, and IaC.",
     "why": "Shifts security left into the IDE and PR, where fixes are cheapest.",
     "capabilities": ["SCA & SAST", "Container & IaC scanning", "Fix PRs", "Developer workflow integration"]},
    {"name": "Cloudflare", "vendor": "Cloudflare", "category": "Edge / WAF / DDoS", "url": "https://www.cloudflare.com/",
     "one_liner": "A global edge network that absorbs attacks before they reach origin.",
     "why": "Sees a huge slice of internet traffic; its scale turns DDoS and bot defense into a utility.",
     "capabilities": ["WAF & DDoS mitigation", "Bot management", "Zero Trust (Access/Gateway)", "Global anycast network"]},
    {"name": "Tenable", "vendor": "Tenable", "category": "Exposure / Vuln Management", "url": "https://www.tenable.com/",
     "one_liner": "Find, prioritize, and close exposures across the modern attack surface.",
     "why": "Nessus set the standard for vuln scanning; now expanding to unified exposure management.",
     "capabilities": ["Vulnerability management", "Attack surface management", "Cloud & OT/IoT coverage", "Risk-based prioritization"]},
    {"name": "Splunk", "vendor": "Cisco", "category": "SIEM / Observability", "url": "https://www.splunk.com/",
     "one_liner": "Search and correlate machine data at scale for security and ops.",
     "why": "The reference SIEM for many SOCs; now part of Cisco's security fabric.",
     "capabilities": ["SIEM (Enterprise Security)", "SOAR", "UEBA", "Massive-scale log analytics"]},
    {"name": "Abnormal Security", "vendor": "Abnormal", "category": "Email Security", "url": "https://abnormalsecurity.com/",
     "one_liner": "Behavioral AI that stops socially-engineered email attacks.",
     "why": "Models normal communication patterns to catch BEC and account takeover other filters miss.",
     "capabilities": ["Behavioral BEC detection", "Account takeover protection", "Vendor fraud defense", "API-based, no MX change"]},
    {"name": "HiddenLayer", "vendor": "HiddenLayer", "category": "AI / ML Security", "url": "https://hiddenlayer.com/",
     "one_liner": "Security for machine-learning models against adversarial and theft attacks.",
     "why": "As AI ships to production, the models themselves become an attack surface — a frontier few cover.",
     "capabilities": ["Model scanning", "Adversarial ML detection", "AI supply-chain security", "Model theft protection"]},
    {"name": "Lakera", "vendor": "Lakera", "category": "AI / LLM Security", "url": "https://www.lakera.ai/",
     "one_liner": "Real-time guardrails against prompt injection and LLM abuse.",
     "why": "Prompt injection is the top LLM risk; Lakera productized defenses trained on a huge attack corpus.",
     "capabilities": ["Prompt-injection defense", "PII / data-leak filtering", "Content moderation", "LLM red-teaming (Gandalf)"]},
]

# --- Ranking heuristics -------------------------------------------------------
# Higher weight = pushed toward the lead. Matched against title + summary.
SEVERITY = {
    3: [  # Critical
        "zero-day", "zero day", "0-day", "actively exploited", "in the wild",
        "emergency directive", "critical vulnerability", "unauthenticated remote",
        "cvss 10", "cvss 9", "mass exploitation", "wormable",
    ],
    2: [  # High
        "ransomware", "data breach", "breach", "exploited", "backdoor",
        "supply chain", "nation-state", "apt", "malware", "data leak",
        "espionage", "cyberattack", "compromised",
    ],
    1: [  # Notable (default for security news)
        "vulnerability", "cve-", "patch", "phishing", "flaw", "leak", "hacked",
    ],
}

# Topic tags surfaced as kickers/labels.
TOPICS = {
    "Ransomware":    ["ransomware", "extortion", "lockbit", "blackcat", "alphv", "ryuk"],
    "Zero-Day":      ["zero-day", "zero day", "0-day", "actively exploited"],
    "Data Breach":   ["breach", "data leak", "exposed", "leaked", "stolen data"],
    "Nation-State":  ["nation-state", "apt", "espionage", "state-sponsored", "china", "russia", "north korea", "iran"],
    "Vulnerability": ["vulnerability", "cve-", "flaw", "patch", "exploit"],
    "Malware":       ["malware", "trojan", "backdoor", "botnet", "loader", "stealer"],
    "Phishing":      ["phishing", "smishing", "social engineering", "credential"],
    "Supply Chain":  ["supply chain", "npm", "pypi", "dependency", "package"],
    "Cloud":         ["cloud", "aws", "azure", "kubernetes", "s3 bucket"],
    "AI Security":   ["ai ", "artificial intelligence", "llm", "prompt injection", "deepfake"],
    "Policy":        ["regulation", "policy", "sanction", "law", "gdpr", "compliance"],
}
