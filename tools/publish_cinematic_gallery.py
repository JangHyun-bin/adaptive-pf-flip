#!/usr/bin/env python
"""Publish a cinematic static gallery through a local server and optional cftunnel."""

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


TRYCLOUDFLARE_RE = re.compile(r"https://[A-Za-z0-9.-]+\.trycloudflare\.com")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def posix_rel(path, root):
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path.replace(os.sep, "/")


def choose_port(start):
    import socket

    port = int(start)
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                port += 1
                continue
        return port


def request_check(url, method="GET", timeout=10):
    req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        length = response.headers.get("Content-Length")
        if method == "GET":
            body = response.read()
            size = len(body)
        else:
            size = int(length) if length and length.isdigit() else None
        return {
            "url": url,
            "method": method,
            "status": response.status,
            "content_length": size,
        }


def retry_check(url, method="GET", timeout_seconds=30, request_timeout=10):
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            return request_check(url, method=method, timeout=request_timeout)
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            last_error = str(exc)
            time.sleep(0.5)
    raise RuntimeError(f"HTTP check failed for {url}: {last_error}")


def start_process(command, stdout_log, stderr_log):
    os.makedirs(os.path.dirname(stdout_log), exist_ok=True)
    stdout = open(stdout_log, "ab")
    stderr = open(stderr_log, "ab")
    flags = 0
    if os.name == "nt":
        flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        flags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        return subprocess.Popen(command, stdout=stdout, stderr=stderr, creationflags=flags)
    finally:
        stdout.close()
        stderr.close()


def find_cloudflared(explicit):
    if explicit:
        if os.path.isfile(explicit):
            return os.path.abspath(explicit)
        raise SystemExit(f"cloudflared not found: {explicit}")
    found = shutil.which("cloudflared") or shutil.which("cloudflared.exe")
    if found:
        return found
    raise SystemExit("cloudflared executable was not found on PATH")


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def wait_for_tunnel_url(log_paths, timeout_seconds):
    deadline = time.time() + timeout_seconds
    seen = ""
    while time.time() < deadline:
        seen = "\n".join(read_text(path) for path in log_paths)
        match = TRYCLOUDFLARE_RE.search(seen)
        if match:
            return match.group(0)
        time.sleep(0.5)
    tail = seen[-2000:]
    raise RuntimeError(f"Timed out waiting for trycloudflare URL. Log tail:\n{tail}")


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def stop_pid(pid):
    if not pid:
        return {"pid": pid, "status": "skipped"}
    try:
        os.kill(int(pid), signal.SIGTERM)
        return {"pid": int(pid), "status": "signaled"}
    except ProcessLookupError:
        return {"pid": int(pid), "status": "not_found"}
    except OSError as exc:
        return {"pid": int(pid), "status": "error", "error": str(exc)}


def stop_from_manifest(path):
    manifest_path = os.path.abspath(path)
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    processes = manifest.get("processes", {})
    results = [
        stop_pid(processes.get("cloudflared_pid")),
        stop_pid(processes.get("server_pid")),
    ]
    manifest["status"] = "stopped"
    manifest["stopped_utc"] = now_iso()
    manifest["stop_results"] = results
    write_json(manifest_path, manifest)
    print(json.dumps({
        "status": "stopped",
        "manifest": manifest_path,
        "stop_results": results,
    }, indent=2, sort_keys=True))


