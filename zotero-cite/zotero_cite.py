#!/usr/bin/env python3
"""zotero-cite: add items to local Zotero and generate docx fragments with live Zotero citation fields.

Usage:
  python zotero_cite.py search <query> [--fulltext] [--tag TAG] [--collection NAME] [--limit N]
  python zotero_cite.py add <item.json> [--tag TAG ...] [--collection NAME]
  python zotero_cite.py cite KEY [KEY2 ...] [--text TEXT] [-o OUT.docx]
  python zotero_cite.py document <spec.json> [-o OUT.docx]
  python zotero_cite.py collections
  python zotero_cite.py mkcol NAME [--parent KEY]
  python zotero_cite.py move ITEM_KEY COLLECTION_KEY [--remove COLLECTION_KEY2]
  python zotero_cite.py delete ITEM_KEY
  python zotero_cite.py rmcol COLLECTION_KEY
"""
import argparse
import html
import json
import os
import random
import re
import string
import sys
import time
import urllib.parse
import urllib.request
import uuid
import zipfile
from xml.sax.saxutils import escape

BASE = "http://localhost:23119"
API = BASE + "/api/users/0"
def resolve_key_file():
    """API key 文件路径：环境变量优先，默认 ~/.config/zotero-cite/api-key。"""
    return os.environ.get("ZOTERO_API_KEY_FILE") or os.path.join(
        os.path.expanduser("~"), ".config", "zotero-cite", "api-key")


KEY_FILE = resolve_key_file()
_WEB_BASE = None


