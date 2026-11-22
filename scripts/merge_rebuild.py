# -*- coding: utf-8 -*-
"""按「多个 zh_*.json 合并」重建指定 bundle，避免 add_bundle 单文件重建冲掉旧译文。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import add_bundle as ab  # noqa

PACK = Path(__file__).resolve().parent.parent
JOBS = {
    "org/netbeans/modules/uihandler/Bundle.properties":
        ["translations/batch4/zh_uihandler.json", "translations/batch7/zh_menu.json"],
    "org/netbeans/modules/options/Bundle.properties":
        ["translations/batch4/zh_options_api.json", "translations/batch7/zh_menu.json"],
    "org/netbeans/spi/quicksearch/Bundle.properties":
        ["translations/batch5/zh_quicksearch.json", "translations/batch7/zh_menu.json"],
    "org/netbeans/modules/javahelp/Bundle.properties":
        ["translations/batch5/zh_misc2.json", "translations/batch7/zh_menu.json"],
}


def main():
    man = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
    for bundle, files in JOBS.items():
        zh = {}
        for f in files:
            d = json.loads((PACK / f).read_text(encoding="utf-8"))
            for it in d["items"]:
                if (it.get("bundle") or d.get("bundle")) == bundle:
                    zh[it["key"]] = it["zh"]
        jar = ab.resolve_jar(bundle)
        keys, translated, tpl, loc = ab.build(jar, bundle, zh)
        man["bundles"][bundle] = {
            "jar": jar.replace("/", "\\"),
            "keys": keys,
            "translated": translated,
            "pack": str(loc.relative_to(PACK)).replace("\\", "/"),
        }
        print("%-56s %3d 键 %3d 中文化" % (bundle.split("/")[-2], keys, translated))
    (PACK / "MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=1),
                                        encoding="utf-8")


if __name__ == "__main__":
    main()
