#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("AIPERF_DATA_DIR", "/data/results"))
RUNS_DIR = DATA_DIR / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

RUNS = {}
RUNS_LOCK = threading.Lock()


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def text_response(handler, status, payload, content_type="text/plain; charset=utf-8"):
    body = payload.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length else b"{}"
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc


def normalize_models_url(base_url):
    url = str(base_url or "").strip().rstrip("/")
    if not url:
        raise ValueError("base_url is required")
    return f"{url}/models"


def fetch_models(config):
    url = normalize_models_url(config.get("base_url"))
    api_key = str(config.get("api_key", "")).strip()
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    proxy_enabled = bool(config.get("proxy_enabled"))
    proxy_url = str(config.get("proxy_url", "")).strip()
    proxies = {}
    if proxy_enabled and proxy_url:
        if "://" not in proxy_url:
            proxy_url = "http://" + proxy_url
        proxies = {"http": proxy_url, "https": proxy_url}

    opener = build_opener(ProxyHandler(proxies))
    request = Request(url, headers=headers, method="GET")
    with opener.open(request, timeout=30) as response:
        raw = response.read()
        payload = json.loads(raw.decode("utf-8"))

    models = []
    for item in payload.get("data", []):
        if isinstance(item, dict) and item.get("id"):
            models.append(str(item["id"]))
        elif isinstance(item, str):
            models.append(item)
    return {"models": sorted(set(models)), "url": url}


def aiperf_info():
    exe = shutil.which("aiperf")
    if not exe:
        return {
            "available": False,
            "path": None,
            "message": "aiperf executable was not found in this container",
        }

    probes = [
        [exe, "--version"],
        [exe, "version"],
        [exe, "--help"],
    ]
    for cmd in probes:
        try:
            completed = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20)
            return {
                "available": True,
                "path": exe,
                "command": cmd,
                "exit_code": completed.returncode,
                "output": completed.stdout[:4000],
            }
        except Exception as exc:
            last_error = str(exc)
    return {"available": True, "path": exe, "message": last_error}


def coerce_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def build_aiperf_command(config, artifact_dir):
    endpoint_type = config.get("endpoint_type", "chat")
    streaming = bool(config.get("streaming", True))
    server_token_count = bool(config.get("server_token_count", False))
    fixed_output = bool(config.get("fixed_output", True))
    output_tokens = coerce_int(config.get("output_tokens"), 128)
    warmup_count = max(1, coerce_int(config.get("warmup_count"), 1))

    command = [
        "aiperf",
        "profile",
        "--model",
        config.get("model", "model"),
        "--tokenizer",
        "builtin",
        "--url",
        config.get("base_url", "http://127.0.0.1:8000"),
        "--endpoint-type",
        endpoint_type,
        "--concurrency",
        str(coerce_int(config.get("concurrency"), 1)),
        "--request-count",
        str(coerce_int(config.get("request_count"), 1)),
        "--synthetic-input-tokens-mean",
        str(coerce_int(config.get("input_tokens"), 128)),
        "--synthetic-input-tokens-stddev",
        "0",
        "--output-tokens-mean",
        str(output_tokens),
        "--output-tokens-stddev",
        "0",
        "--warmup-request-count",
        str(warmup_count),
        "--request-timeout-seconds",
        str(coerce_int(config.get("timeout"), 120)),
        "--artifact-dir",
        str(artifact_dir),
        "--ui",
        "none",
    ]

    api_key = config.get("api_key", "")
    if api_key:
        command.extend(["--api-key", api_key])
    if streaming:
        command.append("--streaming")
    if not server_token_count:
        command.append("--no-server-metrics")
    if fixed_output:
        command.extend(["--extra-inputs", f"min_tokens:{output_tokens}", "--extra-inputs", "ignore_eos:true"])
    return command


def proxy_env(config):
    env = os.environ.copy()
    proxy_enabled = bool(config.get("proxy_enabled"))
    proxy_url = str(config.get("proxy_url", "")).strip()
    no_proxy = str(config.get("no_proxy", "")).strip()
    if proxy_enabled and proxy_url:
        if "://" not in proxy_url:
            proxy_url = "http://" + proxy_url
        env["AIPERF_HTTP_TRUST_ENV"] = "true"
        env["HTTP_PROXY"] = proxy_url
        env["HTTPS_PROXY"] = proxy_url
        env["http_proxy"] = proxy_url
        env["https_proxy"] = proxy_url
        if no_proxy:
            env["NO_PROXY"] = no_proxy
            env["no_proxy"] = no_proxy
    return env


def redact_command(command):
    redacted = []
    hide_next = False
    for item in command:
        if hide_next:
            redacted.append("***redacted***")
            hide_next = False
            continue
        redacted.append(item)
        if item == "--api-key":
            hide_next = True
    return redacted


