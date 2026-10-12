#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = "litsearch/1.0 (literature-search skill)"
TIMEOUT = 20


def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def http_get(url, headers=None, retries=2, timeout=TIMEOUT):
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429 and attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1)
                continue
            raise
    raise last_err


def http_post(url, data, headers=None, retries=2, timeout=TIMEOUT):
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(1)
                continue
            raise
    raise last_err


def inv_index_to_text(inv):
    if not inv:
        return None
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def search_openalex(query, limit, year_from=None, year_to=None, sort=None):
    params = {"search": query, "per-page": min(limit, 50)}
    key = os.environ.get("OPENALEX_API_KEY")
    if key:
        params["api_key"] = key
    mailto = os.environ.get("LITSEARCH_MAILTO")
    if mailto:
        params["mailto"] = mailto
    filters = []
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")
    if year_to:
        filters.append(f"to_publication_date:{year_to}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    if sort == "cited":
        params["sort"] = "cited_by_count:desc"
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = json.loads(http_get(url))
    out = []
    for w in data.get("results", []):
        loc = w.get("primary_location") or {}
        src = loc.get("source") or {}
        pdf = loc.get("pdf_url")
        oa = w.get("open_access") or {}
        out.append({
            "title": w.get("title"),
            "authors": [a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author")],
            "year": w.get("publication_year"),
            "venue": src.get("display_name"),
            "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
            "url": w.get("id"),
            "pdf_url": pdf or oa.get("oa_url"),
            "abstract": inv_index_to_text(w.get("abstract_inverted_index")),
            "citations": w.get("cited_by_count"),
            "source": "openalex",
        })
    return out


def search_s2(query, limit, year_from=None, year_to=None, sort=None):
    params = {
        "query": query,
        "limit": min(limit, 20),
        "fields": "title,authors,year,venue,externalIds,abstract,citationCount,openAccessPdf,url",
    }
    if year_from or year_to:
        params["year"] = f"{year_from or ''}-{year_to or ''}"
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
    headers = {}
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if key:
        headers["x-api-key"] = key
    data = json.loads(http_get(url, headers=headers))
    out = []
    for p in data.get("data", []):
        ext = p.get("externalIds") or {}
        pdf = p.get("openAccessPdf") or {}
        out.append({
            "title": p.get("title"),
            "authors": [a.get("name") for a in p.get("authors", [])],
            "year": p.get("year"),
            "venue": p.get("venue"),
            "doi": ext.get("DOI"),
            "url": p.get("url"),
            "pdf_url": pdf.get("url"),
            "abstract": p.get("abstract"),
            "citations": p.get("citationCount"),
            "source": "semantic_scholar",
        })
    return out


def search_arxiv(query, limit, year_from=None, year_to=None, sort=None):
    params = {
        "search_query": f"all:{query}",
        "max_results": min(limit, 30),
        "sortBy": "relevance" if sort != "cited" else "submittedDate",
    }
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    raw = http_get(url)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(raw)
    out = []
    for e in root.findall("a:entry", ns):
        published = e.findtext("a:published", default="", namespaces=ns)
        year = int(published[:4]) if published[:4].isdigit() else None
        if year_from and year and year < year_from:
            continue
        if year_to and year and year > year_to:
            continue
        arxiv_id = e.findtext("a:id", default="", namespaces=ns)
        out.append({
            "title": " ".join((e.findtext("a:title", default="", namespaces=ns) or "").split()),
            "authors": [a.findtext("a:name", default="", namespaces=ns) for a in e.findall("a:author", ns)],
            "year": year,
            "venue": "arXiv",
            "doi": None,
            "url": arxiv_id,
            "pdf_url": arxiv_id.replace("/abs/", "/pdf/") if arxiv_id else None,
            "abstract": " ".join((e.findtext("a:summary", default="", namespaces=ns) or "").split()),
            "citations": None,
            "source": "arxiv",
        })
    return out


def search_crossref(query, limit, year_from=None, year_to=None, sort=None):
    params = {"query": query, "rows": min(limit, 50)}
    mailto = os.environ.get("LITSEARCH_MAILTO")
    if mailto:
        params["mailto"] = mailto
    filters = []
    if year_from:
        filters.append(f"from-pub-date:{year_from}-01-01")
    if year_to:
        filters.append(f"until-pub-date:{year_to}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    if sort == "cited":
        params["sort"] = "is-referenced-by-count"
        params["order"] = "desc"
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    data = json.loads(http_get(url))
    out = []
    for w in data.get("message", {}).get("items", []):
        authors = []
        for a in w.get("author", []):
            name = " ".join(x for x in [a.get("given"), a.get("family")] if x)
            if name:
                authors.append(name)
        issued = w.get("issued", {}).get("date-parts", [[None]])
        out.append({
            "title": (w.get("title") or [None])[0],
            "authors": authors,
            "year": issued[0][0] if issued and issued[0] else None,
            "venue": (w.get("container-title") or [None])[0],
            "doi": w.get("DOI"),
            "url": w.get("URL"),
            "pdf_url": None,
            "abstract": w.get("abstract"),
            "citations": w.get("is-referenced-by-count"),
            "source": "crossref",
        })
    return out


BUCKET_MAP = {"0": 0, "1-10": 5, "11-50": 30, "51-200": 125, "200-1000": 600, "1000-5000": 3000, "5000+": 10000}


def bucket_to_count(bucket):
    return BUCKET_MAP.get(bucket) if bucket else None


def search_aminer(query, limit, year_from=None, year_to=None, sort=None):
    key = os.environ.get("AMINER_API_KEY")
    if not key:
        return []
    hdrs = {"Authorization": key, "X-Platform": "opencode"}
    params = {"title": query, "page": 1, "size": min(limit * 2, 20)}
    url = "https://datacenter.aminer.cn/gateway/open_platform/api/paper/search?" + urllib.parse.urlencode(params)
    data = json.loads(http_get(url, headers=hdrs))
    results = data.get("data", [])
    if not results:
        return []
    ids = [r["id"] for r in results]
    body = json.dumps({"ids": ids}).encode("utf-8")
    try:
        info_resp = http_post(
            "https://datacenter.aminer.cn/gateway/open_platform/api/paper/info",
            body,
            headers={"Content-Type": "application/json;charset=utf-8", **hdrs}
        )
        info_data = json.loads(info_resp)
    except Exception:
        info_data = {"data": []}
    info_map = {d["id"]: d for d in info_data.get("data", [])}
    out = []
    for r in results:
        info = info_map.get(r.get("id"), {})
        year = r.get("year") or info.get("year")
        if year_from and year and year < year_from:
            continue
        if year_to and year and year > year_to:
            continue
        authors = [a.get("name") or a.get("name_zh") for a in info.get("authors", []) if a.get("name") or a.get("name_zh")] or ([r.get("first_author")] if r.get("first_author") else [])
        out.append({
            "title": info.get("title") or r.get("title"),
            "authors": authors,
            "year": year,
            "venue": ((info.get("venue") or {}).get("raw") or (info.get("venue") or {}).get("raw_zh") or r.get("venue_name")),
            "doi": r.get("doi"),
            "url": f"https://www.aminer.cn/pub/{r.get('id')}" if r.get("id") else None,
            "pdf_url": None,
            "abstract": info.get("abstract_slice"),
            "citations": bucket_to_count(r.get("n_citation_bucket")),
            "source": "aminer",
        })
    return out[:limit]


SOURCES = {
    "openalex": search_openalex,
    "s2": search_s2,
    "arxiv": search_arxiv,
    "crossref": search_crossref,
    "aminer": search_aminer,
}


def norm_key(rec):
    if rec.get("doi"):
        return "doi:" + rec["doi"].lower()
    return "t:" + "".join((rec.get("title") or "").lower().split())


def cmd_search(args):
    if args.source == "all":
        sources = ["openalex", "crossref", "arxiv"]
        if os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
            sources.append("s2")
        if os.environ.get("AMINER_API_KEY"):
            sources.append("aminer")
    else:
        sources = [args.source]
    results, errors = [], {}
    fetch_n = min(args.limit * 3, 50) if args.sort == "cited" else args.limit
    for name in sources:
        try:
            results.extend(SOURCES[name](args.query, fetch_n, args.year_from, args.year_to, None))
        except Exception as e:
            errors[name] = str(e)
    seen, deduped = set(), []
    for r in results:
        k = norm_key(r)
        if k in seen:
            continue
        seen.add(k)
        deduped.append(r)
    if args.sort == "cited":
        deduped.sort(key=lambda r: (r.get("citations") or 0), reverse=True)
    payload = {"query": args.query, "count": len(deduped[:args.limit]), "results": deduped[:args.limit]}
    if errors:
        payload["errors"] = errors
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_fetch(args):
    doi = args.doi.strip()
    params = {}
    key = os.environ.get("OPENALEX_API_KEY")
    if key:
        params["api_key"] = key
    mailto = os.environ.get("LITSEARCH_MAILTO")
    if mailto:
        params["mailto"] = mailto
    qs = ("?" + urllib.parse.urlencode(params)) if params else ""
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi) + qs
    try:
        w = json.loads(http_get(url))
        loc = w.get("primary_location") or {}
        rec = {
            "title": w.get("title"),
            "authors": [a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author")],
            "year": w.get("publication_year"),
            "venue": (loc.get("source") or {}).get("display_name"),
            "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
            "url": w.get("id"),
            "pdf_url": loc.get("pdf_url") or (w.get("open_access") or {}).get("oa_url"),
            "abstract": inv_index_to_text(w.get("abstract_inverted_index")),
            "citations": w.get("cited_by_count"),
            "source": "openalex",
        }
        print(json.dumps(rec, ensure_ascii=False, indent=2))
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"DOI not found or API error: {e}"}, ensure_ascii=False))
        sys.exit(1)


