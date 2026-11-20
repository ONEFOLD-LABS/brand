# Concepts

How the mark was found: three rounds of Krea-2 Turbo on a local ComfyUI. These are raster drafts kept as a record, not logos. The final mark in `logos/` is computed geometry (`tools/make_logo.py`) modelled on the chosen draft.

Setup for all rounds: `krea2_turbo_fp8_scaled` with `qwen3vl_4b_fp8_scaled` (CLIP type `krea2`) and `qwen_image_vae`, AuraFlow sampling shift 3.4, 8 steps, CFG 1.0, `res_multistep` / `simple`, 1024 × 1024. The scripts are in `tools/comfyui/`.

| File | Round | What |
|---|---|---|
| `krea2-round1-flat.webp` | 1 | Flat drafts: folded disc, folded O, folded band, folded square; seeds 11 and 2026 |
| `krea2-round2-depth.webp` | 2 | The same ideas with light, shadow and paper curl; seeds 7, 42 (O) and 99, 314 (disc) |
| `krea2-round3-bigflap.webp` | 3 | Image-to-image from the round-2 draft “O, corner peeled” (seed 42), asking for a larger flap; denoise 0.6–0.8 |
| `krea2-chosen-bigflap.webp` | 3 | The chosen draft: denoise 0.7, seed 3 |

Colours were given in the prompts (petrol `#0e5a64`, saffron `#f2b630`); everything else came from the model.
