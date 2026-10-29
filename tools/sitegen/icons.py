"""Picks an icon for a chip label (rules in src/content/icons.json, sprite from tools/make_icons.py)."""
import re

from .config import ROOT, load

_DATA = load("icons")
_SPRITE = ROOT / "assets" / "icons" / "sprite.svg"
SYMBOLS = set(re.findall(r'<symbol id="([^"]+)"', _SPRITE.read_text(encoding="utf8"))) if _SPRITE.exists() else set()
SPRITE_URL = "/assets/icons/sprite.svg"


def _matches(rule, text):
    k, mode = rule["k"], rule.get("mode", "in")
    if mode == "eq":
        return text == k
    if mode == "start":
        return text.startswith(k)
    if mode == "word":
        return re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9+#])", text) is not None
    return k in text


def resolve(label, group=None):
    """Icon id for a label: brand logo if present in the sprite, else the rule's generic glyph."""
    text = label.lower()
    for rule in _DATA["rules"]:
        if _matches(rule, text):
            if rule["i"] in SYMBOLS:
                return rule["i"]
            return rule.get("fb") or _DATA["default"]
    return _DATA["groups"].get(group) or _DATA["default"]


def svg(icon_id):
    return (f'<svg class="ic" aria-hidden="true" focusable="false">'
            f'<use href="{SPRITE_URL}#{icon_id}"/></svg>')


def group_icon(group_id):
    return _DATA["groups"].get(group_id, _DATA["default"])
