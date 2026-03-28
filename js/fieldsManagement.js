import { app } from "../../scripts/app.js";

// Module-level counter — guarantees unique widget names across all node instances
// without storing any state on the node itself.
let _bishaWidgetIdCounter = 0;

function fitString(ctx, str, maxWidth) {
    let width = ctx.measureText(str).width;
    const ellipsis = "…";
    const ellipsisWidth = ctx.measureText(ellipsis).width;
    if (width <= maxWidth || width <= ellipsisWidth) return str;
    let lo = 0, hi = str.length;
    while (lo < hi) {
        const mid = Math.ceil((lo + hi) / 2);
        if (ctx.measureText(str.substring(0, mid)).width + ellipsisWidth <= maxWidth) lo = mid;
        else hi = mid - 1;
    }
    return str.substring(0, lo) + ellipsis;
}

function isLowQuality() {
    const canvas = app.canvas;
    return ((canvas?.ds?.scale) || 1) <= 0.5;
}

function drawRoundedRectangle(ctx, options) {
    const lq = isLowQuality();
    ctx.save();
    ctx.strokeStyle = options.colorStroke || LiteGraph.WIDGET_OUTLINE_COLOR;
    ctx.fillStyle   = options.colorBackground || LiteGraph.WIDGET_BGCOLOR;
    ctx.beginPath();
    const r = lq ? 0 : (options.borderRadius ?? options.size[1] * 0.5);
    ctx.roundRect(...options.pos, ...options.size, [r]);
    ctx.fill();
    if (!lq) ctx.stroke();
    ctx.restore();
}

