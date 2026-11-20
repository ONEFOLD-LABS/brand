#!/usr/bin/env python3
"""Compile tokens/tokens.json into CSS custom properties (light, dark, and the shared scales)."""
import json
import sys


def main():
    t = json.load(open(sys.argv[1]))
    themes = [th["id"] for th in t["color"]["themes"]]
    first = themes[0]

    def val(tok, theme):
        v = tok["value"]
        return v if isinstance(v, str) else v.get(theme, v[first])

    out = [f"/* {t['name']} — generated from tokens.json by tools/tokens_css.py; do not edit */"]
    out.append(":root {")
    for tok in t["color"]["tokens"]:
        out.append(f"  --{tok['name']}: {val(tok, first)};")
    for fam in ("spacing", "radius"):
        for tok in t[fam]["tokens"]:
            out.append(f"  --{tok['name']}: {tok['value']};")
    for key, stack in t["type"]["families"].items():
        out.append(f"  --font-{key}: {stack};")
    out.append("}")
    for theme in themes[1:]:
        changed = [tok for tok in t["color"]["tokens"] if val(tok, theme) != val(tok, first)]
        body = "\n".join(f"  --{tok['name']}: {val(tok, theme)};" for tok in changed)
        scheme = "  color-scheme: dark;\n" if theme == "dark" else ""
        if theme == "dark":
            out.append(f'@media (prefers-color-scheme: dark) {{\n  :root:not([data-theme="{first}"]) {{\n' + body.replace("\n", "\n  ").replace("  --", "    --", 1) + "\n    color-scheme: dark;\n  }\n}")
        out.append(f'[data-theme="{theme}"] {{\n{body}\n{scheme}}}')
    for g in t["type"]["groups"]:
        for st in g["styles"]:
            fam = st.get("family", g["family"])
            decl = [f"font-family: var(--font-{fam})", f"font-size: {st['fontSize']}", f"line-height: {st['lineHeight']}", f"font-weight: {st['fontWeight']}"]
            if "letterSpacing" in st:
                decl.append(f"letter-spacing: {st['letterSpacing']}")
            if st["name"].startswith("display"):
                decl.append("font-stretch: 125%")
            out.append(f".{st['name']} {{ " + "; ".join(decl) + "; }")
    print("\n".join(out))


if __name__ == "__main__":
    main()
