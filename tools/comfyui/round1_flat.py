# Queue a ComfyUI exploration round for the ONEFOLD mark (Krea-2 Turbo, see concepts/README.md).
# Expects ComfyUI on 127.0.0.1:8188 with krea2_turbo_fp8_scaled, qwen3vl_4b_fp8_scaled and qwen_image_vae.
import json, sys, urllib.request, time, uuid
API = "http://127.0.0.1:8188"
STYLE = ("Flat vector logo mark, minimalist geometric emblem, centered on a plain off-white background, "
         "solid flat colors only: deep petrol teal #0e5a64 and saffron yellow #f2b630, crisp clean edges, "
         "no gradients, no shadows, no texture, no text, no letters, generous empty space around the mark, "
         "professional brand identity design, Swiss modernist style. ")
CONCEPTS = {
 "disc":   "A perfect circle made of one sheet of paper, its top right segment folded over once along a straight diagonal line, the folded flap shows the yellow back side.",
 "square": "A single square sheet folded exactly once along a diagonal, forming a crisp triangle flap, origami-like simplicity, one fold only.",
 "letterO":"A bold geometric letter O shape built from a thick ring, one part of the ring folded over like paper, showing a yellow underside.",
 "ribbon": "One continuous flat band folded once at a sharp angle, forming an abstract monogram, paper fold, two-tone front and back.",
}
NEG = "text, letters, words, watermark, signature, 3d render, photo, gradient, shadow, texture, noise, blurry, multiple logos, mockup, frame, border"
def wf(prompt, seed, prefix):
    return {
     "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors", "weight_dtype": "default"}},
     "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2", "device": "default"}},
     "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
     "4": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.4}},
     "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
     "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEG}},
     "7": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
     "8": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["7", 0],
            "seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "res_multistep", "scheduler": "simple", "denoise": 1.0}},
     "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
     "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}},
    }
def post(p):
    r = urllib.request.Request(API + "/prompt", data=json.dumps({"prompt": p, "client_id": str(uuid.uuid4())}).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))["prompt_id"]
ids = []
for name, c in CONCEPTS.items():
    for seed in (11, 2026):
        ids.append((name, seed, post(wf(STYLE + c, seed, f"onefold/{name}_{seed}"))))
print("queued", len(ids), flush=True)
while True:
    h = json.load(urllib.request.urlopen(API + "/history"))
    done = [i for i in ids if i[2] in h]
    for n, s, pid in done:
        st = h[pid].get("status", {})
        if st.get("status_str") == "error": print("ERROR", n, s, json.dumps(st)[:500], flush=True)
    if len(done) == len(ids): break
    time.sleep(2)
print("done", flush=True)
