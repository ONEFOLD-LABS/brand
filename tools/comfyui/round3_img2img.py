# Queue a ComfyUI exploration round for the ONEFOLD mark (Krea-2 Turbo, see concepts/README.md).
# Expects ComfyUI on 127.0.0.1:8188 with krea2_turbo_fp8_scaled, qwen3vl_4b_fp8_scaled and qwen_image_vae.
import json, urllib.request, uuid
API = "http://127.0.0.1:8188"
P = ("Premium logo mark with real depth: a perfectly round geometric ring shaped like the letter O, made of thick matte petrol teal #0e5a64 paper, "
     "a large clean circular counter in the middle. The bottom right quarter of the ring is peeled and folded over once in a big confident curl, "
     "the folded flap is large and shows the warm saffron yellow #f2b630 back side, light catches the curl, the flap casts a soft shadow onto the ring. "
     "Centered on a plain off-white background, soft studio light from the top left, crisp edges, no text, no letters, generous empty space.")
NEG = "text, letters, watermark, square shape, teardrop counter, deformed ring, multiple logos, mockup, frame, clutter, grain, blurry"
def wf(seed, denoise):
    return {
     "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_turbo_fp8_scaled.safetensors", "weight_dtype": "default"}},
     "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2", "device": "default"}},
     "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
     "4": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.4}},
     "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": P}},
     "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEG}},
     "7": {"class_type": "LoadImage", "inputs": {"image": "onefold_b42.png"}},
     "11": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["3", 0]}},
     "8": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["11", 0],
            "seed": seed, "steps": 8, "cfg": 1.0, "sampler_name": "res_multistep", "scheduler": "simple", "denoise": denoise}},
     "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
     "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": f"onefold/bigflap_d{int(denoise*100)}_s{seed}"}},
    }
for seed, dn in [(1, 0.6), (2, 0.6), (3, 0.7), (4, 0.7), (5, 0.8), (6, 0.8)]:
    r = urllib.request.Request(API + "/prompt", data=json.dumps({"prompt": wf(seed, dn), "client_id": str(uuid.uuid4())}).encode(), headers={"Content-Type": "application/json"})
    print(json.load(urllib.request.urlopen(r)).get("prompt_id"), flush=True)
