"""
ظ†ط´ط± ط±ظˆط§ط¨ط· ط§ظ„طھط­ظ…ظٹظ„ â€” ظ†ط³ط®ط© ظ…ط³طھظ‚ظ„ط© طھظڈط´ط؛ظژظ‘ظ„ ظ…ظ† ط£ظٹ ط®ط¯ظ…ط© cron (ط³ط­ط§ط¨ظٹط©).

    python deploy/cron_publish.py

طھط³طھط®ط¯ظ…:
    â€¢ ظ…ظ‡ظ…ط© ظ…ط¬ط¯ظˆظ„ط© ط¹ظ„ظ‰ ظˆظٹظ†ط¯ظˆط²/ظ„ظٹظ†ظƒط³ (cron)
    â€¢ GitHub Actions
    â€¢ Cloudflare Workers (Cron Trigger)
    â€¢ cron-job.org ط£ظˆ ط£ظٹ ط®ط¯ظ…ط© cron ظ…ط¬ط§ظ†ظٹط© (ط¨طھط·ظ„ط¨ ط±ط§ط¨ط· ظˆط§ط­ط¯)

ط§ظ„ظ…طھط؛ظٹظ‘ط±ط§طھ:
    HF_TOKEN  â€” طھظˆظƒظ† Hugging Face (write)
    (ط£ظˆ ط¶ط¹ظ‡ ظپظٹ ظ…ظ„ظپ deploy/hf-token.txt ط¨ط¬ط§ظ†ط¨ ط§ظ„ط³ظƒط±ط¨طھ âœ“)
"""
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HF_REPO = "hkarrar227/zeggy-data"
HF_API = "https://huggingface.co/api/datasets"

# ط§ظ„ظ…ظ„ظپط§طھ ط¹ظ„ظ‰ MediaFire (ط§ظ„ظ…ط¬ظ„ط¯ ط§ظ„ظ…ط´طھط±ظƒ) â€” ط¨ط¯ظ‘ظ„ظ‡ط§ ظ„ظˆ ط؛ظٹظ‘ط±طھ ط§ظ„ظ…ظ„ظپط§طھ
FILES = [
    ("4rmhxdlqgiogltj", "أندرويد + تلفاز (APK)"),
    ("pzhsd7zuduadeal", "ويندوز — مثبّت"),
    ("anxl7qi0vxcoiv4", "ويندوز — محمول (بدون تثبيت)"),
    ("c4u8cm76ezotbzj", "آيفون/آيباد (مشروع Xcode)"),
]

# رابط تطبيق الويب الفوري — يفتح من أي متصفح بلا تثبيت (نسخة الكتالوج الثابت)
WEB_APP_URL = "https://an2874757-art.github.io/zeggy-web/"

# ظ†ط³ط®ط© ط§ظ„ط£ظ†ط¯ط±ظˆظٹط¯ ط§ظ„ط¯ط§ط¦ظ…ط© ط¹ظ„ظ‰ Hugging Face â€” used for in-app update âœ“
# (ط±ط§ط¨ط· ظ…ط¨ط§ط´ط± ظٹظڈظ†ط²ظژظ‘ظ„ ط¯ط§ط®ظ„ ط§ظ„طھط·ط¨ظٹظ‚ â€” MediaFire طµظپط­ط© ظˆظٹط¨ ظ„ط§ ظ…ظ„ظپط§ظ‹)
APK_HF_URL = (
    "https://huggingface.co/datasets/hkarrar227/zeggy-data/resolve/main/"
    "apk/ZEEGY-BOX-Android.apk"
)

# ط¥طµط¯ط§ط± ط§ظ„طھط·ط¨ظٹظ‚ ط§ظ„ط­ط§ظ„ظٹ (versionCode) â€” ظٹظڈط±ظپط¹ ظ…ط¹ ظƒظ„ ط¨ظ†ط§ط، ط¬ط¯ظٹط¯
APP_VERSION = "2.2"
APP_VERSION_CODE = 22

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def get_token() -> str:
    tok = (os.environ.get("HF_TOKEN") or "").strip()
    if tok:
        return tok
    for p in (
        os.path.join(ROOT, "deploy", "hf-token.txt"),
        os.path.join(ROOT, "deploy", "vercel.env"),
    ):
        if os.path.exists(p):
            m = re.search(r"(?m)^HF_TOKEN=(.+)$", open(p, encoding="utf-8").read())
            if m:
                return m.group(1).strip()
    return ""


