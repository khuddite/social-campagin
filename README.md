# Social Campaign Agent

A multi-agent creative automation pipeline that generates localized social ad campaign assets from a JSON brief. Built with LangGraph, GPT-4o, and FLUX.1.

## What It Does

Given a campaign brief (JSON), the pipeline:

1. **Parses** the brief and resolves existing assets
2. **Writes** ad copy for each product (GPT-4o)
3. **Localizes** copy with cultural adaptation for the target market (GPT-4o)
4. **Generates** hero images for products missing assets (FLUX.1-schnell via HuggingFace)
5. **Composites** final campaign images in 3 aspect ratios (1:1, 9:16, 16:9) with text overlay and brand logo
6. **Checks** brand compliance using vision AI (GPT-4o)
7. **Checks** legal compliance of ad copy (GPT-4o)
8. **Reports** results in a self-contained HTML report

## Architecture

```
Brief Parser → Copy Writer → Localizer → Image Generator → Compositor → Brand Checker → Legal Checker → Reporter
```

Each node is a specialized agent in a LangGraph StateGraph pipeline. State flows through as a typed dictionary.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key (GPT-4o)
- HuggingFace API token (free — sign up at [huggingface.co](https://huggingface.co))

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/social-campaign-agent.git
cd social-campaign-agent

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys
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
- **FLUX.1-schnell** via HuggingFace free tier — best open-source image quality, no local GPU needed
- **Pillow for text overlay** — deterministic rendering (vs. AI text which is unreliable)
- **GPT-4o vision** for brand checking — analyzes final composited images for compliance
- **Jinja2 reporter** (not LLM) — fast, reliable, zero API cost

## Running Tests

```bash
uv run pytest -v
```

## Assumptions & Limitations

- **PoC scope**: This is a proof-of-concept, not production software
- **Rate limits**: HuggingFace free tier may have rate limits for image generation
- **Font**: Uses Inter Bold font; falls back to Pillow default if not available
- **Brand logo**: Expected as a PNG with transparency (RGBA)
- **Image quality**: FLUX.1-schnell is optimized for speed; FLUX.1-dev produces higher quality but is slower
