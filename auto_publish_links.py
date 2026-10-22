"""
ظ†ط´ط± طھظ„ظ‚ط§ط¦ظٹ ظ„ط±ظˆط§ط¨ط· ط§ظ„طھط­ظ…ظٹظ„ â€” ظٹطھط£ظƒط¯ ط£ظ† ظ…ظ„ظپط§طھ MediaFire ظ…ظˆط¬ظˆط¯ط© ظˆظٹط­ط¯ظ‘ط«
ط±ظˆط§ط¨ط· ط§ظ„طھط·ط¨ظٹظ‚ + ط¨ظٹط§ظ† ط§ظ„طھط­ط¯ظٹط« ط¹ظ„ظ‰ ط§ظ„ط¥ظ†طھط±ظ†طھ.

ظٹظڈط´ط؛ظژظ‘ظ„ ظٹط¯ظˆظٹط§ظ‹ ط£ظˆ ظ…ظ† ظ…ظ‡ظ…ط© ظ…ط¬ط¯ظˆظ„ط© (ظƒظ„ ظ£ظ  ط¯ظ‚ظٹظ‚ط©) âœ“

    python deploy/auto_publish_links.py
"""
import base64
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS = os.path.join(ROOT, "deploy", "download-links.txt")
PUBLIC = os.path.join(ROOT, "web", "public")
HF_REPO = "hkarrar227/zeggy-data"

# ط§ظ„ظ…ظ„ظپط§طھ ط§ظ„ظ…ط¹ط±ظˆظپط© (ط§ظ„ظ…ط¬ظ„ط¯ ط§ظ„ظ…ط´طھط±ظƒ ط¹ظ„ظ‰ MediaFire)
FILES = [
    ("4rmhxdlqgiogltj", "ط£ظ†ط¯ط±ظˆظٹط¯ + طھظ„ظپط§ط² (APK)"),
    ("pzhsd7zuduadeal", "ظˆظٹظ†ط¯ظˆط² â€” ظ…ط«ط¨ظ‘طھ"),
    ("anxl7qi0vxcoiv4", "ظˆظٹظ†ط¯ظˆط² â€” ظ…ط­ظ…ظˆظ„ (ط¨ط¯ظˆظ† طھط«ط¨ظٹطھ)"),
    ("c4u8cm76ezotbzj", "ط¢ظٹظپظˆظ†/ط¢ظٹط¨ط§ط¯ (ظ…ط´ط±ظˆط¹ Xcode)"),
]

# ظ†ط³ط®ط© ط§ظ„ط£ظ†ط¯ط±ظˆظٹط¯ ط§ظ„ط¯ط§ط¦ظ…ط© ط¹ظ„ظ‰ Hugging Face â€” طھظڈط³طھط®ط¯ظ… ظپظٹ ط§ظ„طھط­ط¯ظٹط« ط¯ط§ط®ظ„ ط§ظ„طھط·ط¨ظٹظ‚ âœ“
# (ط±ط§ط¨ط· MediaFire طµظپط­ط© ظˆظٹط¨ â€” ظ„ط§ ظٹطµظ„ط­ ظ„ظ„طھظ†ط²ظٹظ„ ط§ظ„ط¢ظ„ظٹ âœ—)
APK_HF_URL = (
    "https://huggingface.co/datasets/hkarrar227/zeggy-data/resolve/main/"
    "apk/ZEEGY-BOX-Android.apk"
)

# ط¥طµط¯ط§ط± ط§ظ„طھط·ط¨ظٹظ‚ ط§ظ„ط­ط§ظ„ظٹ â€” ظ„ط§ط²ظ… ظٹطھط­ط¯ظ‘ط« ظ…ط¹ ظƒظ„ ط¨ظ†ط§ط، ط¬ط¯ظٹط¯ âœ“
APP_VERSION = "2.2"
APP_VERSION_CODE = 22

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def token() -> str:
    for p in (
        os.path.join(ROOT, "deploy", "hf-token.txt"),
        os.path.join(ROOT, "deploy", "vercel.env"),
    ):
        if os.path.exists(p):
            m = re.search(r"(?m)^HF_TOKEN=(.+)$", io.open(p, encoding="utf-8").read())
            if m:
                return m.group(1).strip()
    return ""


