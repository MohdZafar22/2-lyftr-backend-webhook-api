
from collections import defaultdict

http_requests = defaultdict(int)
webhook_results = defaultdict(int)
latencies = []

def record_http(path, status):
    http_requests[(path, status)] += 1

def record_webhook(result):
    webhook_results[result] += 1

def observe_latency(ms):
    latencies.append(ms)

def render_metrics():
    lines = []

    for (path, status), count in http_requests.items():
        lines.append(
            f'http_requests_total{{path="{path}",status="{status}"}} {count}'
        )

    for result, count in webhook_results.items():
        lines.append(
            f'webhook_requests_total{{result="{result}"}} {count}'
        )

    for bound in [100, 500]:
        lines.append(
            f'request_latency_ms_bucket{{le="{bound}"}} '
            f'{len([l for l in latencies if l <= bound])}'
        )

    lines.append(f'request_latency_ms_bucket{{le="+Inf"}} {len(latencies)}')
    lines.append(f"request_latency_ms_count {len(latencies)}")

    return "\n".join(lines)
