import json
import re
import base64
import gzip
import subprocess
from pathlib import Path

SRC = Path("sources/novel/qidian-next/qidian-next-beta.json")
BASE_REF = "90c2a479ed7e9fb0c348160de479f3c1b0198598"


def git_show(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True, encoding="utf-8")


def main():
    base_arr = json.loads(git_show(BASE_REF, str(SRC)))
    cur_arr = json.loads(SRC.read_text(encoding="utf-8"))
    base = base_arr[0] if isinstance(base_arr, list) else base_arr
    cur = cur_arr[0] if isinstance(cur_arr, list) else cur_arr
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
    print("===== BETA4 LOADER REPR =====")
    print(repr(base_js[bs:be]))
    print("===== BETA6 LOADER RAW =====")
    print(cur_js[cs:ce])
    print("===== BETA6 LOADER REPR =====")
    print(repr(cur_js[cs:ce]))

    ignored = {"jsLib", "bookSourceComment", "version", "sourceVersion", "versionCode", "sourceVersionCode"}
    diffs = []
    for k in sorted(set(base) | set(cur)):
        if k in ignored:
            continue
        if base.get(k) != cur.get(k):
            diffs.append(k)
    print("TOP_LEVEL_NON_RUNTIME_DIFFS", diffs)
    for k in sorted(base):
        if "content" in k.lower() or "chapter" in k.lower():
            bv = base.get(k)
            cv = cur.get(k)
            print("FIELD", k, "same=", bv == cv, "base_head=", repr(str(bv)[:500]), "cur_head=", repr(str(cv)[:500]))

    m = re.search(r"var\s+QF_MOD38_PACK\s*=\s*(\{.*?\});\s*var\s+QF_MOD38_EXPORTS", base_js, re.S)
    ex = re.search(r"var\s+QF_MOD38_EXPORTS\s*=\s*(\{.*?\});", base_js, re.S)
    if not m:
        raise SystemExit("module pack missing")
    pack = json.loads(m.group(1))
    exports = json.loads(ex.group(1)) if ex else {}
    print("MODULE_COUNT", len(pack))
    bad = []
    for name, val in pack.items():
        s = str(val)
        if not s.startswith("gz:"):
            text = s
        else:
            b = s[3:].strip().replace("-", "+").replace("_", "/")
            b += "=" * ((4 - len(b) % 4) % 4)
            text = gzip.decompress(base64.b64decode(b)).decode("utf-8")
        print("MODULE", name, "len=", len(text), "head=", repr(text[:80]), "literal_n_head=", text.startswith("\\n"), "slash_n_count=", text.count("\\n"))
        pairs = []
        for n in exports.get(name, []):
            pairs.append(json.dumps(n, ensure_ascii=False) + ":(typeof " + n + "==='function'?" + n + ":null)")
        wrapped = "(function(){\n" + text + "\n;return {" + ",".join(pairs) + "};\n})"
        cp = subprocess.run(["node", "-e", "new Function(process.argv[1]);", wrapped], capture_output=True, text=True)
        if cp.returncode != 0:
            bad.append((name, cp.stderr[:300], repr(text[:160])))
    print("MODULE_PARSE_BAD", bad)

    print("BASE_JS literal \\n count", base_js.count("\\n"), "backslash-newline count", base_js.count("\\\n"))
    print("CUR_JS literal \\n count", cur_js.count("\\n"), "backslash-newline count", cur_js.count("\\\n"))


if __name__ == "__main__":
    main()
