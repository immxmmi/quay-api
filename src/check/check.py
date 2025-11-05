import os
import requests
import logging

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
        response = requests.get(api_base_url)
        if response.status_code == 200:
            logging.info("API is reachable and returned status 200.")
            return {"status": "ok"}
        else:
            logging.error(f"API returned unexpected status code: {response.status_code}")
            return {"status": "error", "reason": "unreachable or invalid response"}
    except Exception as e:
        logging.error(f"Error checking API: {e}")
        return {"status": "error", "reason": "unreachable or invalid response"}

def check():
    result_env = check_env()
    result_api = check_api() if result_env.get("summary", {}).get("status") == "ok" else {"status": "error", "reason": "env check failed"}
    return {"env": result_env, "api": result_api}

def render_check_html(result: dict):
    env_details = result.get("env", {}).get("details", [])
    api_result = result.get("api", {})
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Check Results</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }
  h2 { color: #333; }
  table { border-collapse: collapse; width: 50%; margin-bottom: 30px; }
  th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
  th { background-color: #eee; }
  .status-ok { color: #155724; background-color: #d4edda; font-weight: bold; }
  .status-missing { color: #721c24; background-color: #f8d7da; font-weight: bold; }
  .status-error { color: #721c24; background-color: #f8d7da; font-weight: bold; }
  .status-info { color: #0c5460; background-color: #d1ecf1; font-weight: bold; }
</style>
</head>
<body>
  <h2>Environment Variables Status</h2>
  <table>
    <thead>
      <tr><th>Variable</th><th>Status</th></tr>
    </thead>
    <tbody>
"""
    for item in env_details:
        name = item.get("name", "")
        status = item.get("status", "")
        css_class = "status-ok" if status == "ok" else "status-missing"
        html += f'<tr><td>{name}</td><td class="{css_class}">{status}</td></tr>\n'

    html += """
    </tbody>
  </table>

  <h2>API Check</h2>
  <table>
    <thead>
      <tr><th>Status</th><th>Reason</th></tr>
    </thead>
    <tbody>
"""
    api_status = api_result.get("status", "")
    api_reason = api_result.get("reason", "")
    if api_status == "ok":
        css_class = "status-ok"
        reason_display = "-"
    else:
        css_class = "status-error"
        reason_display = api_reason if api_reason else "-"
    html += f'<tr><td class="{css_class}">{api_status}</td><td>{reason_display}</td></tr>\n'

    html += """
    </tbody>
  </table>
</body>
</html>
"""
    return html
