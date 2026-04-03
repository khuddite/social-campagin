# Social Campaign Agent

A multi-agent creative automation pipeline that generates localized social ad campaign assets from a JSON brief. Built with LangGraph, GPT-4o, and DALL·E 3.

## What It Does

Given a campaign brief (JSON), the pipeline:

1. **Parses** the brief and resolves existing assets
2. **Writes** ad copy for each product (GPT-4o)
3. **Localizes** copy with cultural adaptation for the target market (GPT-4o)
4. **Plans** scene and lighting per product from audience, region, campaign message, and brand (GPT-4o)
5. **Generates** hero images for products missing assets (DALL·E 3)
6. **Integrates** each hero into one scene per product via **`images.edit`** (default **DALL·E 2**, single API call from a square PNG with transparent margins)
7. **Crops** that master to 1:1, 9:16, and 16:9, then adds logo and localized copy
8. **Reports** results in a self-contained HTML report

## Architecture

```
Brief Parser → Copy Writer → Localizer → Background Planner → Hero Generator → Scene Integrator (DALL·E 2 edit) → Compositor → Reporter
```

Each node is a specialized agent in a LangGraph StateGraph pipeline. State flows through as a typed dictionary.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key (GPT-4o, DALL·E 3 for optional heroes, and **DALL·E 2** `images.edit` for scene integration — set `OPENAI_IMAGE_EDIT_MODEL` only if your account supports another edit model, e.g. `gpt-image-1.5`)

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

### Output

```
output/
├── citrus-burst-sparkling-water/
│   ├── 1_1/campaign.png       # 1080×1080 (Instagram feed)
│   ├── 9_16/campaign.png      # 1080×1920 (Instagram story)
│   └── 16_9/campaign.png      # 1920×1080 (Facebook/Twitter)
├── berry-bliss-smoothie/
│   ├── 1_1/campaign.png
│   ├── 9_16/campaign.png
│   └── 16_9/campaign.png
└── campaign-report.html        # Full campaign report
```

## Input Format

See `campaign_brief_example.json` for a complete example. The brief includes:

- **Campaign name** and **message**
- **Brand** config (name, colors, logo, guidelines)
- **Products** (name, description, features, optional hero image)
- **Target** region, language, and audience
- **Aspect ratios** to generate

## Key Design Decisions

- **LangGraph StateGraph** for multi-agent orchestration — typed state, clear data flow, easy to test
- **DALL·E 3** via OpenAI — one API key for LLM and image generation
- **Pillow for text overlay** — deterministic rendering (vs. AI text which is unreliable)
- **Jinja2 reporter** (not LLM) — fast, reliable, zero API cost
- **Text-free heroes** — prompts forbid on-image typography (models often hallucinate nonsense labels). Real headline/body are added in Pillow, not in the generated photo.

## Running Tests

```bash
uv run pytest -v
```

## Assumptions & Limitations

- **PoC scope**: This is a proof-of-concept, not production software
- **Rate limits / billing**: OpenAI usage limits and DALL·E pricing apply to image generation
- **Font**: Uses Inter Bold font; falls back to Pillow default if not available
- **Brand logo**: Expected as a PNG with transparency (RGBA)
- **Image quality**: DALL·E 3 uses `quality=standard` by default; switch to `hd` in `openai_image_client.py` for higher fidelity at higher cost
