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
FEEDS = [
    {"name": "Krebs on Security",   "url": "https://krebsonsecurity.com/feed/",                     "category": "Investigations"},
    {"name": "BleepingComputer",    "url": "https://www.bleepingcomputer.com/feed/",                "category": "Breaking"},
    {"name": "The Hacker News",     "url": "https://feeds.feedburner.com/TheHackersNews",           "category": "Breaking"},
    {"name": "Dark Reading",        "url": "https://www.darkreading.com/rss.xml",                   "category": "Analysis"},
    {"name": "SANS ISC",            "url": "https://isc.sans.edu/rssfeed_full.xml",                 "category": "Advisories"},
    {"name": "The Record",          "url": "https://therecord.media/feed/",                         "category": "Analysis"},
    {"name": "Schneier on Security","url": "https://www.schneier.com/feed/atom/",                   "category": "Analysis"},
    {"name": "Google Security",     "url": "https://security.googleblog.com/feeds/posts/default",   "category": "Research"},
    {"name": "Microsoft Security",  "url": "https://www.microsoft.com/en-us/security/blog/feed/",   "category": "Research"},
    {"name": "Unit 42",             "url": "https://unit42.paloaltonetworks.com/feed/",             "category": "Research"},
    {"name": "Cisco Talos",         "url": "https://blog.talosintelligence.com/rss/",               "category": "Research"},
    {"name": "Securelist",          "url": "https://securelist.com/feed/",                          "category": "Research"},
    {"name": "WeLiveSecurity",      "url": "https://www.welivesecurity.com/en/rss/feed/",           "category": "Analysis"},
    {"name": "SecurityWeek",        "url": "https://www.securityweek.com/feed/",                    "category": "Breaking"},
    {"name": "Graham Cluley",       "url": "https://grahamcluley.com/feed/",                        "category": "Analysis"},
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
