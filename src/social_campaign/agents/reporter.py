"""Node 8: Generate an HTML campaign report from pipeline results."""

from __future__ import annotations

import base64
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from social_campaign.models import CampaignState

_TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates"


def _make_thumbnail(image_path: str, max_size: int = 400) -> str:
    """Create a base64-encoded thumbnail from an image file."""
    from PIL import Image

    img = Image.open(image_path)
    img.thumbnail((max_size, max_size))
    import io

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def generate_report(state: CampaignState) -> dict:
    """Render the HTML campaign report."""
    brief = state["brief"]
    output_dir = Path(state["output_dir"])

    thumbnails: dict[str, dict[str, str]] = {}
    composited = state.get("composited_assets", {})
    for slug, assets in composited.items():
        thumbnails[slug] = {}
        for ratio_key, path in assets.items():
            if Path(path).exists():
                thumbnails[slug][ratio_key] = _make_thumbnail(path)

    total_assets = sum(len(a) for a in composited.values())
    brand_results = state.get("brand_check_results", {})
    legal_results = state.get("legal_check_results", {})
    brand_pass_count = sum(1 for r in brand_results.values() if r.passed)
    legal_flags_count = sum(len(r.flags) for r in legal_results.values())

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,
    )
    template = env.get_template("report.html.j2")

    html = template.render(
        brief=brief,
        copy_variants=state.get("copy_variants", {}),
        localized_copy=state.get("localized_copy", {}),
        composited_assets=composited,
        brand_check_results=brand_results,
        legal_check_results=legal_results,
        thumbnails=thumbnails,
        total_assets=total_assets,
        brand_pass_count=brand_pass_count,
        legal_flags_count=legal_flags_count,
    )

    report_path = output_dir / "campaign-report.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(html)

    return {}