def markdown_report(manifest, root):
    lines = [
        "# Cinematic Gallery Publish Report",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        f"Gallery directory: `{posix_rel(manifest['gallery_dir'], root)}`",
        f"Manifest: `{posix_rel(manifest['manifest_path'], root)}`",
        "",
        "## URLs",
        "",
        f"- Local: `{manifest['local_url']}`",
    ]
    if manifest.get("public_url"):
        lines.append(f"- Public: `{manifest['public_url']}`")
    lines.extend([
        "",
        "## Processes",
        "",
        f"- HTTP server PID: `{manifest['processes']['server_pid']}`",
    ])
    if manifest["processes"].get("cloudflared_pid"):
        lines.append(f"- cloudflared PID: `{manifest['processes']['cloudflared_pid']}`")
    lines.extend([
        "",
        "## Checks",
        "",
        "| Target | Method | Status | Bytes |",
        "| --- | --- | ---: | ---: |",
    ])
    for check in manifest["checks"]:
        lines.append(
            f"| `{check['url']}` | `{check['method']}` | {check['status']} | {check.get('content_length', 'n/a')} |"
        )
    lines.extend([
        "",
        "## Logs",
        "",
        f"- `{posix_rel(manifest['logs']['server_stdout'], root)}`",
        f"- `{posix_rel(manifest['logs']['server_stderr'], root)}`",
    ])
    if manifest["logs"].get("cloudflared_stdout"):
        lines.append(f"- `{posix_rel(manifest['logs']['cloudflared_stdout'], root)}`")
    if manifest["logs"].get("cloudflared_stderr"):
        lines.append(f"- `{posix_rel(manifest['logs']['cloudflared_stderr'], root)}`")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("gallery_dir", nargs="?", help="Directory containing index.html and assets/")
    parser.add_argument("--port", type=int, default=8899, help="Preferred local port")
    parser.add_argument("--bind", default="127.0.0.1", help="Local bind address")
    parser.add_argument("--cftunnel", action="store_true", help="Start a Cloudflare quick tunnel")
    parser.add_argument("--cloudflared", help="Path to cloudflared executable")
    parser.add_argument("--manifest", help="Output publish manifest path")
    parser.add_argument("--report", help="Optional Markdown publish report path")
    parser.add_argument("--stop-manifest", help="Stop server/tunnel PIDs recorded in a publish manifest")
    parser.add_argument("--timeout-seconds", type=float, default=60.0, help="Startup and verification timeout")
    args = parser.parse_args(argv)

    root = os.getcwd()
    if args.stop_manifest:
        stop_from_manifest(args.stop_manifest)
        return
    if not args.gallery_dir:
        raise SystemExit("gallery_dir is required unless --stop-manifest is used")
    gallery_dir = os.path.abspath(args.gallery_dir)
    index_path = os.path.join(gallery_dir, "index.html")
    gif_path = os.path.join(gallery_dir, "assets", "shot.gif")
    if not os.path.isfile(index_path):
        raise SystemExit(f"Missing gallery index: {index_path}")
    if not os.path.isfile(gif_path):
        raise SystemExit(f"Missing gallery GIF: {gif_path}")

    manifest_path = os.path.abspath(args.manifest or os.path.join(gallery_dir, "publish_manifest.json"))
    log_dir = os.path.join(gallery_dir, "publish_logs")
    os.makedirs(log_dir, exist_ok=True)
    port = choose_port(args.port)
    local_url = f"http://{args.bind}:{port}"

    server_stdout = os.path.join(log_dir, "http_stdout.log")
    server_stderr = os.path.join(log_dir, "http_stderr.log")
    server = start_process(
        [sys.executable, "-m", "http.server", str(port), "--bind", args.bind, "--directory", gallery_dir],
        server_stdout,
        server_stderr,
    )
    cloudflared = None
    public_url = None
    checks = []

    try:
        checks.append(retry_check(f"{local_url}/index.html", timeout_seconds=args.timeout_seconds))
        checks.append(retry_check(f"{local_url}/assets/shot.gif", method="HEAD", timeout_seconds=args.timeout_seconds))

        cloud_stdout = None
        cloud_stderr = None
        cloudflared_path = None
        if args.cftunnel:
            cloudflared_path = find_cloudflared(args.cloudflared)
            cloud_stdout = os.path.join(log_dir, "cloudflared_stdout.log")
            cloud_stderr = os.path.join(log_dir, "cloudflared_stderr.log")
            cloudflared = start_process(
                [cloudflared_path, "tunnel", "--url", local_url, "--no-autoupdate"],
                cloud_stdout,
                cloud_stderr,
            )
            public_url = wait_for_tunnel_url([cloud_stdout, cloud_stderr], args.timeout_seconds)
            checks.append(retry_check(f"{public_url}/index.html", timeout_seconds=args.timeout_seconds))
            checks.append(retry_check(f"{public_url}/assets/shot.gif", method="HEAD", timeout_seconds=args.timeout_seconds))

        manifest = {
            "status": "running",
            "started_utc": now_iso(),
            "gallery_dir": gallery_dir,
            "index_path": index_path,
            "manifest_path": manifest_path,
            "local_url": local_url,
            "public_url": public_url,
            "checks": checks,
            "processes": {
                "server_pid": server.pid,
                "cloudflared_pid": cloudflared.pid if cloudflared else None,
            },
            "logs": {
                "server_stdout": server_stdout,
                "server_stderr": server_stderr,
                "cloudflared_stdout": cloud_stdout,
                "cloudflared_stderr": cloud_stderr,
            },
            "cloudflared": {
                "enabled": bool(args.cftunnel),
                "path": cloudflared_path if args.cftunnel else None,
            },
        }
        write_json(manifest_path, manifest)
        if args.report:
            report_path = os.path.abspath(args.report)
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(markdown_report(manifest, root))
        print(json.dumps({
            "status": "running",
            "local_url": local_url,
            "public_url": public_url,
            "manifest": manifest_path,
            "server_pid": server.pid,
            "cloudflared_pid": cloudflared.pid if cloudflared else None,
        }, indent=2, sort_keys=True))
    except Exception:
        if cloudflared and cloudflared.poll() is None:
            cloudflared.terminate()
        if server and server.poll() is None:
            server.terminate()
        raise


if __name__ == "__main__":
    main()
