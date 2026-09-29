import json, glob, os, re

# 用 raw_decode 解析拼接的多个 JSON 对象
def parse_multi_json(text):
    decoder = json.JSONDecoder()
    objs = []
    idx = 0
    while idx < len(text):
        # 跳过空白
        while idx < len(text) and text[idx] in ' \r\n\t':
            idx += 1
        if idx >= len(text):
            break
        try:
            obj, end = decoder.raw_decode(text, idx)
            objs.append(obj)
            idx = end
        except Exception as e:
            idx += 1
    return objs

files = glob.glob('/Coze/Drive/自媒体运营达人/所有对话/主对话/projects/论文写作Skills系列/episodes/01-预读分类详读/references/.tmp_raw/xhs_7d_*.json')
for f in sorted(files):
    kw = os.path.basename(f).replace('xhs_7d_','').replace('.json','')
    with open(f, encoding='utf-8') as fh:
        text = fh.read()
    objs = parse_multi_json(text)
    # 找到包含 items 的对象
    items = []
    related = []
    latest = []
    for o in objs:
        if isinstance(o, dict):
            if 'items' in o:
                items = o['items']
            if 'relatedSearches' in o:
                related = o['relatedSearches']
            if 'latestHotArticles' in o and not items:
                latest = o['latestHotArticles']
    print(f"\n########## 关键词: {kw} | 文章数: {len(items)} | 拓词: {related if isinstance(related,list) else related}")
    for i in items[:50]:
        print(f"[{i.get('createTime','')}] {i.get('title','')} | 赞{i.get('likedCount','')} 藏{i.get('collectedCount','')} 评{i.get('commentsCount','')} 享{i.get('sharedCount','')} | 作者{i.get('authorNickname','')}({i.get('authorFans','')})")
        print(f"   desc: {str(i.get('desc',''))[:80]}")