def web_api_base():
    """Web API 基地址：优先环境变量 ZOTERO_USER_ID，否则用 API key 自动获取用户 ID（可移植，不硬编码）。"""
    global _WEB_BASE
    if _WEB_BASE:
        return _WEB_BASE
    uid = os.environ.get("ZOTERO_USER_ID")
    if not uid:
        req = urllib.request.Request(
            "https://api.zotero.org/keys/current",
            headers={"Zotero-API-Key": load_web_key(), "Zotero-API-Version": "3"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            info = json.loads(resp.read().decode("utf-8"))
        uid = str(info.get("userID", ""))
        if not uid:
            sys.exit("无法从 API key 解析 Zotero 用户 ID；请设置环境变量 ZOTERO_USER_ID")
    _WEB_BASE = "https://api.zotero.org/users/" + uid
    return _WEB_BASE


def load_web_key():
    try:
        with open(KEY_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        sys.exit(f"API key not found at {KEY_FILE}")


def web_request(path, method="GET", data=None, if_version=None):
    headers = {"Zotero-API-Key": load_web_key(), "Zotero-API-Version": "3"}
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode("utf-8")
    if if_version is not None:
        headers["If-Unmodified-Since-Version"] = str(if_version)
    req = urllib.request.Request(web_api_base() + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"Web API error {e.code}: {e.read().decode('utf-8')[:300]}")

TYPE_MAP = {
    "journalArticle": "article-journal",
    "book": "book",
    "bookSection": "chapter",
    "conferencePaper": "paper-conference",
    "thesis": "thesis",
    "report": "report",
    "webpage": "webpage",
    "newspaperArticle": "article-newspaper",
    "magazineArticle": "article-magazine",
    "preprint": "article",
    "dataset": "dataset",
}
FIELD_MAP = {
    "publicationTitle": "container-title",
    "bookTitle": "container-title",
    "proceedingsTitle": "container-title",
    "encyclopediaTitle": "container-title",
    "dictionaryTitle": "container-title",
    "volume": "volume",
    "issue": "issue",
    "pages": "page",
    "publisher": "publisher",
    "place": "publisher-place",
    "DOI": "DOI",
    "url": "URL",
    "ISSN": "ISSN",
    "ISBN": "ISBN",
    "abstractNote": "abstract",
    "shortTitle": "short-title",
    "series": "collection-title",
    "edition": "edition",
    "language": "language",
    "citationKey": "citation-key",
}
CREATOR_MAP = {"author": "author", "editor": "editor", "translator": "translator"}


def ping_local():
    try:
        with urllib.request.urlopen(BASE + "/connector/ping", timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def find_zotero_exe():
    import os
    candidates = [
        os.path.expandvars(r"%ProgramFiles%\Zotero\zotero.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Zotero\zotero.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Zotero\zotero.exe"),
        os.environ.get("ZOTERO_EXE", ""),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def ensure_running(timeout=90):
    """Ping local Zotero; if down, launch it and wait until the HTTP server is up."""
    if ping_local():
        return
    exe = find_zotero_exe()
    if not exe:
        sys.exit("Zotero is not running and zotero.exe was not found; "
                 "please start Zotero manually or set ZOTERO_EXE")
    import subprocess
    subprocess.Popen([exe], close_fds=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2)
        if ping_local():
            time.sleep(2)
            return
    sys.exit("Zotero launched but local API did not come up in time")


def http_json(url, data=None, headers=None, raw=False):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read()
        if raw:
            return resp.status, body
        return resp.status, body.decode("utf-8")


def api_get(path):
    status, text = http_json(API + path)
    if status != 200:
        sys.exit(f"Local API error {status}: {text[:200]}")
    return json.loads(text)


def search_items(query, limit=10):
    q = urllib.parse.quote(query)
    items = api_get(f"/items?q={q}&qmode=titleCreatorYear&limit={limit}&itemType=-attachment")
    return items


def find_key_by_title(title):
    items = search_items(title, limit=20)
    exact = [i for i in items if i["data"].get("title", "").strip() == title.strip()]
    pool = exact or items
    if not pool:
        return None
    pool.sort(key=lambda i: i["data"].get("dateAdded", ""), reverse=True)
    return pool[0]["key"]


def cmd_search(args):
    params = [f"q={urllib.parse.quote(args.query)}", f"limit={args.limit}",
              "itemType=-attachment"]
    if args.fulltext:
        params.append("qmode=everything")
    if args.tag:
        params.append("tag=" + urllib.parse.quote(args.tag))
    if args.collection:
        col_key = find_collection_key(args.collection)
        if not col_key:
            sys.exit(f"collection not found: {args.collection}")
        params.append("collection=" + col_key)
    items = api_get("/items?" + "&".join(params))
    for i in items:
        d = i["data"]
        creators = "; ".join(
            c.get("lastName", c.get("name", "")) for c in d.get("creators", [])
        )
        print(f'{i["key"]}\t{d.get("date", "")[:4]}\t{creators}\t{d.get("title", "")}')
    if not items:
        print("(no results)")


def find_collection_key(name):
    cols = api_get("/collections")
    exact = [c for c in cols if c["data"]["name"] == name]
    return exact[0]["key"] if exact else None


def patch_item_collections(item_key, collections):
    _, item = web_request(f"/items/{item_key}")
    version = item["version"]
    web_request(f"/items/{item_key}", method="PATCH",
                data={"collections": collections}, if_version=version)


def patch_item_collections_retry(item_key, collections, attempts=4, delay=2.0):
    """归文件夹（Web API PATCH）。connector 刚保存的条目在 Web API 侧可能有秒级同步延迟，
    首次失败会 sys.exit；这里捕获后间隔重试，耗尽次数再抛出最后一次错误。"""
    last_args = None
    for i in range(attempts):
        try:
            patch_item_collections(item_key, collections)
            return
        except SystemExit as e:
            last_args = e.args
            if i < attempts - 1:
                time.sleep(delay)
    sys.exit((" ".join(str(a) for a in last_args)) if last_args else "patch item collections failed")


def cmd_collections(args):
    for c in api_get("/collections"):
        d = c["data"]
        print(f'{c["key"]}\t{d["name"]}\tparent={d.get("parentCollection") or "-"}')


def cmd_mkcol(args):
    col = {"name": args.name, "parentCollection": args.parent or False}
    _, result = web_request("/collections", method="POST", data=[col])
    if result.get("success"):
        key = list(result["success"].values())[0]
        print(json.dumps({"key": key}, ensure_ascii=False))
    else:
        sys.exit(f"create collection failed: {json.dumps(result, ensure_ascii=False)}")


def cmd_move(args):
    _, item = web_request(f"/items/{args.item_key}")
    cols = set(item["data"].get("collections", []))
    cols.add(args.collection_key)
    if args.remove:
        cols.discard(args.remove)
    patch_item_collections(args.item_key, sorted(cols))
    print(json.dumps({"key": args.item_key, "collections": sorted(cols)}))


def cmd_delete(args):
    _, item = web_request(f"/items/{args.item_key}")
    web_request(f"/items/{args.item_key}", method="DELETE",
                if_version=item["version"])
    print(json.dumps({"deleted": args.item_key}))


def cmd_rmcol(args):
    _, col = web_request(f"/collections/{args.key}")
    web_request(f"/collections/{args.key}", method="DELETE",
                if_version=col["version"])
    print(json.dumps({"deleted": args.key}))


def _norm(s):
    return "".join(ch for ch in (html.unescape(s or "").lower()) if ch.isalnum())


def _raw(s):
    """原文级归一化：只反转义 + 去空白，保留标点——用于抓 &amp; 类实体残留。"""
    return re.sub(r"\s+", "", html.unescape(s or ""))


def _unescape_item(item):
    """入库前反转义所有文本字段的 HTML 实体（&amp; &lt; 等），防止元数据被污染。"""
    for k in ("title", "publicationTitle", "bookTitle", "proceedingsTitle",
              "encyclopediaTitle", "dictionaryTitle", "publisher", "abstractNote",
              "DOI", "url", "ISSN", "ISBN", "shortTitle", "series", "place",
              "edition", "language"):
        if isinstance(item.get(k), str):
            item[k] = html.unescape(item[k]).strip()
    for c in item.get("creators", []):
        for k in ("firstName", "lastName", "name"):
            if isinstance(c.get(k), str):
                c[k] = html.unescape(c[k]).strip()
    return item


def cmd_add(args):
    with open(args.file, encoding="utf-8") as f:
        item = json.load(f)
    _unescape_item(item)
    tags = item.setdefault("tags", [])
    for t in args.tag or []:
        tags.append({"tag": t})

    doi = item.get("DOI")
    title = item.get("title", "")

    # 去重 1：按 DOI 全文检索（qmode=everything 才索引 DOI 字段；默认 titleCreatorYear 搜不到 DOI）
    if doi:
        dup = api_get(f"/items?q={urllib.parse.quote(doi)}&qmode=everything&itemType=-attachment")
        if dup:
            print(json.dumps({"key": dup[0]["key"], "duplicate": True}, ensure_ascii=False))
            return
    # 去重 2：按归一化标题精确匹配兜底（老条目可能缺 DOI 字段）
    if title:
        hits = search_items(title, limit=20)
        for h in hits:
            d = h.get("data", {})
            if d.get("itemType") == "attachment":
                continue
            if _norm(d.get("title")) == _norm(title):
                print(json.dumps({"key": h["key"], "duplicate": True, "by": "title"}, ensure_ascii=False))
                return

    payload = json.dumps({
        "items": [item],
        "uri": item.get("url") or "http://localhost",
        "sessionID": "zc-" + uuid.uuid4().hex[:12],
    }).encode("utf-8")
    status, body = http_json(
        BASE + "/connector/saveItems",
        data=payload,
        headers={"Content-Type": "application/json"},
        raw=True,
    )
    if status not in (200, 201):
        sys.exit(f"saveItems failed {status}: {body[:200]}")

    key = None
    for _ in range(10):
        time.sleep(0.6)
        key = find_key_by_title(title)
        if key:
            break
    if not key:
        sys.exit("saved but could not resolve item key; check Zotero library")

    if args.collection:
        col_key = find_collection_key(args.collection)
        if not col_key:
            sys.exit(f"collection not found: {args.collection}")
        patch_item_collections_retry(key, [col_key])
    result = {"key": key, "duplicate": False}
    if args.check:
        report = verify_item_against_source(key, item)
        result["check"] = report
    print(json.dumps(result, ensure_ascii=False))


def verify_item_against_source(key, source_item):
    """入库后验证：读回 Zotero 条目，与源 item.json 逐字段比对。"""
    d = api_get(f"/items/{key}")["data"]
    problems, fields = [], {}
    checks = [
        ("title", "title", None),
        ("publicationTitle", "publicationTitle", "venue"),
        ("DOI", "DOI", "doi"),
        ("date", "year", "date"),
    ]
    for zf, sf, sf2 in checks:
        want = source_item.get(sf) if source_item.get(sf) is not None else source_item.get(sf2)
        got = d.get(zf)
        want = str(want) if want is not None else None
        got = str(got) if got is not None else None
        fields[zf] = {"source": want, "zotero": got}
        if want and got and _norm(want) != _norm(got):
            problems.append(f"{zf} 不一致：源 [{want}] vs Zotero [{got}]")
        elif want and not got:
            problems.append(f"{zf} 缺失：Zotero 未存 [{want}]")
        elif want and got and _raw(want) != _raw(got):
            problems.append(f"{zf} 值近似但原文有差异（疑似 HTML 实体残留/标点差异）：源 [{want}] vs Zotero [{got}]")
    src_cre = [(_norm(c.get("lastName", "")), _norm(c.get("firstName", ""))) for c in source_item.get("creators", [])]
    zot_cre = [(_norm(c.get("lastName", "")), _norm(c.get("firstName", ""))) for c in d.get("creators", [])]
    fields["creators"] = {"source_count": len(src_cre), "zotero_count": len(zot_cre)}
    if src_cre and src_cre != zot_cre:
        problems.append(f"作者不一致：源 {len(src_cre)} 人 vs Zotero {len(zot_cre)} 人（姓氏顺序/拆分需人工核对）")
    verdict = "✅ 一致" if not problems else "⚠️ 有差异"
    return {"verdict": verdict, "problems": problems, "fields": fields}


def cmd_check(args):
    """验证已入库条目：读回 Zotero 数据，与源 item.json 或 Crossref 权威元数据比对。"""
    d = api_get(f"/items/{args.key}")["data"]
    print(f"条目 {args.key} | {(d.get('title') or '')[:60]}")
    print("-" * 60)
    if args.source:
        with open(args.source, encoding="utf-8") as f:
            source_item = json.load(f)
        report = verify_item_against_source(args.key, source_item)
        for p in report["problems"]:
            print("⚠️", p)
        if not report["problems"]:
            print("✅ 与源 item.json 逐字段一致")
        return
    # 无源文件：按 DOI 调 Crossref 核验
    doi = d.get("DOI")
    if not doi:
        print("❌ 条目无 DOI，无法权威核验；请用 --source item.json 做字段比对")
        return
    try:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="") + "?mailto=litsearch@example.com"
        w = json.loads(urllib.request.urlopen(urllib.request.Request(url), timeout=30).read().decode("utf-8"))["message"]
        ref = {
            "title": html.unescape((w.get("title") or [None])[0] or ""),
            "venue": html.unescape((w.get("container-title") or [None])[0] or ""),
            "year": (w.get("issued", {}).get("date-parts", [[None]])[0][0]),
        }
        problems = []
        for label, got, want in (
            ("标题", d.get("title"), ref["title"]),
            ("期刊", d.get("publicationTitle"), ref["venue"]),
            ("年份", (d.get("date") or "")[:4], str(ref["year"])),
        ):
            if _norm(got) != _norm(want):
                problems.append((label, got, want, False, f"值不一致：Zotero [{got}] vs Crossref [{want}]"))
            elif _raw(got) != _raw(want):
                problems.append((label, got, want, True, f"值近似但原文有差异（疑似 HTML 实体残留）：Zotero [{got}] vs Crossref [{want}]"))
            else:
                problems.append((label, got, want, True, None))
        all_ok = True
        for label, got, want, match, note in problems:
            if match and not note:
                print("✅", label, "| Zotero:", got, "| Crossref:", want)
            else:
                print("⚠️", label, "|", note)
            all_ok = all_ok and match
        print("-" * 60)
        print("✅ 与 Crossref 权威元数据一致" if all_ok else "⚠️ 存在差异，见上方 ⚠️ 行")
    except urllib.error.HTTPError as e:
        print(f"❌ Crossref 查询失败（{e.code}）——DOI 可能无法解析")
    except Exception as e:
        print(f"❌ Crossref 查询异常: {e}")


def cmd_doctor(args):
    """环境自检：小白跑这一条命令，就知道环境缺什么、怎么补。只读检查，不修改任何东西。"""
    checks = {}

    def report(name, status, detail, fix=None):
        checks[name] = {"status": status, "detail": detail, "fix": fix}
        mark = {"ok": "✅", "warn": "⚠️", "fail": "❌", "info": "ℹ️"}[status]
        print("%s %s：%s" % (mark, name, detail))
        if fix:
            for line in fix.splitlines():
                print("      " + line)

    print("=" * 56)
    print(" Zotero 环境自检（只读检查，不会改动任何配置）")
    print("=" * 56)

    exe = find_zotero_exe()
    if exe:
        report("Zotero 安装", "ok", exe)
    else:
        report("Zotero 安装", "fail", "未找到 zotero.exe",
               "到 zotero.org 下载安装 Zotero 5.0+（默认路径安装即可）；非默认路径时设置环境变量 ZOTERO_EXE 指向 zotero.exe")

    running = ping_local()
    if running:
        report("Local API 开关", "ok", "Zotero 运行中，localhost:23119 连通",
               "开关位置：设置 → 高级 → 常规 → 勾选'允许此计算机上的其他应用程序与 Zotero 通讯'")
    else:
        report("Local API 开关", "fail", "无法连接 localhost:23119（开关未开或 Zotero 未运行）",
               "① 打开 Zotero；② 设置 → 高级 → 常规 → 勾选'允许此计算机上的其他应用程序与 Zotero 通讯'；③ 浏览器访问 http://localhost:23119/connector/ping 应显示 running")

    try:
        load_web_key()
        status, _ = web_request("/collections?limit=1")
        if status == 200:
            report("账号与 API key", "ok", "已登录且 key 有效（Web API 连通），用户 ID 自动解析为 %s" % web_api_base().rsplit("/", 1)[-1])
        else:
            report("账号与 API key", "fail", "Web API 返回状态 %s" % status)
    except SystemExit as e:
        report("账号与 API key", "fail", str(e),
               "① 到 zotero.org 登录 → 设置 → Keys → Create new private key（全选权限）；"
               "② 把 key 存到文件：ZOTERO_API_KEY_FILE 环境变量指定的路径，或默认 %s；"
               "③ 确认 Zotero 桌面端已登录（设置 → 同步）" % KEY_FILE)

    report("Word 插件", "info", "打开 Word 看菜单栏是否有 'Zotero' 标签（只做文献管理可忽略）")
    report("浏览器插件", "info", "skill 不依赖浏览器插件，未安装也能正常使用")

    print("=" * 56)
    all_ok = all(c["status"] != "fail" for c in checks.values())
    print(" ✅ 全部就绪，可以直接用了。" if all_ok else " ❌ 还有未就绪项，按上方指引处理，处理完再跑一次复查。")
    if args.json:
        print(json.dumps({"all_ok": all_ok, "checks": checks}, ensure_ascii=False, indent=2))
    sys.exit(0 if all_ok else 1)


def zotero_to_csl(d):
    csl = {"type": TYPE_MAP.get(d.get("itemType"), "article-journal")}
    for zf, cf in FIELD_MAP.items():
        if d.get(zf):
            csl[cf] = d[zf]
    if d.get("title"):
        csl["title"] = d["title"]
    for c in d.get("creators", []):
        role = CREATOR_MAP.get(c.get("creatorType"))
        if not role:
            continue
        entry = {"family": c.get("lastName", ""), "given": c.get("firstName", "")}
        if c.get("name"):
            entry = {"literal": c["name"]}
        csl.setdefault(role, []).append(entry)
    date = d.get("date", "")
    m = re.search(r"(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?", date)
    if m:
        parts = [int(m.group(1))]
        if m.group(2):
            parts.append(int(m.group(2)))
        if m.group(3):
            parts.append(int(m.group(3)))
        csl["issued"] = {"date-parts": [parts]}
    return csl


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def get_item_bundle(key):
    item = api_get(f"/items/{key}?include=data,bib,citation")
    d = item["data"]
    alt = item.get("links", {}).get("alternate", {}).get("href", "")
    uri = alt.replace("https://www.zotero.org", "http://zotero.org") or \
        f"http://zotero.org/users/0/items/{key}"
    cit_text = strip_tags(item.get("citation", ""))
    return {"key": key, "data": d, "uri": uri, "citation_text": cit_text,
            "bib_html": item.get("bib", "")}


def citation_instr(bundles):
    cit_items = []
    texts = []
    for b in bundles:
        csl = zotero_to_csl(b["data"])
        csl["id"] = b["key"]
        ci = {"id": b["key"], "uris": [b["uri"]], "itemData": csl}
        if b.get("suppress_author"):
            ci["suppress-author"] = True
        cit_items.append(ci)
        if b["citation_text"]:
            t = b["citation_text"]
            if b.get("suppress_author"):
                m = re.match(r"^\(.*(\d{4}).*\)$", t)
                if m:
                    t = f"({m.group(1)})"
            texts.append(t)
    plain = "; ".join(texts) if texts else "(citation)"
    if plain and not plain.startswith("("):
        plain = "(" + plain + ")"
    cit = {
        "citationID": "".join(random.choices(string.ascii_letters, k=8)),
        "properties": {
            "unsorted": False,
            "formattedCitation": plain,
            "plainCitation": plain,
            "noteIndex": 0,
        },
        "citationItems": cit_items,
        "schema": "https://github.com/citation-style-language/schema/raw/master/csl-citation.json",
    }
    return " ADDIN ZOTERO_ITEM CSL_CITATION " + json.dumps(cit, ensure_ascii=False) + " ", plain


def field_open(instr):
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve">{escape(instr)}</w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>')


FIELD_CLOSE = '<w:r><w:fldChar w:fldCharType="end"/></w:r>'


def text_run(t, italic=False):
    font = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>'
    size = '<w:sz w:val="24"/><w:szCs w:val="24"/>'
    rpr = f'<w:rPr>{font}{size}<w:i/></w:rPr>' if italic else f'<w:rPr>{font}{size}</w:rPr>'
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(t)}</w:t></w:r>'


def bib_html_to_runs(h):
    h = re.sub(r'<span class="Z3988".*?</span>', '', h, flags=re.S)
    m = re.search(r'<div class="csl-entry">(.*?)</div>\s*$', h.strip(), flags=re.S)
    if m:
        h = m.group(1)
    h = re.sub(r'</?div[^>]*>', '', h)
    runs = []
    italic = False
    for tok in re.split(r'(<i>|</i>)', h):
        if tok == '<i>':
            italic = True
        elif tok == '</i>':
            italic = False
        elif tok:
            runs.append(text_run(html.unescape(tok), italic))
    return ''.join(runs)


CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'''

DOC_TMPL = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
{body}
<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1800" w:bottom="1440" w:left="1800" w:header="851" w:footer="992" w:gutter="0"/></w:sectPr>
</w:body></w:document>'''


BODY_PPR = ('<w:pPr><w:spacing w:line="360" w:lineRule="auto"/>'
            '<w:ind w:firstLineChars="200" w:firstLine="480"/>'
            '<w:jc w:val="both"/></w:pPr>')
TITLE_PPR = '<w:pPr><w:jc w:val="center"/><w:spacing w:after="240"/></w:pPr>'
BIB_PPR = '<w:pPr><w:ind w:leftChars="200" w:hangingChars="200"/></w:pPr>'


def heading_run(t, size=32):
    rpr = ('<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/>'
           f'<w:b/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>')
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(t)}</w:t></w:r>'


def bib_paras(bundles):
    """One XML paragraph per bundle, wrapped in a single ZOTERO_BIBL field."""
    bib_instr = ' ADDIN ZOTERO_BIBL {"uncited":[],"omitted":[],"custom":[]} CSL_BIBLIOGRAPHY '
    paras = []
    n = len(bundles)
    for idx, b in enumerate(bundles):
        p = '<w:p>' + BIB_PPR
        if idx == 0:
            p += field_open(bib_instr)
        p += bib_html_to_runs(b["bib_html"])
        if idx == n - 1:
            p += FIELD_CLOSE
        p += '</w:p>'
        paras.append(p)
    return paras


def build_docx(body_text, bundles, out_path):
    instr, plain = citation_instr(bundles)
    cite_para = '<w:p>'
    if body_text:
        cite_para += text_run(body_text)
    cite_para += field_open(instr) + text_run(plain) + FIELD_CLOSE
    cite_para += '</w:p>'

    document = DOC_TMPL.format(body=cite_para + "\n" + "\n".join(bib_paras(bundles)))
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", document)


def cmd_cite(args):
    bundles = [get_item_bundle(k) for k in args.keys]
    build_docx(args.text or "", bundles, args.out)
    print(f"written: {args.out}")


def cmd_document(args):
    """Generate a whole document from a JSON spec. Spec shape:
    {"title": "optional heading",
     "paragraphs": [
        [{"text": "..."},
         {"keys": ["KEY"], "suppress_author": true},
         {"text": "..."}],
        ...
     ]}
    """
    with open(args.file, encoding="utf-8") as f:
        spec = json.load(f)
    paras = spec.get("paragraphs")
    if not isinstance(paras, list) or not paras:
        sys.exit('document JSON needs a non-empty "paragraphs" list')
    bundles = {}
    for para in paras:
        if not isinstance(para, list):
            sys.exit('each paragraph must be a list of segments '
                     '([{"text": ...} | {"keys": [...]}, ...])')
        for seg in para:
            for k in seg.get("keys", []):
                bundles.setdefault(k, get_item_bundle(k))

    xml_paras = []
    if spec.get("title"):
        xml_paras.append('<w:p>' + TITLE_PPR + heading_run(spec["title"]) + '</w:p>')
    for para in paras:
        runs = []
        for seg in para:
            if seg.get("text"):
                runs.append(text_run(seg["text"]))
            if seg.get("keys"):
                bs = [dict(bundles[k], suppress_author=seg.get("suppress_author", False))
                      for k in seg["keys"]]
                instr, plain = citation_instr(bs)
                runs.append(field_open(instr) + text_run(plain) + FIELD_CLOSE)
        xml_paras.append('<w:p>' + BODY_PPR + ''.join(runs) + '</w:p>')
    xml_paras.extend(bib_paras([bundles[k] for k in dict.fromkeys(
        k for para in paras for seg in para for k in seg.get("keys", []))]))

    document = DOC_TMPL.format(body="\n".join(xml_paras))
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", document)
    print(f"written: {args.out}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Zotero local add + citation docx fragment generator")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--fulltext", action="store_true",
                   help="search PDF body text as well (qmode=everything)")
    s.add_argument("--tag", help="only items carrying this tag")
    s.add_argument("--collection", help="only items in this collection (by name)")
    s.set_defaults(fn=cmd_search)

    a = sub.add_parser("add")
    a.add_argument("file", help="JSON file with one Zotero item (API format)")
    a.add_argument("--tag", action="append")
    a.add_argument("--collection", help="collection (folder) name to file the item into")
    a.add_argument("--check", action="store_true",
                   help="入库后读回条目与源数据逐字段比对，输出验证结论")
    a.set_defaults(fn=cmd_add)

    ck = sub.add_parser("check",
                        help="验证已入库条目：读回 Zotero 数据，与源 item.json（--source）或 Crossref 权威元数据比对")
    ck.add_argument("key")
    ck.add_argument("--source", help="源 item.json 路径；不给则按条目 DOI 走 Crossref 核验")
    ck.set_defaults(fn=cmd_check)

    dc = sub.add_parser("doctor", help="环境自检：检查 Zotero 版本/开关/账号，缺什么告诉你怎么补")
    dc.add_argument("--json", action="store_true", help="输出结构化 JSON（agent 友好）")
    dc.set_defaults(fn=cmd_doctor)

    sub.add_parser("collections").set_defaults(fn=cmd_collections)

    mc = sub.add_parser("mkcol")
    mc.add_argument("name")
    mc.add_argument("--parent", help="parent collection key")
    mc.set_defaults(fn=cmd_mkcol)

    mv = sub.add_parser("move")
    mv.add_argument("item_key")
    mv.add_argument("collection_key")
    mv.add_argument("--remove", help="collection key to remove the item from")
    mv.set_defaults(fn=cmd_move)

    dl = sub.add_parser("delete")
    dl.add_argument("item_key")
    dl.set_defaults(fn=cmd_delete)

    rc = sub.add_parser("rmcol")
    rc.add_argument("key", help="collection key to delete (items inside are NOT deleted)")
    rc.set_defaults(fn=cmd_rmcol)

    c = sub.add_parser("cite")
    c.add_argument("keys", nargs="+")
    c.add_argument("--text", default="", help="body text before the citation")
    c.add_argument("-o", "--out", default="citation_fragment.docx")
    c.set_defaults(fn=cmd_cite)

    d = sub.add_parser("document",
                       help="generate a whole docx from a JSON spec "
                            "(multi-paragraph, multi-citation, suppress_author)")
    d.add_argument("file", help="JSON spec file (see SKILL.md for shape)")
    d.add_argument("-o", "--out", default="document.docx")
    d.set_defaults(fn=cmd_document)

    args = p.parse_args()
    if args.cmd in ("search", "add", "cite", "document", "collections", "check"):
        ensure_running()
    args.fn(args)


if __name__ == "__main__":
    main()
