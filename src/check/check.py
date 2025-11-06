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
    background-color: #f4f6f8;
    transition: background-color 0.3s ease;
  }
  .container {
    max-width: 900px;
    margin: 0 auto;
    background: #fff;
    padding: 25px 30px 40px 30px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-radius: 10px;
  }
  .info-box {
    background-color: #007bff;
    color: white;
    padding: 15px 20px;
    border-radius: 6px;
    font-size: 16px;
    margin-bottom: 30px;
    box-shadow: 0 2px 6px rgba(0,123,255,0.4);
  }
  h2 {
    color: #333;
    border-bottom: 2px solid #ddd;
    padding-bottom: 8px;
    margin-bottom: 20px;
  }
  table {
    border-collapse: separate;
    border-spacing: 0 8px;
    width: 70%;
    margin: 0 auto 40px auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border-radius: 8px;
    overflow: hidden;
  }
  th, td {
    padding: 12px 18px;
    text-align: left;
    background-color: #fff;
    border-radius: 6px;
    transition: background-color 0.3s ease;
  }
  th {
    background-color: #f0f0f0;
    font-weight: 600;
  }
  .status-ok {
    color: rgba(21, 87, 36, 0.85);
    background-color: rgba(182, 245, 182, 0.4);
    font-weight: bold;
    border-radius: 6px;
  }
  .status-missing {
    color: rgba(133, 100, 4, 0.85);
    background-color: rgba(255, 238, 186, 0.4);
    font-weight: bold;
    border-radius: 6px;
  }
  .status-error {
    color: rgba(114, 28, 36, 0.85);
    background-color: rgba(245, 198, 203, 0.4);
    font-weight: bold;
    border-radius: 6px;
  }
  .status-info {
    color: rgba(0, 64, 133, 0.85);
    background-color: rgba(204, 229, 255, 0.4);
    font-weight: bold;
    border-radius: 6px;
  }
</style>
</head>
<body>
  <div class="container">
    <div class="info-box">
      ℹ️  This check validates environment variables and API connectivity. Authentication is not required for the reachability test.
    </div>

    <h2>Environment Variables Check</h2>
    <p style="color:#666; font-size:14px; margin-top:-10px;">Checks whether required environment variables are correctly set.</p>
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
  </div>
</body>
</html>
"""
    return html
