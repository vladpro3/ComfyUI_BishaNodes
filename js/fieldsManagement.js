import { app } from "../../scripts/app.js";

const originalWidgetData = {};

const updateWidget = (node, widget, show = false, widgetName = "") => {
    if (!originalWidgetData[widget.name]) {
        originalWidgetData[widget.name] = {originalType: widget.type, originalComputeSize: widget.computeSize};
    }

    widget.type = show ? originalWidgetData[widget.name].originalType : "hide" + widgetName;
    widget.computeSize = show ? originalWidgetData[widget.name].originalComputeSize : () => [0, -4];
    widget.linkedWidgets?.forEach(_widget => updateWidget(node, _widget, show, "_" + widget.name));
    node.setSize([node.size[0], node.computeSize()[1]]);
}

const toggleVisibility = (node, countValue, maxValue) => {
    for (let i = 0; i < maxValue; i++) {
        const textWidget = node.widgets.find((widget) => widget.name === `file_${i + 1}`);
        const boolWidget = node.widgets.find((widget) => widget.name === `enabled_${i + 1}`);

        if (textWidget && boolWidget) {
            if (i < countValue) {
                updateWidget(node, textWidget, true);
                updateWidget(node, boolWidget, true);
            } else {
                updateWidget(node, textWidget, false);
                updateWidget(node, boolWidget, false);
            }
        }
    }
}

app.registerExtension({
    name: "BishaNodes.LoadDataFromFiles",
    nodeCreated(node) {
        if (node.comfyClass !== 'LoadDataFromFiles') {
            return;
        }

        for (const widget of node.widgets || []) {
            if (widget.name !== 'files_count') {
                continue;
            }

            let widgetValue = widget.value;
            let originalDescriptor = Object.getOwnPropertyDescriptor(widget, 'value');

            if (!originalDescriptor) {
                originalDescriptor = Object.getOwnPropertyDescriptor(widget.constructor.prototype, 'value');
            }

            toggleVisibility(node, widget.value, widget.options.max);

            Object.defineProperty(widget, 'value', {
                get() {
                    return originalDescriptor && originalDescriptor.get
                        ? originalDescriptor.get.call(widget)
                        : widgetValue;
                },
                set(newVal) {
                    if (originalDescriptor && originalDescriptor.set) {
                        originalDescriptor.set.call(widget, newVal);
                    } else {
                        widgetValue = newVal;
                    }

                    toggleVisibility(node, widget.value, widget.options.max);
                }
            });
        }
    }
});

