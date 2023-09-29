from .nodes import YARS, YARSAdv


NODE_CLASS_MAPPINGS = {"YARS": YARS, "YARSAdv": YARSAdv}
NODE_DISPLAY_NAME_MAPPINGS = {
    "YARS": "yaResolution Selector",
    "YARSAdv": "yaResolution Selector (Advanced)",
}


# --------------------------- Install web extension ----------------------------
import shutil
from pathlib import Path

# Get base paths
node_dir = Path(__file__).resolve().parent
comfy_dir = node_dir.parent.parent

script_path = node_dir / "js" / "quickNodes.js"
destination_dir = comfy_dir / "web" / "extensions" / "tropfchen"
destination_path = destination_dir / "yarsQuickNodes.js"

try:
    destination_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(script_path, destination_path)
except PermissionError as permission_error:
    print(f"Permission error: {permission_error}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
