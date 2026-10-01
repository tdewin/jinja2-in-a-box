#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader

INPUT_DIR = Path("/data")
OUTPUT_DIR = Path("/data/output")
JSON_DATA_FILE = INPUT_DIR / "data.json"

def to_nice_yaml(data, indent=2, **kwargs):
    """Custom Jinja2 filter replicating Ansible's to_nice_yaml."""
    return yaml.dump(
        data,
        default_flow_style=False,
        indent=indent,
        sort_keys=False,
        **kwargs
    )

def get_context() -> dict:
    context = {}

    if JSON_DATA_FILE.exists() and JSON_DATA_FILE.is_file():
        try:
            with open(JSON_DATA_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                if isinstance(json_data, dict):
                    context.update(json_data)
                    print(f"Loaded context variables from {JSON_DATA_FILE.name}")
                else:
                    print(f"Warning: {JSON_DATA_FILE.name} must contain a JSON object. Skipping.", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"Error parsing {JSON_DATA_FILE.name}: {e}", file=sys.stderr)

    context.update(dict(os.environ))
    return context

def main():
    if not INPUT_DIR.exists():
        print(f"Error: Directory '{INPUT_DIR}' does not exist.", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    context = get_context()

    env = Environment(
        loader=FileSystemLoader(str(INPUT_DIR)),
        autoescape=False,
        keep_trailing_newline=True
    )

    # Register custom filters (replicating Ansible filters)
    env.filters["to_nice_yaml"] = to_nice_yaml
    env.filters["to_yaml"] = to_nice_yaml
    env.filters["to_nice_json"] = lambda d, indent=2: json.dumps(d, indent=indent)

    j2_files = list(INPUT_DIR.rglob("*.j2"))
    if not j2_files:
        print("No .j2 files found in /data.")
        return

    for filepath in j2_files:
        if OUTPUT_DIR in filepath.parents or filepath.parent == OUTPUT_DIR:
            continue

        rel_path = filepath.relative_to(INPUT_DIR)
        out_rel_path = rel_path.with_suffix("") if rel_path.suffix == ".j2" else rel_path
        dest_file = OUTPUT_DIR / out_rel_path

        dest_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"Processing: {rel_path} -> {dest_file.relative_to(OUTPUT_DIR)}")

        template = env.get_template(str(rel_path))
        rendered_content = template.render(context)

        with open(dest_file, "w", encoding="utf-8") as f:
            f.write(rendered_content)

    print("Processing complete.")

if __name__ == "__main__":
    main()
