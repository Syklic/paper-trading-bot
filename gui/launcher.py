import os
import sys
import time
import socket
import subprocess
import webbrowser
from pathlib import Path


def _has_free_port(start=8501, end=8999):
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free TCP ports found in range 8501-8999")

def _app_path():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    # Support onedir (files next to exe) and onefile (extracted to MEIPASS)
    # The repo keeps the dashboard at dashboard/app.py
    # First try alongside the executable dir
    p = base / "dashboard" / "app.py"
    if p.exists():
        return str(p)
    # Try when running from source (gui/launcher.py within repo)
    p2 = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"
    return str(p2)

def main():
    app = _app_path()
    if not os.path.exists(app):
        raise SystemExit(f"Could not locate dashboard/app.py at: {app}")

    port = _has_free_port()
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = str(port)
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["PYTHONWARNINGS"] = env.get("PYTHONWARNINGS", "ignore")

    # If running under PyInstaller onefile/onedir, sys.executable is our launcher.
    # Use the embedded python to run streamlit module so it resolves package resources.
    py = sys.executable
    cmd = [
        py, "-m", "streamlit", "run", app,
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]

    # Start Streamlit server
    server = subprocess.Popen(cmd, env=env)

    # Wait for server to come up
    url = f"http://127.0.0.1:{port}"
    for _ in range(120):  # ~60s
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.25):
                break
        except OSError:
            time.sleep(0.5)
    else:
        # Failed to start
        webbrowser.open(url)
        server.wait()
        return

    # Try to bring up an embedded window via pywebview, if present
    try:
        import webview  # pywebview
        window = webview.create_window("Paper Trading Bot", url=url, width=1220, height=800)
        webview.start(gui=None)  # let pywebview choose backend
    except Exception:
        # Fallback to default browser
        webbrowser.open(url)
        try:
            server.wait()
        except KeyboardInterrupt:
            pass

    # Ensure the server is terminated on close
    try:
        server.terminate()
    except Exception:
        pass

if __name__ == "__main__":
    main()