function drawTogglePart(ctx, { posX, posY, height, value }) {
    const lq = isLowQuality();
    ctx.save();
    const toggleRadius   = height * 0.36;
    const toggleBgWidth  = height * 1.5;
    if (!lq) {
        ctx.beginPath();
        ctx.roundRect(posX + 4, posY + 4, toggleBgWidth - 8, height - 8, [height * 0.5]);
        ctx.globalAlpha = app.canvas.editor_alpha * 0.25;
        ctx.fillStyle   = "rgba(255,255,255,0.45)";
        ctx.fill();
        ctx.globalAlpha = app.canvas.editor_alpha;
    }
    ctx.fillStyle = value === true ? "#89B" : "#888";
    const toggleX = lq || value === false
        ? posX + height * 0.5
        : value === true
            ? posX + height
            : posX + height * 0.75;
    ctx.beginPath();
    ctx.arc(toggleX, posY + height * 0.5, toggleRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    return [posX, toggleBgWidth];
}

function drawWidgetButton(ctx, options, text, isPressed) {
    const lq = isLowQuality();
    const borderRadius = lq ? 0 : (options.borderRadius ?? 4);
    ctx.save();
    if (!lq && !isPressed) {
        drawRoundedRectangle(ctx, {
            size: [options.size[0] - 2, options.size[1]],
            pos:  [options.pos[0] + 1,  options.pos[1] + 1],
            borderRadius,
            colorBackground: "#000000aa",
            colorStroke:     "#000000aa",
        });
    }
    drawRoundedRectangle(ctx, {
        size: options.size,
        pos:  [options.pos[0], options.pos[1] + (isPressed ? 1 : 0)],
        borderRadius,
        colorBackground: isPressed ? "#444" : LiteGraph.WIDGET_BGCOLOR,
        colorStroke: "transparent",
    });
    if (!lq && text) {
        ctx.textBaseline = "middle";
        ctx.textAlign    = "center";
        ctx.fillStyle    = LiteGraph.WIDGET_TEXT_COLOR;
        ctx.fillText(text, options.pos[0] + options.size[0] / 2, options.pos[1] + options.size[1] / 2 + (isPressed ? 1 : 0));
    }
    ctx.restore();
}

// ---------------------------------------------------------------------------
// BishaBaseWidget — base class with hit-area / mouse-event routing
// ---------------------------------------------------------------------------

class BishaBaseWidget {
    constructor(name) {
        this.name    = name;
        this.type    = "custom";
        this.options = {};
        this.y       = 0;
        this.last_y  = 0;
        this.mouseDowned           = null;
        this.isMouseDownedAndOver  = false;
        this.hitAreas              = {};
        this._downedForMove        = [];
        this._downedForClick       = [];
    }

    serializeValue(node, index) { return this.value; }

    _within(pos, bounds) {
        const xOk = pos[0] >= bounds[0] && pos[0] <= bounds[0] + bounds[1];
        if (bounds.length === 2) return xOk;
        return xOk && pos[1] >= bounds[1] && pos[1] <= bounds[1] + bounds[3];
    }

    mouse(event, pos, node) {
        if (event.type === "pointerdown") {
            this.mouseDowned          = [...pos];
            this.isMouseDownedAndOver = true;
            this._downedForMove.length  = 0;
            this._downedForClick.length = 0;
            let handled = false;
            for (const part of Object.values(this.hitAreas)) {
                if (!this._within(pos, part.bounds)) continue;
                if (part.onMove)  this._downedForMove.push(part);
                if (part.onClick) this._downedForClick.push(part);
                if (part.onDown) {
                    const r = part.onDown.apply(this, [event, pos, node, part]);
                    handled = handled || r === true;
                }
                part.wasClickedAndOver = true;
            }
            return this.onMouseDown(event, pos, node) ?? handled;
        }

        if (event.type === "pointerup") {
            if (!this.mouseDowned) return true;
            this._downedForMove.length = 0;
            const wasOver = this.isMouseDownedAndOver;
            this.cancelMouseDown();
            let handled = false;
            for (const part of Object.values(this.hitAreas)) {
                if (part.onUp && this._within(pos, part.bounds)) {
                    const r = part.onUp.apply(this, [event, pos, node, part]);
                    handled = handled || r === true;
                }
                part.wasClickedAndOver = false;
            }
            for (const part of this._downedForClick) {
                if (this._within(pos, part.bounds)) {
                    const r = part.onClick.apply(this, [event, pos, node, part]);
                    handled = handled || r === true;
                }
            }
            this._downedForClick.length = 0;
            if (wasOver) handled = this.onMouseClick(event, pos, node) || handled;
            return this.onMouseUp(event, pos, node) ?? handled;
        }

        if (event.type === "pointermove") {
            this.isMouseDownedAndOver = !!this.mouseDowned;
            if (this.mouseDowned &&
                (pos[0] < 15 || pos[0] > node.size[0] - 15 ||
                 pos[1] < this.last_y || pos[1] > this.last_y + LiteGraph.NODE_WIDGET_HEIGHT)) {
                this.isMouseDownedAndOver = false;
            }
            for (const part of Object.values(this.hitAreas)) {
                if (this._downedForMove.includes(part))  part.onMove.apply(this, [event, pos, node, part]);
                if (this._downedForClick.includes(part)) part.wasClickedAndOver = this._within(pos, part.bounds);
            }
            return this.onMouseMove(event, pos, node) ?? true;
        }
        return false;
    }

    cancelMouseDown() {
        this.mouseDowned          = null;
        this.isMouseDownedAndOver = false;
        this._downedForMove.length = 0;
    }

    onMouseDown(event, pos, node)  {}
    onMouseUp(event, pos, node)    {}
    onMouseClick(event, pos, node) {}
    onMouseMove(event, pos, node)  {}
}

// ---------------------------------------------------------------------------
// BishaDividerWidget
// ---------------------------------------------------------------------------

class BishaDividerWidget extends BishaBaseWidget {
    constructor(opts = {}) {
        super("divider");
        this.value   = {};
        this.options = { serialize: false };
        this.type    = "custom";
        this._opts   = { marginTop: 7, marginBottom: 7, marginLeft: 15, marginRight: 15, thickness: 1, ...opts };
    }
    draw(ctx, node, width, posY) {
        if (!this._opts.thickness) return;
        ctx.save();
        ctx.strokeStyle = LiteGraph.WIDGET_OUTLINE_COLOR;
        const x = this._opts.marginLeft;
        const y = posY + this._opts.marginTop;
        const w = width - this._opts.marginLeft - this._opts.marginRight;
        ctx.stroke(new Path2D(`M ${x} ${y} h ${w}`));
        ctx.restore();
    }
    computeSize(width) {
        return [width, this._opts.marginTop + this._opts.marginBottom + this._opts.thickness];
    }
}

// ---------------------------------------------------------------------------
// BishaButtonWidget
// ---------------------------------------------------------------------------

class BishaButtonWidget extends BishaBaseWidget {
    constructor(label, onClick) {
        super(label);
        this.type  = "custom";
        this.value = "";
        this.label = label;
        this._cb   = onClick;
    }
    draw(ctx, node, width, y, height) {
        drawWidgetButton(ctx, { size: [width - 30, height], pos: [15, y] }, this.label, this.isMouseDownedAndOver);
    }
    onMouseClick(event, pos, node) {
        return this._cb(event, pos, node);
    }
}

// ---------------------------------------------------------------------------
// BishaFileHeaderWidget — "Toggle All" header row
// ---------------------------------------------------------------------------

class BishaFileHeaderWidget extends BishaBaseWidget {
    constructor(node) {
        super("BishaFileHeader");
        this.value   = { type: "BishaFileHeader" };
        this.type    = "custom";
        this._node   = node;
        this.hitAreas = {
            toggle: { bounds: [0, 0], onDown: this._onToggleDown },
        };
    }

    draw(ctx, node, w, posY, height) {
        const margin      = 10;
        const innerMargin = margin * 0.33;
        const lq          = isLowQuality();
        const allState    = node.allFilesState();
        posY += 2;
        const midY = posY + height * 0.5;
        ctx.save();

        if (!node.hasBishaFileWidgets()) {
            // Empty state hint
            ctx.globalAlpha  = app.canvas.editor_alpha * 0.4;
            ctx.fillStyle    = LiteGraph.WIDGET_TEXT_COLOR;
            ctx.textAlign    = "center";
            ctx.textBaseline = "middle";
            if (!lq) ctx.fillText("Нажмите ➕ Add file чтобы добавить файл", node.size[0] / 2, midY);
            ctx.restore();
            return;
        }

        this.hitAreas.toggle.bounds = drawTogglePart(ctx, { posX: 10, posY, height, value: allState });
        if (!lq) {
            const posX = 10 + this.hitAreas.toggle.bounds[1] + innerMargin;
            ctx.globalAlpha  = app.canvas.editor_alpha * 0.55;
            ctx.fillStyle    = LiteGraph.WIDGET_TEXT_COLOR;
            ctx.textAlign    = "left";
            ctx.textBaseline = "middle";
            ctx.fillText("Toggle All", posX, midY);
        }
        ctx.restore();
    }

    _onToggleDown(event, pos, node) {
        node.toggleAllFiles();
        this.cancelMouseDown();
        return true;
    }
}

// ---------------------------------------------------------------------------
// BishaFileWidget — one file row
// ---------------------------------------------------------------------------

const DEFAULT_FILE_DATA = { on: true, file: "" };

class BishaFileWidget extends BishaBaseWidget {
    constructor(name) {
        super(name);
        this.type = "custom";
        this._value = { ...DEFAULT_FILE_DATA };
        this.hitAreas = {
            toggle: { bounds: [0, 0], onDown: this._onToggleDown },
            file:   { bounds: [0, 0], onClick: this._onFileClick },
        };
    }

    get value()  { return this._value; }
    set value(v) {
        this._value = (v && typeof v === "object") ? { ...DEFAULT_FILE_DATA, ...v } : { ...DEFAULT_FILE_DATA };
    }

    serializeValue() {
        return { ...this._value };
    }

    draw(ctx, node, w, posY, height) {
        const margin      = 10;
        const innerMargin = margin * 0.33;
        const lq          = isLowQuality();
        const midY        = posY + height * 0.5;

        ctx.save();

        // Background rounded rect
        drawRoundedRectangle(ctx, {
            pos:  [margin, posY],
            size: [node.size[0] - margin * 2, height],
        });

        // Toggle
        let posX = margin;
        this.hitAreas.toggle.bounds = drawTogglePart(ctx, { posX, posY, height, value: this._value.on });

        if (lq) { ctx.restore(); return; }

        posX += this.hitAreas.toggle.bounds[1] + innerMargin;

        if (!this._value.on) ctx.globalAlpha = app.canvas.editor_alpha * 0.4;

        // File path text
        ctx.fillStyle    = LiteGraph.WIDGET_TEXT_COLOR;
        ctx.textAlign    = "left";
        ctx.textBaseline = "middle";
        const fileWidth  = node.size[0] - margin - posX - innerMargin;
        const label      = this._value.file || "Click to set file path…";
        ctx.fillText(fitString(ctx, label, fileWidth), posX, midY);
        this.hitAreas.file.bounds = [posX, fileWidth];

        ctx.globalAlpha = app.canvas.editor_alpha;
        ctx.restore();
    }

    _onToggleDown(event, pos, node) {
        this._value.on = !this._value.on;
        this.cancelMouseDown();
        return true;
    }

    _onFileClick(event, pos, node) {
        app.canvas.prompt("File path", this._value.file, (v) => {
            this._value.file = v;
            node.setDirtyCanvas(true, true);
        }, event);
        this.cancelMouseDown();
        return true;
    }
}

// ---------------------------------------------------------------------------
// Node class extension
// ---------------------------------------------------------------------------

function moveArrayItem(arr, item, targetIndex) {
    const idx = arr.indexOf(item);
    if (idx === -1) return;
    arr.splice(idx, 1);
    arr.splice(targetIndex, 0, item);
}

function removeArrayItem(arr, item) {
    const idx = arr.indexOf(item);
    if (idx !== -1) arr.splice(idx, 1);
}

function setupBishaLoadDataNode(nodeType) {
    const orig_onNodeCreated = nodeType.prototype.onNodeCreated;
    const orig_configure     = nodeType.prototype.configure;

    // Track button spacer per node instance (no _fileCounter needed)
    nodeType.prototype._bishaSetup = function () {
        if (this._bishaReady) return;
        this._bishaReady   = true;
        this._buttonSpacer = null;
        this._bishaInitWidgets();
    };

    nodeType.prototype._bishaInitWidgets = function () {
        // Clear existing widgets if any
        while (this.widgets?.length) this.removeWidget(this.widgets[0]);
        this._buttonSpacer = null;
        this._addNonFileWidgets();
    };

    nodeType.prototype._addNonFileWidgets = function () {
        // Divider on top (index 0)
        const topDivider = new BishaDividerWidget({ marginTop: 4, marginBottom: 0, thickness: 0 });
        this.addCustomWidget(topDivider);
        moveArrayItem(this.widgets, topDivider, 0);

        // Header (index 1)
        const header = new BishaFileHeaderWidget(this);
        this.addCustomWidget(header);
        moveArrayItem(this.widgets, header, 1);

        // Spacer before the add button
        this._buttonSpacer = new BishaDividerWidget({ marginTop: 4, marginBottom: 0, thickness: 0 });
        this.addCustomWidget(this._buttonSpacer);

        // "Add file" button
        this.addCustomWidget(new BishaButtonWidget("Add file", (event, pos, node) => {
            this.addNewFileWidget();
            const computed = this.computeSize();
            this.size[1] = Math.max(this.size[1], computed[1]);
            this.setDirtyCanvas(true, true);
            return true;
        }));
    };

    nodeType.prototype.addNewFileWidget = function (data) {
        // Use module-level counter for a globally unique name — no instance state needed.
        const widget = new BishaFileWidget("file_" + (++_bishaWidgetIdCounter));
        if (data) widget.value = data;
        this.addCustomWidget(widget);
        if (this._buttonSpacer) {
            moveArrayItem(this.widgets, widget, this.widgets.indexOf(this._buttonSpacer));
        }
        return widget;
    };

    nodeType.prototype.hasBishaFileWidgets = function () {
        return !!this.widgets?.find(w => w.name?.startsWith("file_"));
    };

    nodeType.prototype.allFilesState = function () {
        let allOn = true, allOff = true;
        for (const w of (this.widgets || [])) {
            if (!w.name?.startsWith("file_")) continue;
            const on = w.value?.on;
            allOn  = allOn  && on === true;
            allOff = allOff && on === false;
            if (!allOn && !allOff) return null;
        }
        return allOn && this.hasBishaFileWidgets() ? true : false;
    };

    nodeType.prototype.toggleAllFiles = function () {
        const allOn    = this.allFilesState();
        const toggleTo = !allOn;
        for (const w of (this.widgets || [])) {
            if (w.name?.startsWith("file_") && w.value?.on != null) {
                w.value.on = toggleTo;
            }
        }
    };

    // Right-click context menu for file rows
    const orig_getSlotMenuOptions = nodeType.prototype.getSlotMenuOptions;
    nodeType.prototype.getSlotMenuOptions = function (slot) {
        if (slot?.widget?.name?.startsWith("file_")) {
            const widget = slot.widget;
            const index  = this.widgets.indexOf(widget);
            const canUp   = !!this.widgets[index - 1]?.name?.startsWith("file_");
            const canDown = !!this.widgets[index + 1]?.name?.startsWith("file_");

            return [
                {
                    content: "Move Up",
                    disabled: !canUp,
                    callback: () => { moveArrayItem(this.widgets, widget, index - 1); this.setDirtyCanvas(true,true); },
                },
                {
                    content: "Move Down",
                    disabled: !canDown,
                    callback: () => { moveArrayItem(this.widgets, widget, index + 1); this.setDirtyCanvas(true,true); },
                },
                null,
                {
                    content: "Remove",
                    callback: () => { removeArrayItem(this.widgets, widget); this.setDirtyCanvas(true,true); },
                },
            ];
        }
        return orig_getSlotMenuOptions ? orig_getSlotMenuOptions.call(this, slot) : undefined;
    };

    // Detect right-click on a file widget row (since they are canvas widgets, not real slots)
    const orig_getSlotInPosition = nodeType.prototype.getSlotInPosition;
    nodeType.prototype.getSlotInPosition = function (canvasX, canvasY) {
        const slot = orig_getSlotInPosition ? orig_getSlotInPosition.call(this, canvasX, canvasY) : null;
        if (!slot) {
            let last = null;
            for (const w of (this.widgets || [])) {
                if (!w.last_y) continue;
                if (canvasY > this.pos[1] + w.last_y) { last = w; continue; }
                break;
            }
            if (last?.name?.startsWith("file_")) {
                return { widget: last, output: { type: "FILE WIDGET" } };
            }
        }
        return slot;
    };

    // onNodeCreated
    nodeType.prototype.onNodeCreated = function () {
        orig_onNodeCreated?.call(this);
        this._bishaSetup();
        const computed = this.computeSize();
        this.size = this.size || [0, 0];
        this.size[0] = Math.max(this.size[0], computed[0]);
        this.size[1] = Math.max(this.size[1], computed[1]);
        this.setDirtyCanvas(true, true);
    };

    // configure — restore widgets from saved workflow
    nodeType.prototype.configure = function (info) {
        // Clear our widgets first, then call orig_configure only for node
        // meta-properties (position, size, color, flags) — NOT widget restoration.
        while (this.widgets?.length) this.removeWidget(this.widgets[0]);
        this._buttonSpacer = null;

        if (info.id != null) {
            // Call orig_configure to restore position/size/color/flags.
            // Safe because we already cleared widgets, so it won't create duplicates.
            const widgetsBackup = info.widgets_values;
            info = { ...info, widgets_values: [] };  // hide values so orig doesn't restore widgets
            orig_configure?.call(this, info);
            info.widgets_values = widgetsBackup;     // restore for our own use below
        }

        const tempW = this.size?.[0] ?? 300;
        const tempH = this.size?.[1] ?? 100;

        // Re-add divider + header + spacer + button
        this._addNonFileWidgets();

        // Re-add file widgets from serialized values
        for (const v of (info.widgets_values || [])) {
            if (v && typeof v === "object" && "file" in v) {
                this.addNewFileWidget(v);
            }
        }

        this._bishaReady = true;

        this.size = this.size || [0, 0];
        this.size[0] = tempW;
        this.size[1] = Math.max(tempH, this.computeSize()[1]);
    };
}

// ---------------------------------------------------------------------------
// Register
// ---------------------------------------------------------------------------

app.registerExtension({
    name: "BishaNodes.LoadDataFromFiles",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "LoadDataFromFiles") {
            setupBishaLoadDataNode(nodeType);
        }
    },
});
