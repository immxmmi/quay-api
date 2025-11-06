import hashlib
import yaml
from reader.yaml_ops import load_yaml_hash, save_yaml_hash
from typing import Union, Dict, Any, Optional
from pathlib import Path


def get_yaml_hash(source: Union[str, Path, Dict[str, Any]]) -> str:
    """Get SHA256 hash from YAML file or data."""
    if isinstance(source, (str, Path)):
        with open(source, "rb") as f:
            content = f.read()
    else:
        content = yaml.safe_dump(source).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def has_yaml_changed(new_hash: str, old_hash: str) -> bool:
    """Return True if the YAML hash has changed."""
    return new_hash != old_hash


def diff_yaml(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two YAML structures and return their differences."""
    diffs = {}
    for key in new_data:
        if key not in old_data:
            diffs[key] = {"status": "added", "new_value": new_data[key]}
        elif new_data[key] != old_data[key]:
            diffs[key] = {
                "status": "modified",
                "old_value": old_data[key],
                "new_value": new_data[key],
            }
    for key in old_data:
        if key not in new_data:
            diffs[key] = {"status": "removed", "old_value": old_data[key]}
    return diffs


def load_yaml_data(file_path: Path) -> Dict[str, Any]:
    """Load YAML content from file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_old_snapshot(storage_dir: Path) -> Dict[str, Any]:
    """Load previous YAML snapshot if it exists."""
    old_file = storage_dir / "last_yaml_snapshot.yaml"
    if old_file.exists():
        with open(old_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_snapshot_and_hash(new_data: Dict[str, Any], new_hash: str, storage_dir: Path):
    """Save updated YAML snapshot and hash."""
    old_file = storage_dir / "last_yaml_snapshot.yaml"
    with open(old_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(new_data, f)
    save_yaml_hash(new_hash, storage_dir)


def check_yaml_change(
    storage_dir: Path,
    file_path: Optional[Path] = None,
    new_data: Optional[Dict[str, Any]] = None
) -> dict:
    """Check YAML changes using a file path or in-memory data."""
    if not storage_dir:
        raise ValueError("storage_dir is required")

    old_hash = load_yaml_hash(storage_dir)

    # Load new YAML if not provided
    if new_data is None:
        if not file_path:
            raise ValueError("Either file_path or new_data must be provided")
        new_data = load_yaml_data(file_path)

    new_hash = get_yaml_hash(new_data)

    if has_yaml_changed(new_hash, old_hash):
        old_data = load_old_snapshot(storage_dir)
        diffs = diff_yaml(old_data, new_data)
        save_snapshot_and_hash(new_data, new_hash, storage_dir)
        return {"status": "changed", "message": "YAML updated", "diff": diffs}

    return {"status": "unchanged", "message": "No changes detected"}


def view_yaml_diff_html(result: dict):
    template_path = Path(__file__).parent / "templates" / "yaml_diff.html"
    html = template_path.read_text(encoding="utf-8")

    diff_rows = ""
    for key, info in result.get("diff", {}).items():
        status = info.get("status")
        old_value = info.get("old_value", "-")
        new_value = info.get("new_value", "-")
        css_class = {
            "added": "status-ok",
            "removed": "status-error",
            "modified": "status-info"
        }.get(status, "")
        diff_rows += f'<tr><td>{key}</td><td class="{css_class}">{status}</td><td>{old_value}</td><td>{new_value}</td></tr>\n'

    html = (
        html.replace("{{ yaml_status }}", result.get("status", ""))
            .replace("{{ yaml_message }}", result.get("message", ""))
            .replace("{{ diff_rows }}", diff_rows)
    )
    return html