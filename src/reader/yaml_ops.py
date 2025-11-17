from pathlib import Path

def save_yaml_hash(hash_value: str, storage_dir: Path):
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_file = storage_dir / "last_hash.txt"
    with open(storage_file, "w", encoding="utf-8") as f:
        f.write(hash_value)

def load_yaml_hash(storage_dir: Path) -> str:
    storage_file = storage_dir / "last_hash.txt"
    if not storage_file.exists():
        return ""
    with open(storage_file, "r", encoding="utf-8") as f:
        return f.read().strip()