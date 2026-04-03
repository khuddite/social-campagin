# Social Campaign Agent

A multi-agent creative automation pipeline that generates localized social ad campaign assets from a JSON brief. Built with LangGraph, GPT-4o, and GPT Image (gpt-image-1.5).

## What It Does

Given a campaign brief (JSON), the pipeline:

1. **Validates** the brief and resolves existing product assets
2. **Writes** punchy ad copy for each product (GPT-4o)
3. **Localizes** copy with cultural adaptation for the target market and language (GPT-4o)
4. **Art-directs** background scenes — plans mood, lighting, and color direction per product (GPT-4o)
5. **Generates hero product images** with branded packaging on transparent backgrounds (gpt-image-1.5) — skips products that already have hero images
6. **Generates background scenes** tailored to the campaign's audience, region, and brand (gpt-image-1.5)
7. **Composites** final ads — layers background + product hero + localized text + brand logo for three aspect ratios (1:1, 9:16, 16:9)
8. **Reports** results in a self-contained HTML report with thumbnails

## Architecture

```
Brief Parser → Copy Writer → Localizer → Background Planner → Hero Generator → Background Generator → Compositor → Reporter
```

Eight specialized agents in a LangGraph StateGraph pipeline. Each agent is a pure function that reads from and writes to a shared typed state dictionary.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key — powers GPT-4o (text agents) and gpt-image-1.5 (image generation)

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/social-campaign-agent.git
cd social-campaign-agent

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key
```

### Run

```bash
uv run social-campaign generate --brief campaign_brief_example.json --output ./output
```

The CLI shows a live progress display with each pipeline step:

```
  ✓ Validating campaign brief & resolving assets
  ✓ Writing ad copy with GPT-4o
  ⟳ Localizing & culturally adapting copy
  · Art-directing background scenes with GPT-4o
  · Generating hero product images with GPT Image
  · Generating background scenes with GPT Image
  · Compositing final ads (hero + background + text + logo)
  · Building HTML campaign report
```

### Output

```
output/
├── proflow-750-insulated-bottle/
│   ├── hero_base.png             # Product cutout (transparent PNG)
│   ├── background.png            # Generated background scene
│   ├── 1_1/campaign.png          # 1080×1080 (Instagram feed)
│   ├── 9_16/campaign.png         # 1080×1920 (Instagram/TikTok story)
│   └── 16_9/campaign.png         # 1920×1080 (Facebook/Twitter)
├── chargeup-electrolyte-mix-citrus/
│   └── ...
└── campaign-report.html           # HTML report with all assets
```

## Input Format

See `campaign_brief_example.json` for a complete example. The brief includes:

- **Campaign name** and **message** — drives the creative direction
- **Brand** config — name, colors, logo path, and tone/guidelines
- **Products** — name, description, key features, and optional hero image path
- **Target** region, language, and audience — drives localization and background art direction
- **Aspect ratios** — which sizes to generate (e.g. `["1:1", "9:16", "16:9"]`)

Products with a `hero_image` path reuse that asset; products without get a hero generated automatically.

## Key Design Decisions

- **LangGraph StateGraph** for multi-agent orchestration — typed state, clear data flow, easy to test each agent independently
- **gpt-image-1.5** for all image generation — transparent product cutouts (`background="transparent"`) and opaque background scenes (`background="opaque"`) from one model
- **Separate background + product compositing** — backgrounds are generated independently from product images, then layered together with Pillow. This gives full control over product placement, sizing, and text overlay
- **Aspect-aware product scaling** — products scale differently per ratio (e.g. 95% width on 9:16 stories, 90% on 1:1 squares) with edge-bleed support for landscape products on tall frames
- **Pillow for text and logo overlay** — deterministic rendering with playful fonts (Permanent Marker headlines, Raleway body) and automatic CJK fallback (Arial Unicode) for non-Latin scripts
- **Jinja2 reporter** (not LLM-powered) — fast, reliable, zero API cost

## Running Tests

```bash
uv run pytest -v
```

## Assumptions & Limitations

- **PoC scope** — proof-of-concept for demonstrating creative automation, not production software
- **API costs** — OpenAI billing applies to GPT-4o and gpt-image-1.5 calls (~2 image generations per product)
- **Font rendering** — Latin scripts use Permanent Marker (headlines) and Raleway Medium (body). Non-Latin scripts (Japanese, Korean, Chinese, Arabic, etc.) automatically fall back to Arial Unicode
- **Brand logo** — expected as a PNG with transparency (RGBA) for clean compositing
- **Background art direction** — the planner avoids mentioning product-category words to prevent the image model from generating unwanted objects (e.g. bottles) in backgrounds
