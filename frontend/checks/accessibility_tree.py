"""Dump the accessibility tree Chrome exposes to screen readers (AT-SPI) and report unnamed controls.

Needs pyatspi and a Chrome started with --force-renderer-accessibility on a session with an AT-SPI bus. For each page,
load it in that Chrome, then run: python3 frontend/checks/accessibility_tree.py
"""
import pyatspi, sys, collections, time
def walk(node, depth=0, out=None):
    out = [] if out is None else out
    try:
        role = node.getRoleName(); name = (node.name or '').strip()
        states = node.getState()
        out.append((role, name, states.contains(pyatspi.STATE_FOCUSABLE), depth))
        for i in range(node.childCount):
            walk(node.getChildAtIndex(i), depth + 1, out)
    except Exception:
        pass
    return out
desk = pyatspi.Registry.getDesktop(0)
chrome = [a for a in (desk.getChildAtIndex(i) for i in range(desk.childCount)) if a and 'chrome' in (a.name or '').lower()]
print('chrome apps', len(chrome))
for app in chrome:
    nodes = walk(app)
    inter = [n for n in nodes if n[2] and n[0] in ('push button','link','entry','combo box','radio button','check box','text','spin button','toggle button','menu item','page tab')]
    unnamed = [n for n in inter if not n[1]]
    print('nodes', len(nodes), 'focusable interactive', len(inter), 'unnamed', len(unnamed))
    print('roles', dict(collections.Counter(n[0] for n in nodes).most_common(14)))
    heads = [n[1] for n in nodes if n[0] == 'heading']
    print('headings', heads[:12])
    print('landmarks', [n[0] + ':' + n[1][:30] for n in nodes if n[0] in ('landmark','navigation','main','document web')][:8])
    for n in inter[:30]: print('  ', n[0], '|', n[1][:60])