def head(url: str, tries: int = 3) -> tuple[int, str]:
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=H, method="GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, ""
            time.sleep(4)
        except Exception:
            time.sleep(4)
    return 0, ""


def commit(path: str, payload: dict, summary: str, tk: str) -> bool:
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
        f"https://huggingface.co/api/datasets/{HF_REPO}/commit/main",
        data=("\n".join(lines) + "\n").encode(),
        method="POST",
        headers={"Authorization": f"Bearer {tk}", "Content-Type": "application/x-ndjson"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.status in (200, 201)
    except Exception as e:
        print(f"  âڑ  {path}: {type(e).__name__}")
        return False


AUTO_LOG = os.path.join(ROOT, "deploy", "auto-publish.log")


def log_line(text: str) -> None:
    """ظٹظƒطھط¨ ظپظٹ ط§ظ„ط³ط¬ظ„ + ظٹط·ط¨ط¹ ط¹ظ„ظ‰ ط§ظ„ط´ط§ط´ط©."""
    try:
        with open(AUTO_LOG, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass
    print(text)


def main() -> int:
    tk = token()
    if not tk:
        print("âڑ  HF_TOKEN ط؛ظٹط± ظ…ظˆط¬ظˆط¯ â€” طھط®ط·ظ‘ظٹ ط§ظ„ظ†ط´ط±")
        return 0

    print("â•گ" * 56)
    print("  ZEEGY BOX â€” ظ†ط´ط± طھظ„ظ‚ط§ط¦ظٹ ظ„ظ„ط±ظˆط§ط¨ط·")
    print("â•گ" * 56)

    links = []
    alive = 0
    for key, label in FILES:
        url = f"https://www.mediafire.com/file/{key}"
        status, html = head(url)
        name = ""
        size = ""
        if status == 200:
            alive += 1
            t = re.search(r"<title>([^<]{2,140}?)</title>", html)
            name = t.group(1).split("|")[0].split("â€”")[0].strip() if t else ""
            s = re.search(r"([\d.]+\s*(?:MB|KB|GB))", html)
            size = s.group(1) if s else ""
            print(f"  âœ” {label:26} {name} ({size})")
        else:
            print(f"  âœک {label:26} ط؛ظٹط± ظ…طھط§ط­ (ط±ظ…ط² {status})")
        links.append(
            {
                "label": label,
                "url": url,
                "name": name,
                "size": size,
                "available": status == 200,
            }
        )

    if not alive:
        print("\nâڑ  ظ„ط§ ظٹظˆط¬ط¯ ظ…ظ„ظپ ظ…طھط§ط­ â€” ظ„ظ… ظٹظڈظ†ط´ط± ط´ظٹط،")
        return 1

    # â‘  ظ…ظ„ظپ ط§ظ„ط±ظˆط§ط¨ط·
    with open(LINKS, "w", encoding="utf-8") as f:
        f.write("ZEEGY BOX â€” ط±ظˆط§ط¨ط· ط§ظ„طھط­ظ…ظٹظ„ (ط¯ط§ط¦ظ…ط© âœ¦ MediaFire + Hugging Face)\n\n")
        f.write(f"ط£ظ†ط¯ط±ظˆظٹط¯ â€” طھط­ظ…ظٹظ„ ظ…ط¨ط§ط´ط± (ط§ظ„ط£ط­ط¯ط« v{APP_VERSION}): {APK_HF_URL}\n")
        for l in links:
            if l["available"]:
                f.write(f"{l['label']}: {l['url']}\n")

    # â‘، طµظپط­ط© ط§ظ„طھط­ظ…ظٹظ„ â€” ط±ط§ط¨ط· ظ…ط¨ط§ط´ط± ظ„ظ„ط£ظ†ط¯ط±ظˆظٹط¯ ط£ظˆظ„ط§ظ‹ âœ“
    direct = (
        f'<a class="row" href="{APK_HF_URL}" style="border-color:#2de2d0;background:#101d1c">'
        f"<span><b style=\"color:#2de2d0\">ط£ظ†ط¯ط±ظˆظٹط¯ â€” طھط­ظ…ظٹظ„ ظ…ط¨ط§ط´ط± "
        f"(ط§ظ„ط£ط­ط¯ط« v{APP_VERSION})</b><br>"
        f'<small style="color:#93a4ab;font-size:11.5px">ZEEGY-BOX-Android.apk آ· '
        f"ط±ط§ط¨ط· ط¯ط§ط¦ظ…</small></span><b>طھظ†ط²ظٹظ„ â¤“</b></a>"
    )
    rows = "\n".join(
        f'<a class="row" href="{l["url"]}"><span>{l["label"]}<br>'
        f'<small style="color:#93a4ab;font-size:11.5px">{l["name"]} آ· {l["size"]}</small></span>'
        f"<b>طھظ†ط²ظٹظ„ â¤“</b></a>"
        for l in links
        if l["available"]
    )
    io.open(os.path.join(PUBLIC, "download.html"), "w", encoding="utf-8").write(
        f"""<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>طھط­ظ…ظٹظ„ ZEEGY BOX</title>
<style>
 body{{margin:0;background:#0b0f11;color:#fff;font-family:"Segoe UI",Tahoma,Arial,sans-serif;padding:34px 18px}}
 .wrap{{max-width:560px;margin:0 auto}}
 h1{{font-size:22px;margin:0 0 4px}} .sub{{color:#93a4ab;font-size:13px;margin-bottom:22px}}
 .row{{display:flex;justify-content:space-between;align-items:center;gap:12px;background:#131a1d;
   border:1px solid #223035;border-radius:14px;padding:14px 16px;margin-bottom:10px;text-decoration:none;color:#fff;transition:.16s}}
 .row:hover{{border-color:#2de2d0;background:#16211f}}
 .row b{{color:#2de2d0;font-size:13px;white-space:nowrap}}
 .note{{color:#93a4ab;font-size:12px;line-height:1.8;margin-top:18px}}
</style></head><body><div class="wrap">
<img src="/brand/logo.png" alt="" style="width:56px;height:56px;border-radius:16px;margin-bottom:12px">
<h1>ZEEGY BOX</h1>
<p class="sub">ظƒظ„ ط§ظ„ظ†ط³ط® â€” طھط¹ظ…ظ„ ظ…ط¨ط§ط´ط±ط© ظ…ظ† ط¬ظ‡ط§ط²ظƒ ط¨ط¯ظˆظ† ط³ظٹط±ظپط±</p>
{direct}
{rows}
<p class="note">â€¢ ط£ظ†ط¯ط±ظˆظٹط¯: ظپط¹ظ‘ظ„ آ«طھط«ط¨ظٹطھ ظ…ظ† ظ…طµط§ط¯ط± ط؛ظٹط± ظ…ط¹ط±ظˆظپط©آ» ط«ظ… ط§ظپطھط­ ط§ظ„ظ…ظ„ظپ.<br>
â€¢ ظˆظٹظ†ط¯ظˆط²: ط´ط؛ظ‘ظ„ ط§ظ„ظ…ط«ط¨ظ‘طھ (ط£ظˆ ط§ظ„ظ†ط³ط®ط© ط§ظ„ظ…ط­ظ…ظˆظ„ط© ط¨ط¯ظˆظ† طھط«ط¨ظٹطھ).<br>
â€¢ ظ…ط§ظƒ: ط§ظپطھط­ ظ…ظ„ظپ dmg.<br>
â€¢ ط¢ظٹظپظˆظ†/ط¢ظٹط¨ط§ط¯: ط§ظپطھط­ ط§ظ„ط±ط§ط¨ط· ظپظٹ ط³ظپط§ط±ظٹ â†گ آ«ظ…ط´ط§ط±ظƒط©آ» â†گ آ«ط¥ط¶ط§ظپط© ط¥ظ„ظ‰ ط§ظ„ط´ط§ط´ط© ط§ظ„ط±ط¦ظٹط³ظٹط©آ».<br>
â€¢ ط§ظ„طھط­ط¯ظٹط«ط§طھ طھطµظٹط± ط¯ط§ط®ظ„ ط§ظ„طھط·ط¨ظٹظ‚ â€” آ«ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ â†گ ط§ظ„طھط­ط¯ظٹط«ط§طھآ».</p>
</div></body></html>"""
    )

    # â‘¢ ط§ظ„ظ†ط´ط± ط¹ظ„ظ‰ ط§ظ„ط¥ظ†طھط±ظ†طھ
    # ط­ط¬ظ… ظ†ط³ط®ط© APK ط§ظ„ط¯ط§ط¦ظ…ط© (ظ…ظ† HF)
    apk_size = 0
    try:
        req = urllib.request.Request(
            APK_HF_URL, headers={"User-Agent": H["User-Agent"]}, method="GET"
        )
        with urllib.request.urlopen(req, timeout=300) as r:
            apk_size = int(r.headers.get("Content-Length") or 0)
    except Exception:
        pass

    published = [
        {
            "label": "ط£ظ†ط¯ط±ظˆظٹط¯ â€” طھط­ظ…ظٹظ„ ظ…ط¨ط§ط´ط± (ط§ظ„ط£ط­ط¯ط«)",
            "url": APK_HF_URL,
            "size": f"{apk_size / 1048576:.2f}MB" if apk_size else "",
        }
    ]
    published += [
        {"label": l["label"], "url": l["url"], "size": l["size"]}
        for l in links
        if l["available"]
    ]

    ok1 = commit(
        "download-links.json",
        {
            "links": published,
            "updatedAt": time.strftime("%Y-%m-%d %H:%M"),
        },
        "download links (auto)",
        tk,
    )
    log_line(f"\n  {'âœ”' if ok1 else 'âڑ '} ط±ظˆط§ط¨ط· ط§ظ„طھط­ظ…ظٹظ„")

    apk = next((l for l in links if "APK" in l["label"] and l["available"]), None)
    if apk:
        # حماية من التراجع — كمثل cron_publish.py ✓
        cur = {}
        try:
            req = urllib.request.Request(
                APK_HF_URL.replace("/resolve/main/apk/ZEEGY-BOX-Android.apk", "/resolve/main/app-update.json"),
                headers={"User-Agent": UA["User-Agent"]},
            )
            with urllib.request.urlopen(req, timeout=90) as r:
                cur = json.loads(r.read().decode("utf-8", "replace"))
        except Exception:
            cur = {}
        try:
            remote_code = int(cur.get("versionCode") or 0)
        except (TypeError, ValueError):
            remote_code = 0
        if remote_code > APP_VERSION_CODE:
            version = str(cur.get("version") or APP_VERSION)
            notes = str(cur.get("notes") or "")
            published_at = str(cur.get("publishedAt") or time.strftime("%Y-%m-%d %H:%M"))
        else:
            version = APP_VERSION
            notes = "تحديث 2.2 — إصلاح صفحات المجموعات ونجوم الشهر (كانت لا تفتح) + زر الرجوع في مكانه الصحيح تحت الهيدر + فتح الأعمال أسرع (تحميل مسبق عند اللمس) + أسماء النجوم تظهر في الرئيسية."
            published_at = time.strftime("%Y-%m-%d %H:%M")

        # ط±ط§ط¨ط· ط§ظ„طھط­ط¯ظٹط«: ظ†ط³ط®ط© HF ط§ظ„ط¯ط§ط¦ظ…ط© (ظ…ظ„ظپ ظ…ط¨ط§ط´ط±) âœ¦
        update_url = APK_HF_URL

        ok2 = commit(
            "app-update.json",
            {
                "version": version,
                "versionCode": max(APP_VERSION_CODE, remote_code),
                "url": update_url,
                "notes": notes,
                "publishedAt": published_at,
                "size": apk_size,
            },
            "app update manifest (auto)",
            tk,
        )
        log_line(f"  {'âœ”' if ok2 else 'âڑ '} ط¨ظٹط§ظ† ط§ظ„طھط­ط¯ظٹط«")

    log_line(f"\nâœ” طھظ… â€” {alive}/{len(FILES)} ظ…ظ„ظپ ظ…طھط§ط­ âœ“")
    return 0


if __name__ == "__main__":
    sys.exit(main())






