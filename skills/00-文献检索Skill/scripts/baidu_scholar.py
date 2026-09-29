#!/usr/bin/env python3
"""百度学术检索 — 百度千帆 v2/tools/baidu_scholar/search
用法: python baidu_scholar.py search "<关键词>" [--page 0] [--abstract]
"""
import argparse, json, os, sys, urllib.parse, urllib.request

UA = "baidu-scholar/1.0"
TIMEOUT = 20
API = "https://qianfan.baidubce.com/v2/tools/baidu_scholar/search"


def cmd_search(args):
    key = os.environ.get("BAIDU_API_KEY")
    if not key:
        print(json.dumps({"error": "BAIDU_API_KEY not set"}, ensure_ascii=False))
        sys.exit(1)

    params = {
        "wd": args.query,
        "pageNum": str(args.page),
        "enable_ai_abstract": "true" if args.abstract else "false",
    }
    url = API + "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Authorization": f"Bearer {key}",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"HTTP {e.code}: {e.reason}"}, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="baidu_scholar")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--page", type=int, default=0)
    p.add_argument("--abstract", action="store_true")
    p.set_defaults(func=cmd_search)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
