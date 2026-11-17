#!/usr/bin/env python3
"""Собирает compare.html — один самодостаточный файл со всеми вариантами
дашборда из папки variants/ и переключателем в правом нижнем углу.

Запуск из корня репозитория:  python3 tools/build_compare.py
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
VARIANTS = sorted(
    (ROOT / "variants").glob("v*.html"),
    key=lambda p: int(re.sub(r"\D", "", p.stem) or 0),
)
OUT = ROOT / "compare.html"

frames = []
buttons = []
for i, path in enumerate(VARIANTS):
    n = re.sub(r"\D", "", path.stem)
    src = html.escape(path.read_text(encoding="utf-8"), quote=True)
    frames.append(
        f'<iframe class="variant" id="variant-{n}" title="Вариант {n}" '
        f'data-variant="{n}" srcdoc="{src}"{"" if i == 0 else " hidden"}></iframe>'
    )
    buttons.append(
        f'<button type="button" class="vs__btn" role="radio" data-variant="{n}" '
        f'aria-checked="{"true" if i == 0 else "false"}">Вариант {n}</button>'
    )

page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Сравнение вариантов</title>
<style>
  html, body {{ margin: 0; height: 100%; background: #F6F7F8; overflow: hidden; }}
  .variant {{ position: fixed; inset: 0; width: 100%; height: 100%; border: 0; display: block; background: #F6F7F8; }}
  .variant[hidden] {{ display: block; visibility: hidden; pointer-events: none; }}

  /* ===== Переключатель вариантов (правый нижний угол) ===== */
  .vs {{
    position: fixed; right: 16px; bottom: 16px; z-index: 1000;
    display: inline-flex; gap: 4px; padding: 4px;
    background: #333333; border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,.24);
    font: 400 13px/16px "Neue Haas Unica W1G", system-ui, sans-serif;
  }}
  .vs__btn {{
    border: 0; background: transparent; color: rgba(255,255,255,.7);
    height: 36px; padding: 0 14px; border-radius: 9px; cursor: pointer; font: inherit;
    transition: background .15s ease, color .15s ease;
  }}
  .vs__btn:hover {{ color: #FFFFFF; }}
  .vs__btn[aria-checked="true"] {{ background: #FFDD2D; color: rgba(0,0,0,.8); font-weight: 500; }}
  .vs__btn:focus-visible {{ outline: 2px solid #FFDD2D; outline-offset: 2px; }}
</style>
</head>
<body>
{chr(10).join(frames)}
<div class="vs" role="radiogroup" aria-label="Вариант дашборда">
  {chr(10).join("  " + b for b in buttons).strip()}
</div>
<script>
(function () {{
  var frames = Array.prototype.slice.call(document.querySelectorAll('.variant'));
  var btns = Array.prototype.slice.call(document.querySelectorAll('.vs__btn'));
  var current = frames[0];

  // Переносим в новый вариант выбранную вкладку и позицию прокрутки
  function syncState(from, to) {{
    try {{
      var fd = from.contentDocument, td = to.contentDocument;
      var tab = fd.querySelector('.tab[aria-selected="true"]');
      if (tab) {{
        var same = td.getElementById(tab.id);
        if (same && same.getAttribute('aria-selected') !== 'true') same.click();
      }}
      var fs = fd.scrollingElement, ts = td.scrollingElement;
      var ratio = fs.scrollTop / Math.max(1, fs.scrollHeight - fs.clientHeight);
      ts.scrollTop = ratio * Math.max(0, ts.scrollHeight - ts.clientHeight);
    }} catch (e) {{}}
  }}

  function show(n) {{
    var next = document.getElementById('variant-' + n);
    if (!next) return;
    if (next !== current) syncState(current, next);
    frames.forEach(function (f) {{ f.hidden = f !== next; }});
    btns.forEach(function (b) {{ b.setAttribute('aria-checked', b.getAttribute('data-variant') === n ? 'true' : 'false'); }});
    current = next;
    try {{ history.replaceState(null, '', '#v' + n); }} catch (e) {{}}
  }}

  btns.forEach(function (b) {{
    b.addEventListener('click', function () {{ show(b.getAttribute('data-variant')); }});
  }});

  // Клавиши 1, 2, … переключают варианты (и внутри открытого варианта тоже)
  function onKey(e) {{
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (/^[1-9]$/.test(e.key)) show(e.key);
  }}
  document.addEventListener('keydown', onKey);
  frames.forEach(function (f) {{
    f.addEventListener('load', function () {{
      try {{ f.contentDocument.addEventListener('keydown', onKey); }} catch (e) {{}}
    }});
  }});

  var m = /^#v(\\d+)$/.exec(location.hash);
  if (m) show(m[1]);
}})();
</script>
</body>
</html>
"""

OUT.write_text(page, encoding="utf-8")
print(f"compare.html: {len(VARIANTS)} вариант(а), {OUT.stat().st_size // 1024} КБ")
