from __future__ import annotations

from pathlib import Path
import urllib.request


def ensure_runtime_assets(base_dir: Path) -> None:
    # Ensure icons dir and placeholder icon
    icons_dir = base_dir / "app" / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    app_icon = icons_dir / "app.png"
    if not app_icon.exists():
        # Create a tiny placeholder PNG (1x1) to avoid binary embedding; user can replace
        app_icon.write_bytes(
            bytes.fromhex(
                "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000A4944415408D763F8FFFF3F0005FE02FEA7C28D3D0000000049454E44AE426082"
            )
        )

    # Ensure fonts with an Arabic-capable font
    fonts_dir = base_dir / "app" / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    noto = fonts_dir / "NotoNaskhArabic-Regular.ttf"
    if not noto.exists():
        try:
            url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf"
            urllib.request.urlretrieve(url, noto)
        except Exception:
            # Silent failure; system fallback fonts may still work
            pass