def fetch(url: str, tries: int = 3):
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, ""
            time.sleep(4)
        except Exception:
            time.sleep(4)
    return 0, ""


def commit(token: str, path: str, payload: dict, summary: str) -> bool:
    content = json.dumps(payload, ensure_ascii=False, indent=2).encode()
    lines = [
        json.dumps({"key": "header", "value": {"summary": summary, "description": ""}}),
        json.dumps(
            {
                "key": "file",
                "value": {
                    "content": base64.b64encode(content).decode(),
                    "path": path,
                    "encoding": "base64",
                },
            }
        ),
    ]
    req = urllib.request.Request(
        f"{HF_API}/{HF_REPO}/commit/main",
        data=("\n".join(lines) + "\n").encode(),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/x-ndjson"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status in (200, 201)
    except Exception as e:
        print("  âڑ ", path, type(e).__name__, str(e)[:80])
        return False


def current_remote_manifest() -> dict:
    """بيان التحديث الموجود سحابياً (لحماية الحاوية من التراجع) ✓"""
    try:
        req = urllib.request.Request(
            "https://huggingface.co/datasets/hkarrar227/zeggy-data/resolve/main/app-update.json",
            headers=UA,
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return {}


def main() -> int:
    token = get_token()
    if not token:
        print("âڑ  ظ„ط§ ظٹظˆط¬ط¯ HF_TOKEN â€” طھط®ط·ظ‘ظٹ")
        return 1

    links = []
    for key, label in FILES:
        url = f"https://www.mediafire.com/file/{key}"
        status, html = fetch(url)
        name = size = ""
        if status == 200:
            t = re.search(r"<title>([^<]{2,140}?)</title>", html)
            name = t.group(1).split("|")[0].split("â€”")[0].strip() if t else ""
            s = re.search(r"([\d.]+\s*(?:MB|KB|GB))", html)
            size = s.group(1) if s else ""
        links.append(
            {
                "label": label,
                "url": url,
                "name": name,
                "size": size,
                "available": status == 200,
            }
        )
        print(f"  {'âœ”' if status == 200 else 'âœک'} {label:26} {name} ({size})")

    alive = [l for l in links if l["available"]]

    # ط±ط§ط¨ط· طھط­ظ…ظٹظ„ ظ…ط¨ط§ط´ط± ظ„ظ„ط£ظ†ط¯ط±ظˆظٹط¯ (ظ†ط³ط®ط© HF ط§ظ„ط¯ط§ط¦ظ…ط©) â€” ظٹظڈظپطھط­ ظپظٹ ط§ظ„ظ…طھطµظپط­ âœ“
    try:
        req = urllib.request.Request(
            APK_HF_URL, headers={"User-Agent": UA["User-Agent"]}, method="GET"
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            apk_size = int(r.headers.get("Content-Length") or 0)
        alive.insert(
            1,
            {
                "label": "أندرويد — تحميل مباشر (الأحدث)",
                "url": APK_HF_URL,
                "name": "ZEEGY-BOX-Android.apk",
                "size": f"{apk_size / 1048576:.2f}MB",
                "available": True,
            },
        )
        print(f"  ✓ أندرويد — تحميل مباشر          ZEEGY-BOX-Android.apk")
    except Exception as e:
        print(f"  âڑ  ط±ط§ط¨ط· APK ط§ظ„ظ…ط¨ط§ط´ط±: {type(e).__name__}")

    # تطبيق الويب لآيفون/آيباد/أي متصفح — فوري بلا تثبيت (نسخة الكتالوج الثابت) ✓
    alive.append(
        {
            "label": "آيفون / آيباد / أي متصفح — تطبيق ويب فوري (بدون تثبيت)",
            "url": WEB_APP_URL,
            "name": "web.zeggy",
            "size": "0MB (يفتح مباشرة)",
            "available": True,
        }
    )
    print("  ✓ تطبيق الويب (آيفون/أي متصفح)  web.zeggy")

    if not alive:
        print("âڑ  ظ„ط§ ظٹظˆط¬ط¯ ظ…ظ„ظپ ظ…طھط§ط­")
        return 1

    ok1 = commit(
        token,
        "download-links.json",
        {
            "links": [{"label": l["label"], "url": l["url"], "size": l["size"]} for l in alive],
            "updatedAt": time.strftime("%Y-%m-%d %H:%M"),
        },
        "download links (cron)",
    )
    print(f"  {'âœ”' if ok1 else 'âڑ '} ط±ظˆط§ط¨ط· ط§ظ„طھط­ظ…ظٹظ„")

    apk = next((l for l in alive if "APK" in l["label"]), None)
    if apk:
        # ط±ط§ط¨ط· ط§ظ„طھط­ط¯ظٹط«: ظ†ط³ط®ط© HF ط§ظ„ط¯ط§ط¦ظ…ط© (ظ…ظ„ظپ ظ…ط¨ط§ط´ط±) âœ¦
        # MediaFire ط±ط§ط¨ط· طµظپط­ط© â€” ظ„ط§ ظٹطµظ„ط­ ظ„ظ„طھظ†ط²ظٹظ„ ط§ظ„ط¢ظ„ظٹ ط¯ط§ط®ظ„ ط§ظ„طھط·ط¨ظٹظ‚ âœ—
        update_url = APK_HF_URL
        size = 0
        try:
            req = urllib.request.Request(
                update_url, headers={"User-Agent": UA["User-Agent"]}, method="GET"
            )
            with urllib.request.urlopen(req, timeout=180) as r:
                size = int(r.headers.get("Content-Length") or 0)
        except Exception:
            pass

        # حماية جذرية من التراجع: قد يُشغَّل السكربت من مصادر قديمة
        # (مستودع سحابي لم يُحدَّث بعد، أو نسخة محلية قديمة) ⇒ إن كان
        # الإصدار المنشور سحابياً أحدث من نسخة السكربت، نحافظ على بياناته
        # ولا نُرجِع بيان التحديث للوراء ✓
        cur = current_remote_manifest()
        try:
            remote_code = int(cur.get("versionCode") or 0)
        except (TypeError, ValueError):
            remote_code = 0
        if remote_code > APP_VERSION_CODE:
            version = str(cur.get("version") or APP_VERSION)
            notes = str(cur.get("notes") or "")
            published_at = str(cur.get("publishedAt") or time.strftime("%Y-%m-%d %H:%M"))
            print(f"  ⚠ الإصدار السحابي ({remote_code}) أحدث — حفظ بيان التحديث ✓")
        else:
            version = APP_VERSION
            notes = "تحديث 2.2 — إصلاح صفحات المجموعات ونجوم الشهر (كانت لا تفتح) + زر الرجوع في مكانه الصحيح تحت الهيدر + فتح الأعمال أسرع (تحميل مسبق عند اللمس) + أسماء النجوم تظهر في الرئيسية."
            published_at = time.strftime("%Y-%m-%d %H:%M")

        ok2 = commit(
            token,
            "app-update.json",
            {
                "version": version,
                "versionCode": max(APP_VERSION_CODE, remote_code),
                "url": update_url,
                "notes": notes,
                "publishedAt": published_at,
                "size": size,
            },
            "app update manifest (cron)",
        )
        print(f"  {'âœ”' if ok2 else 'âڑ '} ط¨ظٹط§ظ† ط§ظ„طھط­ط¯ظٹط«")

    print(f"âœ” طھظ… â€” {len(alive)}/{len(FILES)} ظ…ظ„ظپ")
    return 0 if ok1 else 1


if __name__ == "__main__":
    sys.exit(main())






