#!/usr/bin/env python3
"""Собирает compare.html — один самодостаточный файл со всеми вариантами
дашборда из папки variants/. Переключение версий встроено в «Настройку
отчёта» (шестерёнка) каждого варианта; у вариантов без своей настройки
сборка добавляет шестерёнку с выбором версии. Клавиши 1–9 тоже работают.

Сами файлы в variants/ не меняются: выбор версии добавляется только
внутри compare.html.

Запуск из корня репозитория:  python3 tools/build_compare.py
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Версии, убранные из сравнения (файлы и ветки остаются, вернуть — убрать номер отсюда)
HIDDEN = {"2", "5"}

# Порядок в сравнении: эти версии идут первыми (первая открывается по умолчанию),
# остальные — по номеру файла
FIRST = ["4"]


def _order(p):
    n = re.sub(r"\D", "", p.stem)
    return (FIRST.index(n) if n in FIRST else len(FIRST), int(n or 0))


VARIANTS = [
    p for p in sorted((ROOT / "variants").glob("v*.html"), key=_order)
    if re.sub(r"\D", "", p.stem) not in HIDDEN
]
OUT = ROOT / "compare.html"

# Короткие названия версий для списка в настройке. Новую версию допишите сюда.
NAMES = {
    "1": "Вкладки · исходный вид",
    "2": "Вкладки · настройка блоков",
    "3": "Один лендинг",
    "4": "Лендинг · крупный шрифт",
    "5": "Лендинг · приглушённые цвета",
}

GEAR = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 '
        '0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 '
        '1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 '
        '1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 '
        '2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 '
        '.73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>'
        '<circle cx="12" cy="12" r="3"/></svg>')

# Блок «Версия отчёта», который встраивается в каждый вариант внутри compare.html
PICKER = r"""
<style id="vp-style">
  /* место под переключатель версий внизу страницы сравнения */
  body::after { content: ''; display: block; height: 72px; }
  .vp { padding: 14px 20px 16px; border-bottom: 1px solid var(--tui-border-normal, rgba(0,16,36,.12)); }
  .vp__title { margin: 0 0 8px; font: var(--tui-typo-ui-s); font-weight: 500; color: var(--tui-text-secondary); }
  .vp__list { display: flex; flex-direction: column; gap: 2px; }
  .vp__btn {
    display: flex; align-items: center; gap: 12px; width: 100%; padding: 6px 8px; border: 0; border-radius: 10px;
    background: transparent; text-align: left; cursor: pointer; font: var(--tui-typo-ui-m); color: var(--tui-text-primary);
    transition: background .15s ease;
  }
  .vp__btn:hover { background: var(--tui-background-neutral-1); }
  .vp__btn:focus-visible { outline: 2px solid var(--tui-text-action); outline-offset: 1px; }
  .vp__btn[aria-checked="true"] { background: var(--tui-brand-t-bank); font-weight: 500; }
  .vp__num {
    flex-shrink: 0; min-width: 1.75em; height: 1.75em; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center;
    background: var(--tui-background-neutral-1); font-weight: 500;
  }
  .vp__btn[aria-checked="true"] .vp__num { background: rgba(255,255,255,.6); }
  .vp__hint { margin: 8px 0 0; font: var(--tui-typo-ui-s); color: var(--tui-text-tertiary); }

  /* шестерёнка и окошко для версий без своей настройки */
  .vp-head { display: flex; align-items: center; gap: 8px; }
  .vp-gear {
    width: 48px; height: 48px; padding: 0; border-radius: 12px; cursor: pointer; flex-shrink: 0;
    background: var(--tui-background-base); border: 1px solid var(--tui-border-normal); color: var(--tui-text-secondary);
    display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 1px 2px rgba(0,0,0,.04);
  }
  .vp-gear:hover { color: var(--tui-text-primary); }
  .vp-gear:focus-visible { outline: 2px solid var(--tui-text-action); outline-offset: 2px; }
  .vp-gear svg { width: 20px; height: 20px; }
  .vp-gear[aria-expanded="true"] { background: var(--tui-brand-t-bank); border-color: var(--tui-brand-t-bank); color: rgba(0,0,0,.8); }
  .vp-pop {
    position: fixed; top: 16px; right: 16px; z-index: 60; width: 360px; max-width: calc(100% - 32px);
    background: var(--tui-background-base); border-radius: 16px; box-shadow: 0 12px 40px rgba(0,0,0,.18);
  }
  .vp-pop[hidden] { display: none; }
  .vp-pop .vp { border-bottom: 0; }
  .vp-pop__head { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px 0; }
  .vp-pop__title { margin: 0; font: var(--tui-typo-ui-l-bold); }
  .vp-pop__close { width: 32px; height: 32px; border: 0; border-radius: 8px; background: var(--tui-background-neutral-1); color: var(--tui-text-secondary); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
  .vp-pop__close svg { width: 16px; height: 16px; }
</style>
<script>
(function () {
  if (window.parent === window) return;
  var V = __DATA__;
  function pickerHtml() {
    return '<div class="vp"><p class="vp__title">Версия отчёта</p><div class="vp__list" role="radiogroup" aria-label="Версия отчёта">' +
      V.list.map(function (v) {
        var on = v.n === V.current;
        return '<button type="button" class="vp__btn" role="radio" data-vp="' + v.n + '" aria-checked="' + on + '">' +
          '<span class="vp__num">' + v.n + '</span><span>' + v.name + '</span></button>';
      }).join('') +
      '</div><p class="vp__hint">Быстро: клавиши 1–' + V.list.length + '</p></div>';
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-vp]');
    if (!b) return;
    if (b.getAttribute('data-vp') !== V.current) parent.postMessage({ type: 'compare-variant', n: b.getAttribute('data-vp') }, '*');
  });

  var drawer = document.getElementById('drawer');
  if (drawer) {
    // своя «Настройка отчёта» есть — добавляем выбор версии в её начало
    var head = drawer.querySelector('.drawer__head');
    head.insertAdjacentHTML('afterend', pickerHtml());
    return;
  }

  // своей настройки нет — добавляем шестерёнку и окошко с выбором версии
  var period = document.querySelector('.page-head .period');
  if (!period) return;
  var wrap = document.createElement('div');
  wrap.className = 'vp-head';
  period.parentNode.insertBefore(wrap, period);
  wrap.appendChild(period);
  wrap.insertAdjacentHTML('beforeend', '<button type="button" class="vp-gear" id="vp-gear" aria-expanded="false" aria-controls="vp-pop" aria-label="Настройка отчёта" title="Настройка отчёта">' + V.gear + '</button>');
  document.body.insertAdjacentHTML('beforeend',
    '<div class="vp-pop" id="vp-pop" role="dialog" aria-label="Настройка отчёта" hidden>' +
      '<div class="vp-pop__head"><h2 class="vp-pop__title">Настройка отчёта</h2>' +
      '<button type="button" class="vp-pop__close" aria-label="Закрыть"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>' +
      pickerHtml() + '</div>');
  var gear = document.getElementById('vp-gear'), pop = document.getElementById('vp-pop');
  function setPop(open) {
    pop.hidden = !open;
    gear.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) { var cur = pop.querySelector('[aria-checked="true"]'); if (cur) cur.focus(); }
  }
  gear.addEventListener('click', function () { setPop(pop.hidden); });
  pop.querySelector('.vp-pop__close').addEventListener('click', function () { setPop(false); gear.focus(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !pop.hidden) { setPop(false); gear.focus(); } });
  document.addEventListener('click', function (e) {
    if (!pop.hidden && !pop.contains(e.target) && !gear.contains(e.target)) setPop(false);
  });
})();
</script>
"""

# В сравнении версии нумеруются по порядку (1, 2, 3, …), независимо от номера файла
items = []
for i, p in enumerate(VARIANTS):
    src_n = re.sub(r"\D", "", p.stem)
    items.append({"n": str(i + 1), "name": NAMES.get(src_n, "Вариант " + src_n)})

frames = []
for i, path in enumerate(VARIANTS):
    n = items[i]["n"]
    data = json.dumps({"current": n, "list": items, "gear": GEAR}, ensure_ascii=False).replace("</", "<\\/")
    page_src = path.read_text(encoding="utf-8")
    cut = page_src.rindex("</body>")
    page_src = page_src[:cut] + PICKER.replace("__DATA__", data) + page_src[cut:]
    frames.append(
        f'<iframe class="variant" id="variant-{n}" title="Вариант {n}: {html.escape(items[i]["name"])}" '
        f'data-variant="{n}" srcdoc="{html.escape(page_src, quote=True)}"{"" if i == 0 else " hidden"}></iframe>'
    )

# Переключатель версий поверх отчёта — всегда виден, не зависит от шестерёнки и клавиатуры
vbar = "".join(
    f'<button type="button" class="vbar__btn" role="tab" data-show="{it["n"]}" '
    f'aria-selected="{"true" if i == 0 else "false"}" title="{html.escape(it["name"])}">'
    f'<span class="vbar__num">{it["n"]}</span><span class="vbar__name">{html.escape(it["name"])}</span></button>'
    for i, it in enumerate(items)
)

page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Итоги направлений</title>
<style>
  html, body {{ margin: 0; height: 100%; background: #F6F7F8; overflow: hidden; }}
  .variant {{ position: fixed; inset: 0; width: 100%; height: 100%; border: 0; display: block; background: #F6F7F8; }}
  .variant[hidden] {{ display: block; visibility: hidden; pointer-events: none; }}
  .vbar {{
    position: fixed; left: 50%; bottom: 16px; transform: translateX(-50%); z-index: 100;
    display: flex; gap: 4px; padding: 4px; max-width: calc(100% - 32px); box-sizing: border-box;
    background: rgba(255,255,255,.94); border-radius: 14px; box-shadow: 0 6px 24px rgba(0,0,0,.16), 0 0 0 1px rgba(0,16,36,.08);
    -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
    font: 400 14px/18px "Neue Haas Unica W1G", system-ui, -apple-system, sans-serif;
  }}
  .vbar__btn {{
    display: inline-flex; align-items: center; gap: 8px; min-height: 40px; padding: 0 14px 0 8px; border: 0; border-radius: 10px;
    background: transparent; color: rgba(0,0,0,.72); font: inherit; cursor: pointer; white-space: nowrap; -webkit-tap-highlight-color: transparent;
  }}
  .vbar__btn:hover {{ background: rgba(0,16,36,.06); }}
  .vbar__btn:focus-visible {{ outline: 2px solid #428BF9; outline-offset: 1px; }}
  .vbar__btn[aria-selected="true"] {{ background: #FFDD2D; color: rgba(0,0,0,.9); font-weight: 600; }}
  .vbar__num {{
    display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 7px;
    background: rgba(0,16,36,.07); font-weight: 600;
  }}
  .vbar__btn[aria-selected="true"] .vbar__num {{ background: rgba(255,255,255,.6); }}
  @media (max-width: 720px) {{
    .vbar__name {{ display: none; }}
    .vbar__btn {{ padding: 0 8px; }}
  }}
  @media print {{ .vbar {{ display: none; }} }}
</style>
</head>
<body>
{chr(10).join(frames)}
<nav class="vbar" role="tablist" aria-label="Версия отчёта">{vbar}</nav>
<script>
(function () {{
  var frames = Array.prototype.slice.call(document.querySelectorAll('.variant'));
  var current = frames[0];

  function settingsOpen(doc) {{
    var d = doc.getElementById('drawer');
    if (d) return d.classList.contains('is-open');
    var p = doc.getElementById('vp-pop');
    return !!p && !p.hidden;
  }}
  function openSettings(doc) {{
    if (settingsOpen(doc)) return;
    var g = doc.getElementById('gear') || doc.getElementById('vp-gear');
    if (g) g.click();
  }}

  // Переносим в новую версию вкладку, позицию прокрутки и открытую настройку
  function syncState(from, to) {{
    try {{
      var fd = from.contentDocument, td = to.contentDocument;
      var tab = fd.querySelector('.tab[aria-selected="true"]');
      if (tab) {{
        var same = td.getElementById(tab.id);
        if (same && same.getAttribute('aria-selected') !== 'true') same.click();
      }}
      if (settingsOpen(fd)) {{
        openSettings(td);
        var cur = td.querySelector('[data-vp][aria-checked="true"]');
        if (cur) cur.focus({{ preventScroll: true }});
      }}
      var fs = fd.scrollingElement, ts = td.scrollingElement;
      var ratio = fs.scrollTop / Math.max(1, fs.scrollHeight - fs.clientHeight);
      ts.scrollTop = ratio * Math.max(0, ts.scrollHeight - ts.clientHeight);
    }} catch (e) {{}}
  }}

  function show(n) {{
    var next = document.getElementById('variant-' + n);
    if (!next || next === current) return;
    syncState(current, next);
    frames.forEach(function (f) {{ f.hidden = f !== next; }});
    current = next;
    Array.prototype.forEach.call(document.querySelectorAll('.vbar__btn'), function (b) {{
      b.setAttribute('aria-selected', b.getAttribute('data-show') === String(n) ? 'true' : 'false');
    }});
    try {{ history.replaceState(null, '', '#v' + n); }} catch (e) {{}}
  }}

  // Выбор версии в «Настройке отчёта» внутри варианта
  window.addEventListener('message', function (e) {{
    var ok = frames.some(function (f) {{ return f.contentWindow === e.source; }});
    if (ok && e.data && e.data.type === 'compare-variant') show(String(e.data.n));
  }});

  // Клавиши 1, 2, … переключают версии (кроме ввода текста)
  function onKey(e) {{
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) && t.type !== 'checkbox')) return;
    if (/^[1-9]$/.test(e.key)) show(e.key);
  }}
  document.addEventListener('keydown', onKey);
  frames.forEach(function (f) {{
    f.addEventListener('load', function () {{
      try {{ f.contentDocument.addEventListener('keydown', onKey); }} catch (e) {{}}
    }});
  }});

  var m = /^#v(\\d+)$/.exec(location.hash);
  document.querySelector('.vbar').addEventListener('click', function (e) {{
    var b = e.target.closest('[data-show]');
    if (b) show(b.getAttribute('data-show'));
  }});

  if (m) show(m[1]);
}})();
</script>
</body>
</html>
"""

OUT.write_text(page, encoding="utf-8")
print(f"compare.html: {len(VARIANTS)} вариант(а), {OUT.stat().st_size // 1024} КБ")
