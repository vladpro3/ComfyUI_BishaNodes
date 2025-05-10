# ComfyUI BishaNodes
**Custom Nodes for ComfyUI to Simplify Multi-Resolution Workflows**

## 🌟 **Simple Size Picker**
A utility node for ComfyUI that streamlines image generation across **50+ standardized resolutions** (from 512px to 8K), including ultra-wide formats like 21:9 and niche ratios (e.g., 8:1). Perfect for batch workflows, social media assets, or multi-display projects.

---

### 📋 **Features**
- **Preset Resolutions**:
    - ✅ **Square** (1:1) – 512×512 to 2048×2048
    - ✅ **Portrait** (2:3, 9:16) – 512×768 to 1080×1920
    - ✅ **Landscape** (16:9, 3:2) – 768×512 to 3840×2160 (4K)
    - ✅ **Ultra-Wide** (21:9, 32:9) – 2560×1080 to 7680×2160
    - ✅ **Exotic Ratios** (e.g., 9600×1200 at 8:1)

- **User-Friendly**:
    - Dropdown menu with organized categories (Square, Portrait, etc.).
    - Tooltips with resolution details (e.g., `"DCI 2K (2048×1080 ≈17:9)"`).

---

### 🛠 **Installation**
1. Clone this repo into your `ComfyUI/custom_nodes/` folder:
   ```bash
   git clone https://github.com/yourusername/ComfyUI_BishaNodes.git
   ```  
2. Restart ComfyUI.

---

### 🎮 **Usage**
1. Add the **`Simple Size Picker`** node to your workflow.
2. Select a resolution from the dropdown (e.g., `"3840×1600 (12:5)"`).
3. Connect to your sampler/generator – the node auto-handles dimensions.

![Example Workflow](https://example.com/path/to/screenshot.png) *(placeholder for screenshot)*

---

### 🌐 **Use Cases**
- **Social Media**: Quickly generate assets for Instagram (1:1), Twitter (16:9), and Stories (9:16).
- **Ultra-Wide Wallpapers**: Batch-create 3440×1440 or 5120×2160 backgrounds.
- **AI Art Experiments**: Test latent space in extreme ratios (e.g., 9600×1200).

---

### 💡 **Why This Node?**
- **No Manual Math**: Skip calculating `width/height` for each ratio.
- **Future-Proof**: Easily extendable with new resolutions (edit `resolutions.json`).

