import json, glob, os
def parse_multi_json(text):
    decoder = json.JSONDecoder(); objs, idx = [], 0
    while idx < len(text):
        while idx < len(text) and text[idx] in ' \r\n\t': idx += 1
        if idx >= len(text): break
        try:
            obj, end = decoder.raw_decode(text, idx); objs.append(obj); idx = end
        except Exception: idx += 1
    return objs
base='/Coze/Drive/自媒体运营达人/所有对话/主对话/projects/论文写作Skills系列/episodes/01-预读分类详读/references/.tmp_raw/'
files = glob.glob(base+'gzh_*.json')
for f in sorted(files):
    kw = os.path.basename(f).replace('gzh_','').replace('.json','')
    with open(f, encoding='utf-8') as fh: text=fh.read()
    objs = parse_multi_json(text)
    arts=[]
    for o in objs:
        if isinstance(o, dict) and 'articles' in o: arts=o['articles']
    print(f"\n### 公众号关键词: {kw} | 文章数: {len(arts)}")
    for a in arts[:40]:
        print(f"[{a.get('publicTime','')}] {a.get('title','')} | 阅读{a.get('clicksCount','')} 赞{a.get('likeCount','')} 享{a.get('shareCount','')} 评{a.get('commentsCount','')} | {a.get('author','')} | 总分{a.get('totalScore','')}")
