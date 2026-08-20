#!/usr/bin/env python3
"""Unit tests for zotero_cite.py (pure functions only, no Zotero needed)."""
import json
import re
import sys
import zipfile

sys.path.insert(0, __file__.rsplit("\\", 1)[0])
import zotero_cite as zc

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok  {name}")
    else:
        FAILURES.append(name)
        print(f"FAIL  {name}  {detail}")


def fake_bundle(key, title="Test Paper", year="2024", cit="(Doe, 2024)", bib="<div class=\"csl-entry\">Doe, J. <i>Test Paper</i>.</div>"):
    return {
        "key": key,
        "uri": f"http://zotero.org/users/0/items/{key}",
        "citation_text": cit,
        "bib_html": bib,
        "data": {
            "itemType": "journalArticle",
            "title": title,
            "date": year,
            "creators": [{"creatorType": "author", "firstName": "Jane", "lastName": "Doe"}],
            "publicationTitle": "Journal of Tests",
            "volume": "1", "issue": "2", "pages": "3-4",
        },
    }


def test_zotero_to_csl():
    csl = zc.zotero_to_csl(fake_bundle("K1")["data"])
    check("csl type", csl["type"] == "article-journal")
    check("csl title", csl["title"] == "Test Paper")
    check("csl author", csl["author"] == [{"family": "Doe", "given": "Jane"}])
    check("csl issued", csl["issued"] == {"date-parts": [[2024]]})
    check("csl container", csl["container-title"] == "Journal of Tests")


def test_strip_tags():
    check("strip_tags", zc.strip_tags('<i>Hello</i> &amp; <b>world</b>') == "Hello & world")


def test_citation_instr_normal():
    instr, plain = zc.citation_instr([fake_bundle("K1")])
    data = json.loads(instr.split("CSL_CITATION ", 1)[1].strip())
    check("instr has item", data["citationItems"][0]["id"] == "K1")
    check("no suppress-author by default",
          "suppress-author" not in data["citationItems"][0])
    check("plain text", plain == "(Doe, 2024)")


def test_citation_instr_suppress():
    b = dict(fake_bundle("K1", cit="(Doe, 2024)"), suppress_author=True)
    instr, plain = zc.citation_instr([b])
    data = json.loads(instr.split("CSL_CITATION ", 1)[1].strip())
    check("suppress-author flag set", data["citationItems"][0].get("suppress-author") is True)
    check("plain renders year only", plain == "(2024)")


def test_bib_html_to_runs():
    out = zc.bib_html_to_runs('<div class="csl-entry">Doe, J. <i>Italics</i> tail.</div>')
    check("italic split", '<w:i/>' in out and '<w:t xml:space="preserve">Doe, J. </w:t>' in out)
    check("no Z3988 leftover", "Z3988" not in out)
    check("italic text kept", "Italics" in out)


def test_field_open_escapes():
    out = zc.field_open(' ADDIN ZOTERO_ITEM CSL_CITATION {"a": "x < y"} ')
    check("instrText escaped", "&lt; y" in out)
    check("fldChar begin", out.count('fldCharType="begin"') == 1)


def test_heading_run():
    out = zc.heading_run("标题", size=28)
    check("heading bold", "<w:b/>" in out)
    check("heading size", 'w:val="28"' in out)
    check("heading text", "标题" in out)


def test_bib_paras():
    paras = zc.bib_paras([fake_bundle("K1"), fake_bundle("K2")])
    joined = "".join(paras)
    check("bib field begin once", joined.count('fldCharType="begin"') == 1)
    check("bib field end once", joined.count('fldCharType="end"') == 1)
    check("bib has entries", "Doe, J. " in joined and "Test Paper" in joined)


def test_build_docx():
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "t.docx")
        zc.build_docx("正文", [fake_bundle("K1")], out)
        with zipfile.ZipFile(out) as z:
            names = z.namelist()
            xml = z.read("word/document.xml").decode("utf-8")
        check("docx parts", "[Content_Types].xml" in names
              and "word/document.xml" in names)
        check("ZOTERO_ITEM instr", "ZOTERO_ITEM CSL_CITATION" in xml)
        check("ZOTERO_BIBL instr", "ZOTERO_BIBL" in xml)
        check("body text", "正文" in xml)


def test_cmd_document_xml():
    import tempfile
    import os
    spec = {
        "title": "论AI与深度思考",
        "paragraphs": [
            [{"text": "作者"}, {"keys": ["K1"], "suppress_author": True},
             {"text": "发现结论"}],
            [{"text": "综述支持"}, {"keys": ["K2"]}],
        ],
    }
    # cmd_document needs live Zotero (get_item_bundle), so test the XML
    # assembly via a stub that bypasses the network.
    real_get = zc.get_item_bundle
    zc.get_item_bundle = lambda k: fake_bundle(k)
    try:
        with tempfile.TemporaryDirectory() as td:
            spec_path = os.path.join(td, "spec.json")
            out = os.path.join(td, "doc.docx")
            with open(spec_path, "w", encoding="utf-8") as f:
                json.dump(spec, f, ensure_ascii=False)
            sys.argv = ["zotero_cite.py", "document", spec_path, "-o", out]
            zc.cmd_document(argparse_stub(spec_path, out))
            with zipfile.ZipFile(out) as z:
                xml = z.read("word/document.xml").decode("utf-8")
    finally:
        zc.get_item_bundle = real_get
    check("heading present", "论AI与深度思考" in xml)
    check("suppress-author count", xml.count("suppress-author") == 1)
    check("field begin count", xml.count('fldCharType="begin"') == 3)  # 2 cites + 1 bib
    check("bib entries", xml.count("Test Paper") >= 2)


class argparse_stub:
    def __init__(self, file, out):
        self.file = file
        self.out = out


if __name__ == "__main__":
    for fn in (test_zotero_to_csl, test_strip_tags, test_citation_instr_normal,
               test_citation_instr_suppress, test_bib_html_to_runs,
               test_field_open_escapes, test_heading_run, test_bib_paras,
               test_build_docx, test_cmd_document_xml):
        print(fn.__name__)
        fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("ALL TESTS PASSED")