def redact_config(config):
    clean = dict(config)
    if clean.get("api_key"):
        clean["api_key"] = "***redacted***"
    return clean


def run_benchmark(run_id, configs):
    with RUNS_LOCK:
        RUNS[run_id]["status"] = "running"
        RUNS[run_id]["started_at"] = time.time()

    logs = []
    results = []
    try:
        run_dir = RUNS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run.json").write_text(json.dumps({"configs": [redact_config(c) for c in configs]}, indent=2), encoding="utf-8")

        for config in configs:
            artifact_dir = run_dir / f"c{coerce_int(config.get('concurrency'), 1)}"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            command = build_aiperf_command(config, artifact_dir)
            if config.get("proxy_enabled") and config.get("proxy_url"):
                logs.append(f"Proxy enabled for AIPerf: {config.get('proxy_url')}")
            logs.append("$ " + " ".join(redact_command(command)))

            if not shutil.which("aiperf"):
                raise RuntimeError("aiperf executable is not available in this container")

            process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=proxy_env(config))
            assert process.stdout is not None
            for line in process.stdout:
                logs.append(line.rstrip())
                with RUNS_LOCK:
                    RUNS[run_id]["logs"] = "\n".join(logs[-1000:])
            code = process.wait()
            if code != 0:
                raise RuntimeError(f"aiperf exited with code {code}")

            export_file = artifact_dir / "profile_export_aiperf.json"
            parsed = {}
            if export_file.exists():
                parsed = json.loads(export_file.read_text(encoding="utf-8"))
            results.append({"concurrency": config.get("concurrency"), "artifact_dir": str(artifact_dir), "export": parsed})

        with RUNS_LOCK:
            RUNS[run_id].update({"status": "succeeded", "results": results, "logs": "\n".join(logs[-1000:]), "finished_at": time.time()})
    except Exception as exc:
        logs.append(f"ERROR: {exc}")
        with RUNS_LOCK:
            RUNS[run_id].update({"status": "failed", "error": str(exc), "logs": "\n".join(logs[-1000:]), "finished_at": time.time()})


class Handler(BaseHTTPRequestHandler):
    server_version = "aiperf-gui/0.1"

    def log_message(self, fmt, *args):
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), fmt % args), flush=True)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            text_response(self, 200, (APP_DIR / "index.html").read_text(encoding="utf-8"), "text/html; charset=utf-8")
            return
        if path == "/help.html":
            text_response(self, 200, (APP_DIR / "help.html").read_text(encoding="utf-8"), "text/html; charset=utf-8")
            return
        if path == "/health":
            json_response(self, 200, {"ok": True, "service": "aiperf-gui", "aiperf": aiperf_info()["available"]})
            return
        if path == "/api/aiperf-info":
            json_response(self, 200, aiperf_info())
            return
        if path == "/api/runs":
            with RUNS_LOCK:
                payload = {"runs": list(RUNS.values())}
            json_response(self, 200, payload)
            return
        if path.startswith("/api/runs/"):
            run_id = path.rsplit("/", 1)[-1]
            with RUNS_LOCK:
                run = RUNS.get(run_id)
            if not run:
                json_response(self, 404, {"error": "run not found"})
                return
            json_response(self, 200, run)
            return
        json_response(self, 404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/models":
            try:
                payload = read_json(self)
                config = payload.get("config", payload)
                json_response(self, 200, fetch_models(config))
            except Exception as exc:
                json_response(self, 400, {"error": str(exc)})
            return
        if path != "/api/benchmark":
            json_response(self, 404, {"error": "not found"})
            return
        try:
            payload = read_json(self)
            base_config = payload.get("config", {})
            concurrencies = payload.get("concurrencies") or [base_config.get("concurrency", 1)]
            configs = []
            for concurrency in concurrencies:
                config = dict(base_config)
                config["concurrency"] = coerce_int(concurrency, 1)
                configs.append(config)
            run_id = uuid.uuid4().hex[:12]
            with RUNS_LOCK:
                RUNS[run_id] = {
                    "id": run_id,
                    "status": "queued",
                    "created_at": time.time(),
                    "configs": [redact_config(c) for c in configs],
                    "logs": "",
                    "results": [],
                }
            thread = threading.Thread(target=run_benchmark, args=(run_id, configs), daemon=True)
            thread.start()
            json_response(self, 202, {"run_id": run_id, "status_url": f"/api/runs/{run_id}"})
        except Exception as exc:
            json_response(self, 400, {"error": str(exc)})


def main():
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8080"))
    print(f"AIPerf GUI listening on http://{host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
