import yaml
import importlib
from actions import JOB_REGISTRY

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def resolve_placeholders(data, inputs):
    if isinstance(data, str) and "{{" in data:
        key = data.replace("{{ inputs.", "").replace(" }}", "")
        return inputs.get(key, "")
    if isinstance(data, dict):
        return {k: resolve_placeholders(v, inputs) for k, v in data.items()}
    if isinstance(data, list):
        return [resolve_placeholders(i, inputs) for i in data]
    return data

def run_function(job_name, params):
    module = importlib.import_module("actions")

    action = JOB_REGISTRY.get(job_name)
    if not action:
        print(f"❌ Unknown job: '{job_name}'. Allowed: {list(JOB_REGISTRY.keys())}")
        return

    func = getattr(module, action)
    print(f"➡️ Running: {action}()")
    return func(**params) if isinstance(params, dict) else func()

def run_pipeline(struct_file="struct.yaml"):
    struct = load_yaml(struct_file)
    inputs = load_yaml(struct["input_file"])

    pipeline = struct.get("pipeline", [])

    for step in pipeline:
        if not step.get("enabled", False):
            continue

        job_name = step.get("job")
        params = step.get("params", {})
        params = resolve_placeholders(params, inputs)

        run_function(job_name, params)

    print("✅ Pipeline completed.")

if __name__ == "__main__":
    run_pipeline()