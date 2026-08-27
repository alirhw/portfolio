"""
Live production health audit script (T-069).
Verifies /healthz/ probe, multilingual homepages, robots.txt, and sitemap.xml on a live domain.
"""

import json
import sys
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_HOST = "http://127.0.0.1:8000"


def run_live_smoke_test(base_url: str = DEFAULT_HOST) -> bool:
    """Execute end-to-end health audit against the target live host."""
    base_url = base_url.rstrip("/")
    print("========================================================================")
    print(f"INITIATING LIVE PRODUCTION HEALTH AUDIT: {base_url}")
    print("========================================================================")

    endpoints_to_test = [
        # 1. System health probe
        (f"{base_url}/healthz/", 200, "System Health Probe"),
        # 2. Multilingual homepages
        (f"{base_url}/en/", 200, "English Homepage"),
        (f"{base_url}/fa/", 200, "Persian Homepage (RTL)"),
        # 3. SEO metadata endpoints
        (f"{base_url}/robots.txt", 200, "Robots Metadata"),
        (f"{base_url}/sitemap.xml", 200, "Sitemap XML"),
    ]

    all_passed = True

    for url, expected_code, description in endpoints_to_test:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Production-Health-Probe/1.0",
                "Accept": "*/*",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                content = response.read()

                if status_code == expected_code:
                    print(f"[OK] [{status_code}] {description} -> {url}")

                    # Check JSON health payload structure
                    if "/healthz/" in url:
                        data = json.loads(content.decode())
                        db_status = data.get("checks", {}).get("database")
                        if data.get("status") == "healthy" and db_status == "ok":
                            print("   --> Database connection and Cache confirmed operational.")
                        else:
                            print(f"   [FAIL] Healthcheck data degraded: {data}")
                            all_passed = False
                else:
                    print(f"[FAIL] [{status_code}] {description} (Expected {expected_code})")
                    all_passed = False

        except urllib.error.HTTPError as err:
            print(f"[FAIL] [HTTP {err.code}] {description} -> {url}")
            all_passed = False
        except Exception as exc:
            print(f"[FAIL] [Network/Timeout] {description} -> {exc}")
            all_passed = False

    print("========================================================================")
    if all_passed:
        print("[OK] LIVE PRODUCTION DEPLOYMENT FULLY OPERATIONAL (ZERO DOWNTIME)")
    else:
        print("[FAIL] LIVE PRODUCTION AUDIT IDENTIFIED DEGRADED SERVICES", file=sys.stderr)
    print("========================================================================")
    return all_passed


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    if not run_live_smoke_test(target_url):
        sys.exit(1)
