# ComfyUI BishaNodes
**Custom Nodes for ComfyUI to Simplify Multi-Resolution and Prompt Workflows**

## 🌟 **Nodes Overview**

### 1. Simple Size Picker
### 2. Empty Latent Size Picker
### 3. Create Prompts With Text From File

---

## 📋 **Features**

### 🖼️ **Resolution Nodes**
#### **Simple Size Picker**
- **30+ Standardized Resolutions** (512px to 8K):
  - ✅ **Square** (1:1) – 512×512 to 2048×2048
  - ✅ **Portrait** (2:3, 9:16) – 512×768 to 1080×1920
  - ✅ **Landscape** (16:9, 3:2) – 768×512 to 3840×2160 (4K)
  - ✅ **Ultra-Wide** (21:9, 32:9) – 2560×1080 to 7680×2160
  - ✅ **Exotic Ratios** (e.g., 9600×1200 at 8:1)
- **User-Friendly**:
  - Categorized dropdown menu with tooltips
  - Zero-configuration workflow integration

#### **Empty Latent Size Picker** (Extended Version)
- All features of Simple Size Picker **PLUS**:
- 🚀 **Auto-Generated Latent Output**:
  - Directly connects to samplers
  - Eliminates manual "Empty Latent Image" nodes
  - Preserves selected dimensions in latent space

### 📝 **Prompt Engineering Node**
#### **Create Prompts With Text From File**
- **Batch Prompt Generation**:
  - 🔄 Combine base text with dynamic content from files
  - 🎛️ Control output quantity with `results` parameter
- **File-Based Variability**:
  - Supports .txt files with line-separated entries
  - Random line selection for diverse outputs
- **Use Cases**:
  - Character variations (e.g., "a portrait of [name_from_file]")
  - Style mixing ("in the style of [artist_from_file]")
  - Batch testing different descriptors

---

### 🛠 **Installation**

#### **Method 1: Manual (Git)**
1. Navigate to your ComfyUI’s `custom_nodes` directory:
```bash
   cd /path/to/ComfyUI/custom_nodes/
```
2. Clone the repository **into this folder**:
```bash
   git clone https://github.com/vladpro3/ComfyUI_BishaNodes.git
```
3. Restart ComfyUI.

#### **Method 2: Custom Nodes Manager**
Alternatively, search for `ComfyUI_BishaNodes` in ComfyUI’s **Custom Nodes Manager** and install with one click.

---

## 🎮 **Usage Examples**

### Resolution Workflow
```
TODO
```

### Prompt Expansion Workflow
```
TODO
```

---

## 🌐 **Advanced Use Cases**

**A/B Testing Prompts**:
```python
# styles.txt
cyberpunk neon
oil painting
watercolor sketch
```
   → Generates: ["photo of a cat, cyberpunk neon", "photo of a cat, oil painting", ...]

---

## 💡 **Why These Nodes?**
- **Time Savings**: Eliminate manual resolution math and prompt duplication
- **Scalability**: Process hundreds of variations with 1-click changes
- **Organization**: Structured output for batch workflows
- **Extensible**: Add custom resolutions via text sources

---

## 🔧 **Technical Specifications**

### **Simple Size Picker**
- **Output Types**:
  - `width` (INT)
  - `height` (INT)
- **Default Resolution**: 512 x 512

### **Empty Latent Size Picker**
- **Additional Output**:
  - `latent` (LATENT) with batch support

### **Create Prompts With Text From File**
- **Supported Formats**:
  - `.txt` (line-delimited)
  - `.csv` (first column)
- **Advanced Parameters** *(For `Create Prompts With Text From File` node)*

| Parameter      | Type/Options                  | Description                                                                 | Example Usage                          |
|---------------|-------------------------------|-----------------------------------------------------------------------------|----------------------------------------|
| **`next_line`** | `increment` \| `decrement` \| `random` \| `fixed` | Defines how to select the next line from the file:<br>- `increment`: Sequentially moves forward<br>- `decrement`: Sequentially moves backward<br>- `random`: Picks lines randomly<br>- `fixed`: Always uses the same line (requires `start_line`) | `random` (for varied prompts)          |
| **`start_line`** | Integer (`0`-based)          | Sets the **starting line offset** in the file.<br>- Only affects `increment`/`decrement`/`fixed` modes.<br>- If `fixed` mode is selected, this line will be used for all prompts. | `10` (skips first 10 lines)            |
| **`results`**   | Integer (`≥1`)               | Controls the **number of generated prompts** (lines to process).| `3` (outputs 3 prompts)                |

- **File Requirements**:
  - Text file must have at least `start_line + results` lines for sequential modes.
  - Empty lines are **skipped automatically**.

- **Behavior Examples**:
  - `next_line=increment`, `start_line=5`, `results=3` → Lines **5, 6, 7**
  - `next_line=random`, `results=5` → **5 random lines**
  - `next_line=fixed`, `start_line=2` → **Only line 2** (repeated for all prompts)

---

## 📜 **License**
MIT License - Free for commercial and personal use.

---

> **Happy Generating!** 🎨  
> *For real-time updates, star this repo.*
