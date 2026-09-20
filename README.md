# SeedVR2 API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/bytedance/seedvr2-upscale?utm_source=github&utm_medium=ugc&utm_campaign=seedvr-dev&utm_content=readme-badge&utm_term=tier-a)

SeedVR2 is ByteDance Seed's diffusion-transformer restoration model: instead of interpolating pixels, it regenerates plausible detail, so a blurry, compressed or low-resolution picture comes back sharp rather than merely larger. This package is a Python client for the SeedVR API hosted on Synexa, so one `pip install` and a `run({"image_url": ...})` call return an upscaled image without any weights or GPU on your side.

You get a blocking `run()` that returns when the output is ready, a submit-and-poll mode for batches, webhook delivery on completion, and typed errors. The only dependency is `httpx`. It is meant for photo tools, e-commerce pipelines, archival projects and any service that needs high-quality upscaling as a function call rather than an inference server.

> **Try it now:** [https://synexa.ai/explore/bytedance/seedvr2-upscale](https://synexa.ai/explore/bytedance/seedvr2-upscale?utm_source=github&utm_medium=ugc&utm_campaign=seedvr-dev&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About SeedVR2](#about-seedvr2)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **The 7B checkpoint does not fit a laptop.** SeedVR2 ships in 3B and 7B sizes, and the reference implementation runs high-resolution jobs across multiple datacenter GPUs with sequence parallelism. The hosted endpoint handles that; you call HTTPS.
- **No restoration stack to assemble.** Self-hosting means the DiT weights, the VAE, a matching PyTorch/FlashAttention build and a colour-fix post-processing step. Here the setup is `pip install` and `SYNEXA_API_KEY`.
- **No cold start.** Loading a multi-billion-parameter diffusion model takes minutes on a fresh instance; the hosted model stays resident.
- **$0.004 per image.** A thousand upscales cost four dollars, with nothing billed while idle, which a dedicated GPU running a few jobs an hour cannot match.

## Installation

```bash
pip install git+https://github.com/seedvr-dev/seedvr-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=seedvr-dev&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import seedvr_api

output = seedvr_api.run({
    "image_url": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from seedvr_api import Client

client = Client(api_key="sk-...")
output = client.run({"image_url": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`bytedance/seedvr2-upscale`](https://synexa.ai/explore/bytedance/seedvr2-upscale?utm_source=github&utm_medium=ugc&utm_campaign=seedvr-dev&utm_content=readme-models&utm_term=tier-a) | super-resolution | SeedVR2 restores and upscales images, recovering detail rather than simply interpolating pixels. | $0.004 |

The default model is **`bytedance/seedvr2-upscale`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `bytedance/seedvr2-upscale`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `image_url` | file | yes | — | — | Image to upscale (.jpg/.png/.webp) |
| `upscale_mode` | string | no | `factor` | target, factor | The mode to use for the upscale. If 'target', the upscale factor will be calculated based on the target resolution. If 'factor', the upscale factor will be used directly. |
| `upscale_factor` | number | no | `2` | 1, 10 | Upscaling factor to be used. Will multiply the dimensions with this factor when `upscale_mode` is `factor`. |
| `target_resolution` | string | no | `1080p` | 720p, 1080p, 1440p, 2160p | The target resolution to upscale to when `upscale_mode` is `target`. |
| `seed` | integer | no | `random` | — | The random seed used for the generation process. |
| `noise_scale` | number | no | `0.1` | 0, 1 | The noise scale to use for the generation process. |
| `output_format` | string | no | `jpg` | png, jpg, webp | The format of the output image. |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from seedvr_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About SeedVR2

SeedVR is a family of diffusion-transformer models for image and video restoration from ByteDance's Seed team, published with code and weights at [ByteDance-Seed/SeedVR](https://github.com/ByteDance-Seed/SeedVR). The first model, SeedVR, was presented at CVPR 2025; its central idea is a shifted-window attention scheme that lets a diffusion transformer restore inputs of arbitrary resolution and length without the usual tiling artefacts, treating super-resolution as generation conditioned on the degraded input rather than as interpolation.

SeedVR2 is the follow-up and the model served here. It applies adversarial post-training to the diffusion model so that restoration completes in a single sampling step instead of dozens, which makes it practical for real workloads while keeping the detail-hallucination ability of the diffusion approach. Weights are released in 3B and 7B parameter sizes. Because it generates rather than filters, SeedVR2 is at its best on photographs, compressed web images and AI-generated pictures with soft detail; on line art or text-heavy screenshots a conventional upscaler may be more faithful.

The hosted endpoint takes an `image_url` and returns one upscaled image. `upscale_mode` chooses between `factor` (multiply the input dimensions by `upscale_factor`) and `target` (fit to `target_resolution`); `noise_scale` controls how much freedom the model has to invent texture. Large outputs take longer but cost the same per run, so `target` mode is a convenient way to cap output size.

The endpoint used by this client is `bytedance/seedvr2-upscale`, which is ByteDance's SeedVR2 model served on Synexa for single-image restoration. The open weights and the reference video restoration pipeline are available in the official repository if you want to self-host or process video.

**Official project:** https://github.com/ByteDance-Seed/SeedVR

## Use cases

- **E-commerce catalogue cleanup** — run every supplier-provided product image through `run({"image_url": url, "upscale_mode": "target", "target_resolution": 2048})` so listings share one crisp resolution.
- **Upscaling AI-generated art** — take a 1024 px output from a text-to-image model and pass it with `upscale_factor=2` before printing or using it as a hero image.
- **Restoring compressed social-media images** — recover detail lost to JPEG compression and repeated re-uploads with a moderate `noise_scale`.
- **Old photo digitisation** — feed scanned prints through the endpoint, keeping `seed` fixed so re-runs are reproducible across a family archive.
- **Thumbnail-to-full-size recovery** — when only a small cached copy of an asset survives, use `target` mode to bring it back to the size the layout needs.
- **Batch pre-processing for computer-vision datasets** — submit thousands of low-resolution frames with `wait=False` and a `webhook` and collect the outputs asynchronously.

## FAQ

**Is there a SeedVR API?**

ByteDance publishes SeedVR and SeedVR2 as open weights and code; there is no official hosted API from the research team. This package is a Python client for the `bytedance/seedvr2-upscale` endpoint on Synexa, which serves SeedVR2 for image restoration behind an HTTPS API.

**How much does the SeedVR API cost?**

The hosted endpoint is billed at $0.004 per run, regardless of output size. There is no hourly GPU charge and nothing to pay while idle. New Synexa accounts receive a free trial credit.

**Can I run SeedVR2 without a GPU?**

Yes. This client sends the image to Synexa's GPUs and returns a URL; your side needs only Python 3.8+ and `httpx`. Self-hosting SeedVR2 requires CUDA GPUs with large memory, and the reference pipeline uses multiple cards for high resolutions.

**Does this client work with the ByteDance-Seed/SeedVR repo or ComfyUI?**

No. It does not load local checkpoints or ComfyUI nodes and it does not process video. It is an HTTP client for the hosted single-image endpoint; use the official repository for video restoration or offline inference.

**What input formats does it accept?**

`image_url` (required) must be a publicly reachable `.jpg`, `.png` or `.webp` URL. Optional fields are `upscale_mode` (`factor` or `target`), `upscale_factor` (number), `target_resolution` (pixels), `noise_scale` (number), `seed` (integer) and `output_format`. Output is a URL to the upscaled image.

**Is this the official SeedVR SDK?**

No. This is an independent, MIT-licensed client and is not affiliated with ByteDance. The official project is at https://github.com/ByteDance-Seed/SeedVR.

## Related

- [ByteDance-Seed/SeedVR](https://github.com/ByteDance-Seed/SeedVR) — official SeedVR and SeedVR2 weights, paper links and video restoration code.
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose client for every model on the platform.
- [sczhou/codeformer](https://synexa.ai/explore/sczhou/codeformer) — face-specific restoration to pair with a general upscale.
- [tencentarc/gfpgan](https://synexa.ai/explore/tencentarc/gfpgan) — a lighter face restoration alternative.
- [black-forest-labs/flux-kontext-pro](https://synexa.ai/explore/black-forest-labs/flux-kontext-pro) — edit the image after upscaling it.

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of SeedVR2. Model weights and trademarks belong to their respective owners.
