"""CLI entry point for the Social Campaign Agent."""

from __future__ import annotations

import json
import os
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()


@click.group()
def cli():
    """Social Campaign Agent — Creative automation for social ad campaigns."""
    load_dotenv()


@cli.command()
@click.option(
    "--brief",
    required=True,
    type=click.Path(exists=True),
    help="Path to the campaign brief JSON file.",
)
@click.option(
    "--output",
    default="./output",
    type=click.Path(),
    help="Output directory for generated assets.",
)
def generate(brief: str, output: str):
    """Generate social campaign assets from a campaign brief."""
    brief_path = Path(brief).resolve()
    output_dir = Path(output).resolve()

    missing = []
    if not os.environ.get("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")

    if missing:
        console.print(
            f"[red]Missing environment variables: {', '.join(missing)}[/red]\n"
            f"Set them in a .env file or export them in your shell."
        )
        raise SystemExit(1)

    raw_brief = json.loads(brief_path.read_text())

    console.print(
        Panel(
            f"[bold]Campaign:[/bold] {raw_brief['campaign_name']}\n"
            f"[bold]Products:[/bold] {len(raw_brief['products'])} | "
            f"[bold]Region:[/bold] {raw_brief['target_region']} ({raw_brief['target_language']})\n"
            f"[bold]Aspect Ratios:[/bold] {', '.join(raw_brief.get('aspect_ratios', ['1:1', '9:16', '16:9']))}",
            title="Social Campaign Agent",
            border_style="cyan",
        )
    )

    from social_campaign.pipeline import build_pipeline

    pipeline = build_pipeline()

    # Ordered list matching the pipeline edge sequence
    steps = [
        ("parse_brief", "Validating campaign brief & resolving assets"),
        ("write_copy", "Writing ad copy with GPT-4o"),
        ("localize_copy", "Localizing & culturally adapting copy"),
        ("plan_backgrounds", "Art-directing background scenes with GPT-4o"),
        ("generate_images", "Generating hero product images with GPT Image"),
        ("generate_backgrounds", "Generating background scenes with GPT Image"),
        ("composite_assets", "Compositing final ads (hero + background + text + logo)"),
        ("generate_report", "Building HTML campaign report"),
    ]
    completed: set[str] = set()

    def _build_display() -> Text:
        lines = Text()
        for node_name, label in steps:
            if node_name in completed:
                lines.append("  ✓ ", style="green")
                lines.append(label, style="green")
            elif node_name == current_node:
                lines.append("  ⟳ ", style="bold cyan")
                lines.append(label, style="bold cyan")
            else:
                lines.append("  · ", style="dim")
                lines.append(label, style="dim")
            lines.append("\n")
        return lines

    result = {}
    current_node = steps[0][0]

    with Live(_build_display(), console=console, refresh_per_second=4) as live:
        for event in pipeline.stream({
            "brief_path": str(brief_path),
            "output_dir": str(output_dir),
        }):
            for node_name, node_result in event.items():
                completed.add(node_name)
                if node_result is not None:
                    result.update(node_result)
                # Advance current_node to the next pending step
                current_node = ""
                for sn, _ in steps:
                    if sn not in completed:
                        current_node = sn
                        break
                live.update(_build_display())

    console.print(f"\n[green]✓ Output saved to {output_dir}[/green]")
    report_path = output_dir / "campaign-report.html"
    if report_path.exists():
        console.print(f"[green]✓ Report: {report_path}[/green]")
