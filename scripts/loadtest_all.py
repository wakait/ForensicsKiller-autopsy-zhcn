# -*- coding: utf-8 -*-
"""全量加载回归：把 MANIFEST 里每个 bundle 都从 jar 内以 zh_CN 加载一遍。

输出：通过/失败清单，以及每包中文键数。失败即代表 jar 内资源不可用。
"""
import json
import os
import subprocess
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
ROOT = Path(os.environ.get("AUTOPSY_HOME", r"D:/kit-ascii/autopsy"))
JRE = ROOT / "jre" / "bin"
MAN = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))

bases, jars = [], []
for rel, info in sorted(MAN["bundles"].items()):
    bases.append(rel.replace("\\", "/").replace("/", ".")[:-len(".properties")])
    j = str(ROOT / info["jar"])
    if j not in jars:
        jars.append(j)

cp = os.pathsep.join([str(PACK / "scripts" / "classes")] + jars)
env = dict(os.environ, MSYS2_ARG_CONV_EXCL="*")
cmd = [str(JRE / "java.exe"), "-Duser.language=zh", "-Duser.country=CN",
       "-cp", cp, "LoadCheck"] + bases
r = subprocess.run(cmd, capture_output=True, env=env)
out = r.stdout.decode("gbk", "replace")
print(out[-4000:])
fails = out.count("[MISS]") + out.count("WARN")
print("\n退出码:", r.returncode, "| 异常计数:", fails)
Path(PACK / "QA_LOADTEST.txt").write_text(out, encoding="utf-8")
