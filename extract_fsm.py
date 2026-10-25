# -*- coding: utf-8 -*-
"""用 UnityPy + TypeTreeGenerator 解析 PlayMaker FSM / uGUI Text，提取游戏文本 v3"""
import os, sys, json, struct, collections
import UnityPy
from UnityPy.helpers import TypeTreeGenerator

GAME_DATA = r"D:\Program Files (x86)\Steam\steamapps\common\Lakeview Cabin 2\Lakeview Cabin 2_Data"
MANAGED = os.path.join(GAME_DATA, "Managed")
PROJ = r"D:\StaticHanHua\Projects\lakeview-cabin-2"
OUT = os.path.join(PROJ, "fsm_text_extract.json")

ttg = TypeTreeGenerator.TypeTreeGenerator("2019.4.34f1")
ttg.load_local_dll_folder(MANAGED)
print("dlls loaded:", len(ttg.get_loaded_dll_names()), flush=True)

paths = [os.path.join(GAME_DATA, fn) for fn in os.listdir(GAME_DATA)
         if fn.startswith("level") or (fn.startswith("sharedassets") and fn.endswith(".assets"))
         or fn in ("resources.assets", "globalgamemanagers.assets")]
env = UnityPy.load(*paths)
print("files loaded:", len(env.files), flush=True)

by_name = {os.path.basename(f).lower(): sf for f, sf in env.files.items()}

script_map = {}
for full, sf in env.files.items():
    objs = sf.objects.values() if isinstance(sf.objects, dict) else sf.objects
    for obj in objs:
        if obj.type.name != "MonoScript":
            continue
        try:
            ms = obj.read()
            ns = ms.m_Namespace or ""
            fullname = (ns + "." + ms.m_ClassName) if ns else ms.m_ClassName
            script_map[(id(sf), obj.path_id)] = (ms.m_AssemblyName, fullname)
        except Exception:
            pass
print("monoscripts:", len(script_map), flush=True)

def parse_pptr(raw, off):
    f = struct.unpack_from("<i", raw, off)[0]
    p = struct.unpack_from("<q", raw, off + 4)[0]
    return f, p

def script_of(obj):
    raw = obj.get_raw_data()
    if len(raw) < 32:
        return None
    off = 12 + 1
    off = (off + 3) & ~3
    sc_f, sc_p = parse_pptr(raw, off)
    if sc_p == 0:
        return None
    sf = obj.assets_file
    if sc_f == 0:
        return script_map.get((id(sf), sc_p))
    if 0 < sc_f <= len(sf.externals):
        base = os.path.basename(sf.externals[sc_f - 1].path).lower()
        target = by_name.get(base)
        if target is not None:
            return script_map.get((id(target), sc_p))
    return None

node_cache = {}
def get_nodes(asm, fullname):
    key = (asm, fullname)
    if key in node_cache:
        return node_cache[key]
    nodes = None
    try:
        a = asm[:-4] if asm.endswith(".dll") else asm
        nodes = ttg.get_nodes_up(a, fullname)
    except Exception:
        nodes = None
    node_cache[key] = nodes
    return nodes

def arr(v):
    """UnityPy 数组容器 -> list"""
    if isinstance(v, dict):
        v = v.get("Array", v.get("data"))
    if isinstance(v, list):
        return v
    return []

results = []
fail_class = collections.Counter()

def add(val, kind, fn, pid, obj_name, var_name):
    if isinstance(val, str) and val.strip():
        results.append({
            "value": val, "kind": kind, "file": fn, "path_id": pid,
            "obj_name": obj_name, "var_name": var_name,
        })

def handle_fsm(tree, fn, pid):
    fsm = tree.get("fsm")
    if not isinstance(fsm, dict):
        return 0
    name = tree.get("m_Name", "")
    n = 0
    # 1) 全局字符串变量
    for item in arr(fsm.get("variables", {}).get("stringVariables")):
        if isinstance(item, dict):
            add(item.get("value"), "fsmVar", fn, pid, name, item.get("name", ""))
            n += 1
    # 2) 状态 Action 参数
    for st in arr(fsm.get("states")):
        if not isinstance(st, dict):
            continue
        ad = st.get("actionData")
        if not isinstance(ad, dict):
            continue
        for item in arr(ad.get("fsmStringParams")):
            if isinstance(item, dict):
                add(item.get("value"), "fsmActionStr", fn, pid, name, st.get("name", ""))
                n += 1
        for s in arr(ad.get("stringParams")):
            if isinstance(s, str):
                add(s, "actionStr", fn, pid, name, st.get("name", ""))
                n += 1
    return n

for full, sf in env.files.items():
    fn = os.path.basename(full)
    if fn == "globalgamemanagers.assets":
        continue
    n_ok = n_fail = n_text = 0
    objs = sf.objects.values() if isinstance(sf.objects, dict) else sf.objects
    for obj in objs:
        if obj.type.name != "MonoBehaviour":
            continue
        sk = script_of(obj)
        if not sk:
            n_fail += 1
            fail_class[("<noscript>", fn)] += 1
            continue
        nodes = get_nodes(*sk)
        if nodes is None:
            n_fail += 1
            fail_class[(sk[1], "")] += 1
            continue
        try:
            tree = obj.read_typetree(nodes)
        except Exception:
            n_fail += 1
            fail_class[("<readfail>" + sk[1], "")] += 1
            continue
        n_ok += 1
        cls = sk[1]
        if cls == "PlayMakerFSM":
            n_text += handle_fsm(tree, fn, obj.path_id)
        for tk in ("m_Text", "m_text"):
            t = tree.get(tk)
            if isinstance(t, str) and t.strip():
                add(t, "uguiText", fn, obj.path_id, tree.get("m_Name", ""), cls)
                n_text += 1
    print(f"{fn}: ok={n_ok} fail={n_fail} text={n_text}", flush=True)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print(f"\ntotal: {len(results)} -> {OUT}", flush=True)
print("\ntop fail classes:")
for (cls, f_), c in fail_class.most_common(15):
    print(f"  {c:6d}  {cls}  {f_}")
