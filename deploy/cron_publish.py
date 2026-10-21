"""
نشر روابط التحميل — نسخة مستقلة تُشغَّل من أي خدمة cron (سحابية).

    python deploy/cron_publish.py

تستخدم:
    • مهمة مجدولة على ويندوز/لينكس (cron)
    • GitHub Actions
    • Cloudflare Workers (Cron Trigger)
    • cron-job.org أو أي خدمة cron مجانية (بتطلب رابط واحد)

المتغيّرات:
    HF_TOKEN  — توكن Hugging Face (write)
    (أو ضعه في ملف deploy/hf-token.txt بجانب السكربت ✓)
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

# الملفات على MediaFire (المجلد المشترك) — بدّلها لو غيّرت الملفات
FILES = [
    ("bycusznj016983x", "أندرويد + تلفاز (APK)"),
    ("pzhsd7zuduadeal", "ويندوز — مثبّت"),
    ("anxl7qi0vxcoiv4", "ويندوز — محمول (بدون تثبيت)"),
    ("c4u8cm76ezotbzj", "آيفون/آيباد (مشروع Xcode)"),
]

# نسخة الأندرويد الدائمة على Hugging Face — used for in-app update ✓
# (رابط مباشر يُنزَّل داخل التطبيق — MediaFire صفحة ويب لا ملفاً)
APK_HF_URL = (
    "https://huggingface.co/datasets/hkarrar227/zeggy-data/resolve/main/"
    "apk/ZEEGY-BOX-Android.apk"
)

# إصدار التطبيق الحالي (versionCode) — يُرفع مع كل بناء جديد
APP_VERSION = "1.1"
APP_VERSION_CODE = 11

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
        print("  ⚠", path, type(e).__name__, str(e)[:80])
        return False


def main() -> int:
    token = get_token()
    if not token:
        print("⚠ لا يوجد HF_TOKEN — تخطّي")
        return 1

    links = []
    for key, label in FILES:
        url = f"https://www.mediafire.com/file/{key}"
        status, html = fetch(url)
        name = size = ""
        if status == 200:
            t = re.search(r"<title>([^<]{2,140}?)</title>", html)
            name = t.group(1).split("|")[0].split("—")[0].strip() if t else ""
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
        print(f"  {'✔' if status == 200 else '✘'} {label:26} {name} ({size})")

    alive = [l for l in links if l["available"]]

    # رابط تحميل مباشر للأندرويد (نسخة HF الدائمة) — يُفتح في المتصفح ✓
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
        print(f"  ✔ {'أندرويد — تحميل مباشر':26} ZEEGY-BOX-Android.apk")
    except Exception as e:
        print(f"  ⚠ رابط APK المباشر: {type(e).__name__}")

    if not alive:
        print("⚠ لا يوجد ملف متاح")
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
    print(f"  {'✔' if ok1 else '⚠'} روابط التحميل")

    apk = next((l for l in alive if "APK" in l["label"]), None)
    if apk:
        # رابط التحديث: نسخة HF الدائمة (ملف مباشر) ✦
        # MediaFire رابط صفحة — لا يصلح للتنزيل الآلي داخل التطبيق ✗
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

        ok2 = commit(
            token,
            "app-update.json",
            {
                "version": APP_VERSION,
                "versionCode": APP_VERSION_CODE,
                "url": update_url,
                "notes": "الإصدار الرسمي — روابط دائمة ✦ أندرويد + تلفاز + ويندوز + ماك",
                "publishedAt": time.strftime("%Y-%m-%d %H:%M"),
                "size": size,
            },
            "app update manifest (cron)",
        )
        print(f"  {'✔' if ok2 else '⚠'} بيان التحديث")

    print(f"✔ تم — {len(alive)}/{len(FILES)} ملف")
    return 0 if ok1 else 1


if __name__ == "__main__":
    sys.exit(main())