def probe(label, url, headers=None):
    try:
        http_get(url, headers=headers, retries=0, timeout=10)
        print(f"[OK]   {label}")
        return True
    except Exception as e:
        print(f"[FAIL] {label} -- {e}")
        return False


def cmd_doctor(args):
    print("=== literature-search 环境自检 ===")
    print(f"[INFO] Python {sys.version.split()[0]}")

    oa_key = os.environ.get("OPENALEX_API_KEY")
    params = {"search": "test", "per-page": 1}
    if oa_key:
        params["api_key"] = oa_key
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    probe(f"OpenAlex 数据源（{'已检测到 Key，走认证通道' if oa_key else '匿名模式'}）", url)
    if not oa_key:
        print("[WARN] 未配置 OPENALEX_API_KEY。匿名目前可用但官方已要求 Key，1 分钟免费申请: https://openalex.org/settings/api")

    probe("Crossref 数据源", "https://api.crossref.org/works?query=test&rows=1")
    probe("arXiv 数据源", "https://export.arxiv.org/api/query?search_query=all:test&max_results=1")

    s2_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if s2_key:
        probe("Semantic Scholar 数据源（已检测到 Key）",
              "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1",
              headers={"x-api-key": s2_key})
    else:
        print("[WARN] 未配置 SEMANTIC_SCHOLAR_API_KEY，S2 源默认关闭。免费申请: https://www.semanticscholar.org/product/api#api-key-form")

    aminer_key = os.environ.get("AMINER_API_KEY")
    if aminer_key:
        probe("AMiner 数据源（已检测到 Key）",
              "https://datacenter.aminer.cn/gateway/open_platform/api/paper/search?title=test&page=1&size=1",
              headers={"Authorization": aminer_key, "X-Platform": "opencode"})
    else:
        print("[WARN] 未配置 AMINER_API_KEY，AMiner 源默认关闭。申请: https://open.aminer.cn/open/board?tab=control")

    print()
    print('下一步: python litsearch.py search "你的研究主题" --limit 3')
    print("完整配置引导见 skill 目录下的 SETUP.md")


def main():
    load_env()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="litsearch")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--source", choices=["all"] + list(SOURCES), default="all")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--year-from", type=int, default=None)
    p.add_argument("--year-to", type=int, default=None)
    p.add_argument("--sort", choices=["relevance", "cited"], default="relevance")
    p.set_defaults(func=cmd_search)
    f = sub.add_parser("fetch")
    f.add_argument("doi")
    f.set_defaults(func=cmd_fetch)
    d = sub.add_parser("doctor")
    d.set_defaults(func=cmd_doctor)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
