"""CLI entry point for the Social Campaign Agent."""

from __future__ import annotations

import os
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

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

    import json

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

    node_labels = {
        "parse_brief": "Parsing brief",
        "write_copy": "Generating ad copy",
        "localize_copy": "Localizing copy",
        "generate_images": "Generating images",
        "composite_assets": "Compositing assets",
        "generate_report": "Generating report",
    }

    result = {}
    for event in pipeline.stream({
        "brief_path": str(brief_path),
        "output_dir": str(output_dir),
    }):
        for node_name, node_result in event.items():
            label = node_labels.get(node_name, node_name)
            console.print(f"  [green]✓[/green] {label}")
            if node_result is not None:
                result.update(node_result)

    console.print()
    console.print(f"\n[green]✓ Output saved to {output_dir}[/green]")
    report_path = output_dir / "campaign-report.html"
    if report_path.exists():
        console.print(f"[green]✓ Report: {report_path}[/green]")
