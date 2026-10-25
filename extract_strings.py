# -*- coding: utf-8 -*-
"""扫描 Unity 序列化文件中的长度前缀字符串 + 反编译C#字符串字面量"""
import os, re, struct, sys, json, hashlib

GAME_DATA = r"D:\Program Files (x86)\Steam\steamapps\common\Lakeview Cabin 2\Lakeview Cabin 2_Data"
PROJ = r"D:\StaticHanHua\Projects\lakeview-cabin-2"
OUT = os.path.join(PROJ, "string_scan.json")

# 1. 扫描二进制资产文件
bin_files = []
for fn in os.listdir(GAME_DATA):
    if fn.startswith("level") or fn.startswith("sharedassets") and fn.endswith(".assets") or fn in ("resources.assets", "globalgamemanagers", "globalgamemanagers.assets"):
        if fn.endswith(".assets") or fn.startswith("level") or fn == "globalgamemanagers":
            bin_files.append(fn)
# 修正过滤：排除 .resS/.resource 流文件
bin_files = [f for f in set(bin_files) if not f.endswith((".resS", ".resource"))]

word_re = re.compile(r'^[A-Za-z][A-Za-z0-9\'",.!?:;()&%$#@*+=/_\-\s\\<>{}\[\]]*$')
results = {}  # string -> {files: set(), count}

def looks_like_text(s):
    if not (3 <= len(s) <= 500):
        return False
    if not word_re.match(s):
        return False
    # 必须含至少一个空格或为单词(>=4字母) —— 排除标识符/路径/哈希
    if " " in s:
        letters = sum(c.isalpha() for c in s)
        if letters / max(len(s), 1) < 0.5:
            return False
        return True
    if len(s) >= 5 and s.isalpha():
        return True
    return False

def scan_binary(path, label):
    with open(path, "rb") as f:
        data = f.read()
    n = len(data)
    i = 0
    found = 0
    while i < n - 4:
        ln = struct.unpack_from("<i", data, i)[0]
        if 3 <= ln <= 500 and i + 4 + ln <= n:
            raw = data[i+4:i+4+ln]
            try:
                s = raw.decode("utf-8")
            except UnicodeDecodeError:
                i += 1
                continue
            if looks_like_text(s):
                # 长度前缀可信度检查：前后字节确认（字符串后面通常跟别的字段）
                key = s
                ent = results.setdefault(key, {"files": set(), "count": 0})
                ent["files"].add(label)
                ent["count"] += 1
                found += 1
                i += 4 + ln
                continue
        i += 1

for fn in sorted(bin_files):
    p = os.path.join(GAME_DATA, fn)
    sz = os.path.getsize(p)
    print(f"scan {fn} ({sz//1024}KB)", flush=True)
    scan_binary(p, fn)

# 2. 扫描反编译C#字符串
cs_root = os.path.join(PROJ, "decompiled", "Assembly-CSharp")
str_lit = re.compile(r'"((?:[^"\\\n]|\\.){3,200})"')
cs_count = 0
for dirpath, dirs, files in os.walk(cs_root):
    for fn in files:
        if not fn.endswith(".cs"):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            txt = open(fp, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for m in str_lit.finditer(txt):
            s = m.group(1)
            if looks_like_text(s) and " " in s:
                ent = results.setdefault(s, {"files": set(), "count": 0})
                ent["files"].add("Assembly-CSharp.cs")
                ent["count"] += 1
                cs_count += 1

out = {s: {"files": sorted(v["files"]), "count": v["count"]} for s, v in results.items()}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"\ntotal unique strings: {len(out)} (from cs: {cs_count} occurrences)")
