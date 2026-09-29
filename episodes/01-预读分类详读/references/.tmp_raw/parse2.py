import json, os
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
for kw in ['AI文献阅读','AI科研','AI工具','AI写作']:
    f = base + 'xhs_30d_' + kw + '.json'
    with open(f, encoding='utf-8') as fh: text = fh.read()
    objs = parse_multi_json(text)
    items=[]
    for o in objs:
        if isinstance(o, dict) and 'items' in o: items=o['items']
    print(f"\n### 关键词: {kw} | 文章数: {len(items)}")
    # 只显示与 文献/论文/科研/读/综述/学术 相关的
    kw_filter = ['文献','论文','科研','读','综述','学术','写','research','SCI','期刊','组会','导师']
    cnt=0
    for i in items:
        t = i.get('title',''); d = str(i.get('desc',''))
        if any(k in t or k in d for k in kw_filter):
            cnt+=1
            print(f"[{i.get('createTime','')}] {t} | 赞{i.get('likedCount','')} 藏{i.get('collectedCount','')} 评{i.get('commentsCount','')} 享{i.get('sharedCount','')} | {i.get('authorNickname','')}({i.get('authorFans','')})")
    print(f"-- 其中主题相关 {cnt} 条")
