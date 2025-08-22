import os, sys, subprocess, time, signal, webbrowser
import webview

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_URL = f"http://127.0.0.1:{PORT}"

AUTO_CHECK = os.getenv("AUTO_CHECK_UPDATES", "true").lower() == "true"
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "stable")

class ProcGroup:
    def __init__(self):
        self.streamlit = None
        self.trader = None

    def is_running(self, p):
        return p is not None and p.poll() is None

    def start_trader(self):
        if self.is_running(self.trader):
            return
        # run as a module so PyInstaller finds imports
        self.trader = subprocess.Popen(
            [sys.executable, "-m", "src.paper_trader"], cwd=ROOT
        )

    def stop_trader(self):
        if self.is_running(self.trader):
            try:
                if os.name == "nt":
                    self.trader.terminate()
                else:
                    self.trader.send_signal(getattr(signal, "SIGINT", signal.SIGTERM))
                for _ in range(50):
                    if not self.is_running(self.trader):
                        break
                    time.sleep(0.1)
            except Exception:
                pass
            try:
                self.trader.kill()
            except Exception:
                pass
        self.trader = None

    def start_streamlit(self):
        if self.is_running(self.streamlit):
            return
        env = os.environ.copy()
        env.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
        env.setdefault("STREAMLIT_SERVER_PORT", str(PORT))
        self.streamlit = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "dashboard/app.py"],
            cwd=ROOT,
            env=env,
        )

    def stop_streamlit(self):
        if self.is_running(self.streamlit):
            try:
                self.streamlit.terminate()
                for _ in range(50):
                    if not self.is_running(self.streamlit):
                        break
                    time.sleep(0.1)
            except Exception:
                pass
            try:
                self.streamlit.kill()
            except Exception:
                pass
        self.streamlit = None

    def stop_all(self):
        self.stop_trader()
        self.stop_streamlit()


PROCS = ProcGroup()


class Api:
    def start_all(self):
        PROCS.start_streamlit()
        PROCS.start_trader()
        return "started"

    def stop_trader(self):
        PROCS.stop_trader()
        return "stopped"

    def stop_all(self):
        PROCS.stop_all()
        return "stopped"

    def open_in_browser(self):
        webbrowser.open_new_tab(STREAMLIT_URL)
        return "ok"

    def check_updates(self):
        from src.version import __version__ as cur
        from src.updater import latest_release, compare_versions, download_and_launch

        tag, name, asset = latest_release(include_prerelease=(UPDATE_CHANNEL == "prerelease"))
        if not tag:
            return {"status": "error", "msg": "No releases found."}
        cmp = compare_versions(tag, cur)
        if cmp <= 0:
            return {"status": "ok", "msg": f"Up to date (current {cur}, latest {tag})."}
        if not asset:
            return {
                "status": "warn",
                "msg": f"Update {tag} available, but no installer asset for this platform.",
            }
        path = download_and_launch(asset)
        return {"status": "launch", "msg": f"Launched installer: {os.path.basename(path)}"}


def wait_for_streamlit(timeout_s=40):
    import socket
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            s = socket.create_connection(("127.0.0.1", PORT), 0.2)
            s.close()
            return True
        except Exception:
            time.sleep(0.2)
    return False


def main():
    api = Api()
    api.start_all()
    wait_for_streamlit()

    overlay = f"""
    <style>
      .overlay {{ position: fixed; top: 10px; right: 10px; z-index: 9999; font-family: system-ui, sans-serif; }}
      .overlay button {{ margin-left: 6px; padding: 6px 10px; border-radius: 8px; border: 1px solid #ddd; cursor: pointer; }}
      .overlay .danger {{ background:#b91c1c; color:white; border:none; }}
      .overlay .ok {{ background:#16a34a; color:white; border:none; }}
      .overlay .ghost {{ background:white; color:#111; }}
      .overlay .info {{ background:#0ea5e9; color:white; border:none; }}
    </style>
    <div class="overlay">
      <button class="ok" onclick="pywebview.api.start_all()">Start</button>
      <button class="ghost" onclick="pywebview.api.open_in_browser()">Open in browser</button>
      <button class="info" onclick="(async()=>{{ const r = await pywebview.api.check_updates(); alert(r.msg); }})()">Check updates</button>
      <button class="danger" onclick="pywebview.api.stop_trader()">Stop bot</button>
      <button class="danger" onclick="pywebview.api.stop_all()">Quit all</button>
    </div>
    """

    window = webview.create_window(
        "Trading Bot Dashboard", f"http://127.0.0.1:{PORT}", width=1200, height=800
    )

    def _inject():
        # inject overlay
        webview.windows[0].evaluate_js(
            f"document.body.insertAdjacentHTML('beforeend', `{overlay}`)"
        )
        # optional: auto check updates
        if AUTO_CHECK:
            webview.windows[0].evaluate_js("""
                (async () => {
                  const r = await pywebview.api.check_updates();
                  if (r.status === 'launch') { alert(r.msg); }
                })();
            """)

    webview.start(func=_inject, api=api, debug=False)


if __name__ == "__main__":
    try:
        main()
    finally:
        PROCS.stop_all()
