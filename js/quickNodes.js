import { app } from "../../scripts/app.js";

// ----------- ComfyUI\web\extensions\core\widgetInputs.js copypaste -----------
const CONVERTED_TYPE = "converted-widget";
function hideWidget(node, widget, suffix = "") {
  widget.origType = widget.type;
  widget.origComputeSize = widget.computeSize;
  widget.origSerializeValue = widget.serializeValue;
  widget.computeSize = () => [0, -4]; // -4 is due to the gap litegraph adds between widgets automatically
  widget.type = CONVERTED_TYPE + suffix;
  widget.serializeValue = () => {
    // Prevent serializing the widget if we have no input linked
    if (!node.inputs) {
      return undefined;
    }
    let node_input = node.inputs.find((i) => i.widget?.name === widget.name);

    if (!node_input || !node_input.link) {
      return undefined;
    }
    return widget.origSerializeValue
      ? widget.origSerializeValue()
      : widget.value;
  };

  // Hide any linked widgets, e.g. seed+seedControl
  if (widget.linkedWidgets) {
    for (const w of widget.linkedWidgets) {
      hideWidget(node, w, ":" + widget.name);
    }
  }
}

function getWidgetType(config) {
  // Special handling for COMBO so we restrict links based on the entries
  let type = config[0];
  let linkType = type;
  if (type instanceof Array) {
    type = "COMBO";
    linkType = linkType.join(",");
  }
  return { type, linkType };
}

function convertToInput(node, widget, config) {
  hideWidget(node, widget);

  const { linkType } = getWidgetType(config);

  // Add input and store widget config for creating on primitive node
  const sz = node.size;
  node.addInput(widget.name, linkType, {
    widget: { name: widget.name, config },
  });

  for (const widget of node.widgets) {
    widget.last_y += LiteGraph.NODE_SLOT_HEIGHT;
  }

  // Restore original size but grow if needed
  node.setSize([Math.max(sz[0], node.size[0]), Math.max(sz[1], node.size[1])]);
}
//------------------------------------------------------------------------------

// ------ section inspired by pythongosssss 'ComfyUI-Custom-Scripts' code ------
function addMenuHandler(nodeType, callback) {
  const oldMenuOptions = nodeType.prototype.getExtraMenuOptions;

  nodeType.prototype.getExtraMenuOptions = function () {
    const menuOptions = oldMenuOptions.apply(this, arguments);
    callback.apply(this, arguments);

    return menuOptions;
  };
}

/**
 * Creates a new node in the graph and adjusts its position based on the passed options.
 * @param {string} name - The name of the new node.
 * @param {object} nextTo - The reference node to position the new node next to.
 * @param {object} [options={}] - Optional parameters to adjust the new node's behavior.
 * @param {boolean} [options.select=true] - If set to true, the new node will be selected.
 * @param {number} [options.shiftY=0] - The vertical shift from the reference node's position.
 * @param {boolean} [options.before=false] - If true, the new node will be positioned
 *     to the left of the reference node; otherwise, to the right.
 * @param {array} [options.size] - The size of the new node.
 *
 * @returns {object} The newly created node.
 */
function placeNewNode(name, nextTo, options = {}) {
  const nodeSeparation = 30;
  const { select = true, shiftY = 0, before = false, size } = options;

  const node = LiteGraph.createNode(name);

  if (size) {
    node.size = size;
  }

  app.graph.add(node);

  const [nextToX, nextToY] = nextTo.pos;
  const [nextToWidth] = nextTo.size;

  const offsetX = before
    ? -node.size[0] - nodeSeparation
    : nextToWidth + nodeSeparation;
  node.pos = [nextToX + offsetX, nextToY + shiftY];

  if (select) {
    app.canvas.selectNode(node, false);
  }

  return node;
}

function prependNewNode(node, nodeData, newNodeName, newNodewidgetNames) {
  const newNode = placeNewNode(newNodeName, node, {
    before: true,
    shiftY: 0,
  });

  for (const widget_name of newNodewidgetNames) {
    let slot = node.findInputSlot(widget_name);
    if (slot === -1) {
      //Convert widget into input
      const w = node.widgets.find((obj) => obj.name === widget_name);
      const { required, optional } = nodeData?.input;
      const config = required[w.name] ||
        optional?.[w.name] || [w.type, w.options || {}];
      convertToInput(node, w, config);

      slot = node.findInputSlot(widget_name);
    }
    newNode.connect(newNode.findOutputSlot(widget_name), node, slot);
  }
}

app.registerExtension({
  name: "trop.YARS",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (
      nodeData.name === "EmptyLatentImage" ||
      nodeData.name === "ImageScale"
    ) {
      addMenuHandler(nodeType, function (_, options) {
        const entries = [
          { name: "yaResolution Selector", value: "YARS" },
          { name: "Advanced yaResolution Selector", value: "YARSAdv" },
        ];
        for (const entry of entries) {
          options.unshift({
            content: `Prepend ${entry.name}`,
            callback: () =>
              prependNewNode(this, nodeData, entry.value, ["width", "height"]),
          });
        }
      });
    }
  },
});
