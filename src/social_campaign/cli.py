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
    if not os.environ.get("HF_API_TOKEN"):
        missing.append("HF_API_TOKEN")

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

    with console.status("[bold cyan]Running pipeline...") as status:
        status.update("[bold cyan]Parsing brief...")
        result = pipeline.invoke({
            "brief_path": str(brief_path),
            "output_dir": str(output_dir),
        })

    console.print()
    brief_data = result.get("brief")
    if brief_data:
        for product in brief_data.products:
            slug = product.slug
            brand_result = result.get("brand_check_results", {}).get(slug)
            legal_result = result.get("legal_check_results", {}).get(slug)

            brand_str = "[green]PASS[/green]" if brand_result and brand_result.passed else "[red]FAIL[/red]"
            legal_str = "[green]PASS[/green]" if legal_result and legal_result.passed else "[yellow]FLAGS[/yellow]"

            console.print(f"  [bold]{product.name}[/bold] — Brand: {brand_str} | Legal: {legal_str}")

            if legal_result and legal_result.flags:
                for flag in legal_result.flags:
                    console.print(f"    [yellow]⚠ {flag}[/yellow]")

    console.print(f"\n[green]✓ Output saved to {output_dir}[/green]")
    report_path = output_dir / "campaign-report.html"
    if report_path.exists():
        console.print(f"[green]✓ Report: {report_path}[/green]")
