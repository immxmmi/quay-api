import os
import requests
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

def check_env():
    required_env_vars = ["API_BASE_URL", "API_TOKEN"]
    details = []
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            logging.error(f"Environment variable {var} is missing.")
            details.append({"name": var, "status": "missing"})
            missing_vars.append(var)
        else:
            logging.info(f"Environment variable {var} is set.")
            details.append({"name": var, "status": "ok"})
    summary_status = "error" if missing_vars else "ok"
    if missing_vars:
        logging.error(f"Missing environment variables: {missing_vars}")
    else:
        logging.info("All required environment variables are set.")
    return {"summary": {"status": summary_status}, "details": details}

def check_api():
    api_base_url = os.getenv("API_BASE_URL")
    if not api_base_url:
        logging.error("API_BASE_URL is not set, skipping API check.")
        return {"status": "error", "reason": "API_BASE_URL not set"}
    try:
        response = requests.get(f"{api_base_url.rstrip('/')}/")
        if response.status_code == 401:
            reason = "unauthorized (missing or invalid token)"
        elif response.status_code == 403:
            reason = "forbidden (access denied)"
        elif response.status_code == 404:
            reason = "not found (invalid endpoint)"
        elif response.ok:
            reason = "success"
        else:
            reason = "unexpected response"
        logging.info(f"API is reachable (status {response.status_code}): {reason}")
        return {"status": "ok", "reason": reason}
    except Exception as e:
        logging.error(f"Error checking API: {e}")
        return {"status": "error", "reason": "unreachable or invalid response"}

def check():
    result_env = check_env()
    result_api = check_api() if result_env.get("summary", {}).get("status") == "ok" else {"status": "error", "reason": "env check failed"}
    return {"env": result_env, "api": result_api}

def render_check_html(result: dict):
    template_path = Path(__file__).parent / "templates" / "index.html"
    html = template_path.read_text(encoding="utf-8")

    env_rows = ""
    for item in result.get("env", {}).get("details", []):
        name = item.get("name", "")
        status = item.get("status", "")
        css_class = "status-ok" if status == "ok" else "status-missing"
        env_rows += f'<tr><td>{name}</td><td class="{css_class}">{status}</td></tr>\n'

    api_result = result.get("api", {})
    api_status = api_result.get("status", "")
    api_reason = api_result.get("reason", "-")
    api_class = "status-ok" if api_status == "ok" else "status-error"

    html = (
        html.replace("{{ env_rows }}", env_rows)
            .replace("{{ api_class }}", api_class)
            .replace("{{ api_status }}", api_status)
            .replace("{{ api_reason }}", api_reason)
    )

    return html