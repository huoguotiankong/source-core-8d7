import json
import re
import base64
import gzip
import subprocess
import tempfile
import os
from pathlib import Path

SRC = Path("sources/novel/qidian-next/qidian-next-beta.json")
STABLE = Path("sources/novel/qidian-next/qidian-next.json")
BASE_REF = "90c2a479ed7e9fb0c348160de479f3c1b0198598"


def git_show(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True, encoding="utf-8")


def obj(x):
    return x[0] if isinstance(x, list) else x


def main():
    base = obj(json.loads(git_show(BASE_REF, str(SRC))))
    cur = obj(json.loads(SRC.read_text(encoding="utf-8")))
    stable = obj(json.loads(STABLE.read_text(encoding="utf-8")))
    base_js = base.get("jsLib", "")
    cur_js = cur.get("jsLib", "")

    fn = "function qfModuleUnpackV41(v){"
    marker = "/* alpha84：lazy module 首次加载并发保护。"
    bs = base_js.find(fn); be = base_js.find(marker, bs)
    cs = cur_js.find(fn); ce = cur_js.find(marker, cs)
    if min(bs, be, cs, ce) < 0:
        raise SystemExit("loader boundary missing")

    print("===== BETA4 LOADER RAW =====")
    print(base_js[bs:be])
    print("===== BETA6 LOADER RAW =====")
    print(cur_js[cs:ce])

    ignored = {"jsLib", "bookSourceComment", "version", "sourceVersion", "versionCode", "sourceVersionCode", "bookSourceName", "bookSourceGroup"}
    print("BETA4_vs_BETA6_TOP_DIFFS", [k for k in sorted(set(base)|set(cur)) if k not in ignored and base.get(k)!=cur.get(k)])
    print("STABLE_vs_BETA4_TOP_DIFFS", [k for k in sorted(set(stable)|set(base)) if k not in ignored and stable.get(k)!=base.get(k)])
    for k in sorted(set(base)|set(stable)):
        if "content" in k.lower() or "chapter" in k.lower():
            bv=base.get(k); sv=stable.get(k); cv=cur.get(k)
            print("FIELD", k, "stable==beta4", sv==bv, "beta4==beta6", bv==cv)
            print("  stable_head", repr(str(sv)[:700]))
            print("  beta4_head ", repr(str(bv)[:700]))

    m = re.search(r"var\s+QF_MOD38_PACK\s*=\s*(\{.*?\});\s*var\s+QF_MOD38_EXPORTS", base_js, re.S)
    ex = re.search(r"var\s+QF_MOD38_EXPORTS\s*=\s*(\{.*?\});", base_js, re.S)
    if not m:
        raise SystemExit("module pack missing")
    pack = json.loads(m.group(1)); exports=json.loads(ex.group(1)) if ex else {}
    print("MODULE_COUNT", len(pack))
    bad=[]; plain=[]
    for name,val in pack.items():
        s=str(val); compressed=s.startswith("gz:")
        if compressed:
            b=s[3:].strip().replace("-","+").replace("_","/"); b += "="*((4-len(b)%4)%4)
            text=gzip.decompress(base64.b64decode(b)).decode("utf-8")
        else:
            text=s; plain.append(name)
        print("MODULE",name,"gz=",compressed,"len=",len(text),"head=",repr(text[:120]),"literal_n_head=",text.startswith("\\n"),"literal_r_head=",text.startswith("\\r"),"slash_n_count=",text.count("\\n"))
        pairs=[json.dumps(n,ensure_ascii=False)+":(typeof "+n+"==='function'?"+n+":null)" for n in exports.get(name,[])]
        wrapped="(function(){\n"+text+"\n;return {"+",".join(pairs)+"};\n})"
        with tempfile.NamedTemporaryFile("w",suffix=".js",delete=False,encoding="utf-8") as tf:
            tf.write("new Function("+json.dumps(wrapped,ensure_ascii=False)+");\n")
            p=tf.name
        try:
            cp=subprocess.run(["node",p],capture_output=True,text=True)
            if cp.returncode!=0: bad.append((name,cp.stderr[:500],repr(text[:240])))
        finally:
            os.unlink(p)
    print("PLAIN_MODULES",plain)
    print("MODULE_PARSE_BAD",bad)
    print("BASE_JS literal_backslash_n",base_js.count("\\n"),"backslash_newline",base_js.count("\\\n"))
    print("CUR_JS literal_backslash_n",cur_js.count("\\n"),"backslash_newline",cur_js.count("\\\n"))

if __name__ == "__main__":
    main()
