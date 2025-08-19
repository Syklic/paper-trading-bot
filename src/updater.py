import os, sys, platform, tempfile, subprocess, stat, requests

GITHUB_REPO = os.getenv("GITHUB_REPO", "Syklic/paper-trading-bot")
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "stable")

def _platform_targets():
    s = platform.system().lower()
    if "windows" in s: return ["Setup.exe", ".exe"]
    if "linux" in s: return ["AppImage", ".AppImage", ".run"]
    if "darwin" in s or "mac" in s: return [".dmg",".pkg",".app.zip"]
    return []

def _choose_asset(assets):
    targets = _platform_targets()
    for t in targets:
        for a in assets:
            if t.lower() in a.get("name","").lower():
                return a
    return assets[0] if assets else None

def latest_release(include_prerelease=False):
    base = "https://api.github.com"
    if include_prerelease:
        r = requests.get(f"{base}/repos/{GITHUB_REPO}/releases", timeout=15)
        r.raise_for_status()
        arr = r.json()
        if not arr: return None
        rel = arr[0]
    else:
        r = requests.get(f"{base}/repos/{GITHUB_REPO}/releases/latest", timeout=15)
        r.raise_for_status()
        rel = r.json()
    asset = _choose_asset(rel.get("assets", []))
    return (rel.get("tag_name"), rel.get("name"), asset)

def download_and_launch(asset):
    url = asset["browser_download_url"]
    name = asset["name"]
    fd, path = tempfile.mkstemp(prefix="update_", suffix="_"+name); os.close(fd)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk: f.write(chunk)
    if os.name != "nt":
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    if os.name == "nt":
        subprocess.Popen([path], shell=False)
    else:
        subprocess.Popen([path])
    return path

def compare_versions(a,b):
    def n(x): 
        out=[]; 
        [out.append(int(p)) if p.isdigit() else out.append(0) for p in x.strip("v").split(".")]
        return out
    aa,bb=n(a),n(b)
    for i in range(max(len(aa),len(bb))):
        va = aa[i] if i<len(aa) else 0
        vb = bb[i] if i<len(bb) else 0
        if va>vb: return 1
        if va<vb: return -1
    return 0
