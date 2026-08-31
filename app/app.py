#!/usr/bin/env python3
import csv
import json
import math
import os
import re
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
    body = json.dumps(sanitize_for_json(payload), ensure_ascii=False, indent=2).encode("utf-8")
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


def sanitize_for_json(value):
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: sanitize_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    return value


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
    env.setdefault("LANG", "C.UTF-8")
    env.setdefault("LC_ALL", "C.UTF-8")
    env.setdefault("PYTHONIOENCODING", "utf-8")
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


def parse_float(value):
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text or text.upper() == "N/A":
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


CSV_METRIC_MAP = {
    "Time to First Token (ms)": ("time_to_first_token", "ms"),
    "Request Latency (ms)": ("request_latency", "ms"),
    "Inter Token Latency (ms)": ("inter_token_latency", "ms"),
    "Output Token Throughput (tokens/sec)": ("output_token_throughput", "tokens/sec"),
    "Request Throughput (requests/sec)": ("request_throughput", "requests/sec"),
    "Output Sequence Length (tokens)": ("output_sequence_length", "tokens"),
    "Input Sequence Length (tokens)": ("input_sequence_length", "tokens"),
}


def metric_group(name):
    if name.startswith("Effective ") or name.startswith("Tokens In Flight"):
        return "NVIDIA AIPerf | LLM Metrics: Effective"
    if name.startswith("Active "):
        return "NVIDIA AIPerf | LLM Metrics: Active"
    if name.startswith("Usage ") or name.startswith("Total Usage "):
        return "NVIDIA AIPerf | LLM Metrics: Usage"
    return "NVIDIA AIPerf | LLM Metrics"


def metric_unit(name):
    match = re.search(r"\(([^()]*)\)\s*$", name)
    return match.group(1) if match else ""


def parse_aiperf_csv(path):
    metrics = {}
    sections = []
    section_map = {}
    section_order = {
        "NVIDIA AIPerf | LLM Metrics: Effective": 0,
        "NVIDIA AIPerf | LLM Metrics: Active": 1,
        "NVIDIA AIPerf | LLM Metrics: Usage": 2,
        "NVIDIA AIPerf | LLM Metrics": 3,
    }
    if not path.exists():
        return metrics, sections

    headers = []
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            if row[0] == "Metric":
                headers = row
                continue
            if not headers:
                continue

            name = row[0]
            values = {"unit": metric_unit(name)}
            for index, header in enumerate(headers[1:], start=1):
                if index >= len(row):
                    continue
                stat = "avg" if header == "Value" else header
                number = parse_float(row[index])
                if number is not None:
                    values[stat] = number
            if values.keys() != {"unit"}:
                mapped = CSV_METRIC_MAP.get(name)
                if mapped:
                    key, unit = mapped
                    metrics[key] = {"unit": unit, **{k: v for k, v in values.items() if k != "unit"}}

                group = metric_group(name)
                if group not in section_map:
                    section_map[group] = {"title": group, "metrics": []}
                    sections.append(section_map[group])
                section_map[group]["metrics"].append({"name": name, "values": values})
    sections.sort(key=lambda section: section_order.get(section["title"], 99))
    return metrics, sections


def parse_console_warnings(path):
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    warnings = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if "Warning" not in line or not line.lstrip().startswith(("╭", "┌")):
            index += 1
            continue

        block = [line]
        index += 1
        while index < len(lines):
            block.append(lines[index])
            if lines[index].lstrip().startswith(("╰", "└")):
                break
            index += 1

        title = re.sub(r"[╭─╮┌┐└┘╰│╯]+", " ", block[0]).strip()
        warnings.append({"title": title or "AIPerf Warning", "text": "\n".join(block)})
        index += 1
    return warnings


def load_aiperf_export(artifact_dir):
    export = {}
    json_file = artifact_dir / "profile_export_aiperf.json"
    csv_file = artifact_dir / "profile_export_aiperf.csv"
    console_file = artifact_dir / "profile_export_console.txt"

    if json_file.exists():
        try:
            export = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as exc:
            export = {"parse_warning": f"failed to parse {json_file.name}: {exc}"}

    csv_metrics, sections = parse_aiperf_csv(csv_file)
    for key, value in csv_metrics.items():
        if not isinstance(export.get(key), dict) or not export[key]:
            export[key] = value
    if sections:
        export["_sections"] = sections
    warnings = parse_console_warnings(console_file)
    if warnings:
        export["_warnings"] = warnings
    return sanitize_for_json(export)


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

            process = subprocess.Popen(
                command,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=proxy_env(config),
            )
            assert process.stdout is not None
            for line in process.stdout:
                logs.append(line.rstrip())
                with RUNS_LOCK:
                    RUNS[run_id]["logs"] = "\n".join(logs[-1000:])
            code = process.wait()
            parsed = load_aiperf_export(artifact_dir)
            if parsed:
                results.append({"concurrency": config.get("concurrency"), "artifact_dir": str(artifact_dir), "export": parsed})
                with RUNS_LOCK:
                    RUNS[run_id]["results"] = results

            if code != 0:
                raise RuntimeError(f"aiperf exited with code {code}")

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
