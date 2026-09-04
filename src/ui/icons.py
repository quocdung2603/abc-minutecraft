"""SVG icon helpers — return an SVG string for the given name.

Danh sách icon: upload, audio, gear, check, download, clipboard,
arrow_right, sparkle, document.
"""
import streamlit as st


def _svg(width=24, height=24, stroke="currentColor", **attrs) -> str:
    """Base SVG wrapper. Override stroke via the stroke param."""
    attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    return (f'<svg width="{width}" height="{height}" viewBox="0 0 24 24" '
            f'fill="none" stroke="{stroke}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" {attrs_str}></svg>')


# --- Icon functions -----------------------------------------------------

def upload() -> str:
    """Upload/arrow-up icon."""
    return _svg(stroke="var(--svg-stroke)", width=22, height=22) + (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>'
    )


def audio() -> str:
    """Audio/music note icon."""
    return _svg(stroke="var(--svg-stroke)", width=18, height=18) + (
        '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>'
    )


def gear() -> str:
    """Gear/cog icon."""
    return _svg(stroke="var(--svg-stroke)", width=22, height=22) + (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06'
        'a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09'
        'A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83'
        'l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09'
        'A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0'
        'l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09'
        'a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83'
        'l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09'
        'a1.65 1.65 0 0 0-1.51 1z"/>'
    )


def check() -> str:
    """Check/checkmark icon."""
    return _svg(stroke="#16a34a", width=18, height=18) + (
        '<polyline points="20 6 9 17 4 12"/>'
    )


def download() -> str:
    """Download/arrow-down icon."""
    return _svg(stroke="var(--svg-stroke)", width=22, height=22) + (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>'
    )


def clipboard() -> str:
    """Clipboard/list icon."""
    return _svg(stroke="var(--svg-stroke)", width=20, height=20) + (
        '<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/>'
        '<line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/>'
        '<line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>'
    )


def arrow_right() -> str:
    """Arrow right icon."""
    return _svg(stroke="var(--svg-stroke)", width=22, height=22) + (
        '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>'
    )


def sparkle() -> str:
    """Sparkle/star icon."""
    return _svg(stroke="var(--svg-stroke)", width=22, height=22) + (
        '<path d="M12 2L13.09 8.26L19 7L14.74 11.91L21 14L14.74 12.09L19 17L13.09 15.74L12 22L10.91 15.74L5 17L9.26 12.09L3 14L9.26 11.91L5 7L10.91 8.26L12 2Z"/>'
    )


def document() -> str:
    """Document/page icon."""
    return _svg(stroke="var(--svg-stroke)", width=34, height=34) + (
        '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>'
        '<polyline points="14 2 14 8 20 8"/>'
        '<path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>'
    )


# --- Generic helpers ----------------------------------------------------

def icon(name: str, size: int = 22) -> str:
    """Return SVG HTML string for a named icon.

    Args:
        name: One of: upload, audio, gear, check, download,
              clipboard, arrow_right, sparkle, document.
        size: Pixel size (default 22).

    Returns:
        Full <svg>...</svg> HTML string.
    """
    table = {
        "upload": upload,
        "audio": audio,
        "gear": gear,
        "check": check,
        "download": download,
        "clipboard": clipboard,
        "arrow_right": arrow_right,
        "sparkle": sparkle,
        "document": document,
    }
    fn = table.get(name, document)
    # Replace width/height in the returned string
    return fn().replace('width="22"', f'width="{size}"').replace('width="18"', f'width="{size}"').replace('width="20"', f'width="{size}"').replace('width="34"', f'width="{size}"')


def lucide(name: str, size: int = 22) -> str:
    """Alias for icon() — compatible with Lucide naming convention."""
    return icon(name, size)
