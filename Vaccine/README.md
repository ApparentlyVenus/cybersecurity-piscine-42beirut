# Vaccine

*This project has been created as part of the 42 curriculum by odana*

# Description

A tool that detects SQL injection vulnerabilities in a URL. Given a target and a
parameter, it runs a battery of tests and reports which parameters are injectable,
the payload that worked, and the database engine behind them.

# Requirements

- Python 3
- `requests` (`pip install requests`)

# Usage

```
./vaccine.py [options] URL

```
For GET, put the parameters in the URL query string. For POST, pass them with `-D`.

# Options

| Option | Description |
|--------|-------------|
| `URL` | Target URL (required). Include the query string for GET params. |
| `-o FILE` | Archive file for results. Default: `results.json`. Created on first run. |
| `-X METHOD` | HTTP method, `GET` or `POST`. Default: `GET`. |
| `-D DATA` | POST body as `key=val&key2=val2`. The params tested when `-X POST`. |
| `-A AGENT` | Custom `User-Agent` header. |
| `-C COOKIE` | Custom `Cookie` header (e.g. a session cookie to reach authenticated pages). |

# Detection Techniques

- **Error-based**: sends syntax-breaking payloads (e.g. a lone `'`) and matches
  the database error that leaks into the response. Confirms the vulnerability and
  fingerprints the engine at once.
- **Boolean-based (blind)**: sends a TRUE and a FALSE condition and compares the
  responses. If TRUE matches the normal page and FALSE differs, the param is
  injectable even with no visible error.
- **Time-based (blind)**: injects an engine-specific delay (e.g. `SLEEP(5)`) and
  measures the response time. A response that arrives late confirms execution when
  nothing else is observable.

# Database Engines

Engine detection is by error signature. The tool recognizes **MySQL/MariaDB,
PostgreSQL, Microsoft SQL Server, and Oracle**. The same table drives the
time-based delay payload per engine.

# Testing

Tested against a local [SQLi-Labs](https://github.com/Audi-1/sqli-labs) container:

```
docker run -d -p 8080:80 acgpiano/sqli-labs
# open http://localhost:8080/ once and click "Setup/reset Database"
```

GET, error + boolean + time-based, MySQL:

```
./vaccine.py "http://localhost:8080/Less-1/?id=1"
```

POST, injectable login form:

```
./vaccine.py -X POST -D "uname=admin&passwd=admin" "http://localhost:8080/Less-11/"
```

POST with custom User-Agent and Cookie headers:

```
./vaccine.py -X POST -D "uname=admin&passwd=admin" \
    -A "Mozilla/5.0" -C "PHPSESSID=test123" "http://localhost:8080/Less-11/"
```

Using testasp and testaspnet:

GET requests on both pages

```
./vaccine.py "http://testaspnet.vulnweb.com/ReadNews.aspx?id=0"
```

```
./vaccine.py "http://testasp.vulnweb.com/showforum.asp?id=0"
```