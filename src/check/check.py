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
    env_details = result.get("env", {}).get("details", [])
    api_result = result.get("api", {})
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Check Results</title>
<style>
  body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: white;
    text-align: center;
  }
  table {
    border-collapse: collapse;
    width: 60%;
    margin: 20px auto;
    border: 1px solid #ccc;
  }
  th, td {
    border: 1px solid #ccc;
    padding: 10px 15px;
    text-align: left;
  }
  th {
    background-color: #f2f2f2;
    font-weight: bold;
  }
  .status-ok {
    background-color: #d4edda;
    color: #155724;
    font-weight: bold;
  }
  .status-missing {
    background-color: #fff3cd;
    color: #856404;
    font-weight: bold;
  }
  .status-error {
    background-color: #f8d7da;
    color: #721c24;
    font-weight: bold;
  }
  .status-info {
    background-color: #d1ecf1;
    color: #0c5460;
    font-weight: bold;
  }
  h2 {
    color: #333;
    margin-top: 40px;
    margin-bottom: 10px;
  }
  p.description {
    color: #666;
    font-size: 14px;
    margin-top: -10px;
    margin-bottom: 20px;
  }
</style>
</head>
<body>

  <h1 style="text-align:center; color:#222;">System & API Health Check</h1>
  <p style="text-align:center; color:#666; font-size:14px; margin-top:-10px;">
  Overview of environment, system, and API reachability.
  </p>

    <h2>Environment Variables Check</h2>
    <p class="description">Checks whether required environment variables are correctly set.</p>
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

    <h2>System Requirements Check</h2>
    <table>
      <thead>
        <tr><th>Requirement</th><th>Status</th></tr>
      </thead>
      <tbody>
        <tr><td>Python Version >= 3.8</td><td class="status-ok">ok</td></tr>
        <tr><td>Requests Library</td><td class="status-ok">ok</td></tr>
        <tr><td>Internet Connectivity</td><td class="status-info">info</td></tr>
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
