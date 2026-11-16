import ast
import re
from datetime import datetime
import orjson
from typing import List, Dict, Any, Optional
from pathlib import Path
from operator import itemgetter



class Filters:

    _KEYS = {
        "ClientAddr" : "string : Client IP address with port",
        "ClientHost" : "string : Client hostname (if resolvable)",
        "ClientPort" : "string : Client source port",
        "ClientUsername" : "string : Client username ('-' if unauthenticated)",
        "RequestMethod" : "string : HTTP method (GET, POST, PUT, DELETE, etc.)",
        "RequestPath" : "string : Full request path ('/', '/api/xxx', etc.)",
        "RequestHost" : "string : Host header received from the client",
        "RequestAddr" : "string : Host header received from the client",
        "RequestProtocol" : "string : HTTP protocol (HTTP/1.1, HTTP/2.0)",
        "RequestScheme" : "string : Transport scheme ('http', 'https')",
        "RequestContentLength" : "int : Size of the content sent by the client (bytes)",
        "RequestCount" : "int : Total number of requests (cumulative or session)",
        "RetryAttempts" : "int : Retry attempts (0 by default)",
        "DownstreamStatus" : "int : HTTP status code returned to the client (200, 401, 502, etc.)",
        "DownstreamContentSize" : "int : Size of the content returned by Traefik (bytes)",
        "Overhead" : "int : Additional time added by Traefik (µs)",
        "OriginStatus" : "int : HTTP status code returned by the backend (0 if no response)",
        "OriginDuration" : "int : Processing duration by the backend only (µs), 0 if none",
        "OriginContentSize" : "int : Actual content size from the backend (bytes)",
        "Duration" : "int : Total processing duration by Traefik including the backend (µs)",
        "GzipRatio" : "float : Gzip compression ratio if enabled",
        "TLSCipher" : "string : Cipher suite used for encryption ('TLS_AES_128_GCM_SHA256')",
        "TLSVersion" : "string : TLS version used ('1.2', '1.3', etc.)",
        "TrustForwardHeader" : "boolean : (in middleware, not log) If true, trusts X-Forwarded-* headers",
        "RouterName" : "string : Name of the router that handled the request ('router-name@provider')",
        "ServiceName" : "string : Name of the backend service ('service-name@provider')",
        "ServiceAddress" : "string : Backend IP address ('sync-in:80', etc.)",
        "ServiceURL" : "string : Full backend URL ('http://sync-in:80')",
        "entryPointName" : "string : Name of the entrypoint used ('websecure', 'traefik', etc.)",
        "StartLocal" : "string : Timestamp in server local format (with timezone)",
        "StartUTC" : "string : Pure UTC timestamp for reproducibility",
        "time" : "string : Final request timestamp ('YYYY-MM-DDTHH:MM:SS+XX:XX')",
        "level" : "string : Log level (info, warning, error)",
        "msg" : "string : Log message (often empty)  ",
        }
    
    _FILTERS = {
        "="  : "equals",
        "!=" : "not equals",
        ">"  : "greater (numeric or timestamp only)",
        ">="  : "greater or equal (numeric or timestamp only)",
        "<"  : "lower (numeric or timestamp only)",
        "<="  : "lower or equal (numeric or timestamp only)",
        "~"  : "contains (str or timestamp only)",
        }

    _OPERATORS = {
        "&&" : "'and' operator",
        "||" : "'or' operator"
        }

    _TIMESTAMP_KEYS = ["time", "StartLocal", "StartUTC"]


    def __init__(self, expr: str):
        self.expr = Filters._translate(expr)
        Filters._validate_keys(self.expr)

        self.code = compile(self._translate(expr), "<string>", "eval")

    @classmethod
    def _validate_keys(cls,expr: str) -> None:
        tree = ast.parse(expr, mode="eval")
        used_keys = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id != 'str': # ignore str format flag
                    used_keys.append(node.id)

        traefik_keys = list(Filters._KEYS.keys())
        for key in used_keys:
            if key not in traefik_keys:
                error_msg = [f"Filter key '{key}' does not exist."]
                error_msg.append("Available keys are :")
                for k, v in Filters._KEYS.items():
                    error_msg.append(f" - {k} : {v}")
                error_msg = "\n".join(error_msg)
                raise Exception(error_msg)

    @staticmethod
    def _translate(expr: str) -> str:
        # Traduction syntaxique : && -> and, ~ -> in str()
        expr = expr.replace("&&", "and").replace("||", "or")
        expr = re.sub(r"(?<=\w)=(?=['\"])", " == ", expr)
        expr = expr.replace(" = ", " == ")
        expr = re.sub(r"(?<=\w)!=(?=['\"])", " != ", expr)
        expr = re.sub(r"(?<=\w)<=(?=['\"])", " <= ", expr)
        expr = re.sub(r"(?<=\w)>=(?=['\"])", " >= ", expr)
        expr = re.sub(r"(?<=\w)<(?=['\"])", " < ", expr)
        expr = re.sub(r"(?<=\w)>(?=['\"])", " > ", expr)
        expr = re.sub(r"(?<=\w)~(?=['\"])", " ~ ", expr)
        expr = re.sub(
            r"(\w+)\s*~\s*['\"]([^'\"]+)['\"]", r"'\2' in str(\1)", expr
        )
        return expr

    def match(self, record: dict) -> bool:
        try:
            # Isolated evaluation context (security + speed)
            return bool(eval(self.code, {"__builtins__": {}, "str": str, "dt": datetime}, record))
        except KeyError:
            return False


async def RequestAccessLog(
        access_log_file: Path,
        filter_expr: str,
        page:int = 1,
        per_page:int = 10,
        sort: Optional[str] = '-time',
        ) -> List[Dict[str, Any]]:
    # TODO: Add a quick search with escape when requested page is full.

    def _StreamAccesLogFile(filepath: str):
        """Read a file line by line and stream it)."""

        def _normalize_iso(s: str) -> str:
            return re.sub(r"(\.\d{6})\d+", r"\1", s)

        with open(filepath, "r", encoding="utf-8") as f:  # Read-only mode - no exclusive lock
            for line in f:
                if not line.strip():
                    continue
                record = orjson.loads(line)
                # Convert timestamps
                for k in Filters._TIMESTAMP_KEYS:
                    record[k] = _normalize_iso(record[k])
                yield record

    filter = Filters(filter_expr)
    filtered = []
    # start = (page - 1) * per_page
    # end = start + per_page
    for i, entry in enumerate(_StreamAccesLogFile(access_log_file.resolve().as_posix())):
        if filter.match(entry):
            # if start <= len(res) < end:
            #     res.append(entry)
            # elif len(res) >= end:
            #     break
            filtered.append(entry)
            
    # Sort filtered results
    if sort:
        if sort[1:] not in list(Filters._KEYS.keys()):
            sort = None
            # TODO : raise ?

    if sort[0] == '+':
        filtered.sort(key=itemgetter(sort[1:]))
    elif sort[0] == '-':
        filtered.sort(key=itemgetter(sort[1:]), reverse=True)

    # Keep resquested page
    start = (page - 1) * per_page
    end = min(len(filtered), start + per_page)

    output = {
        "total_pages": int(len(filtered) / per_page),
        "total_items": len(filtered),
        "results": filtered[start:end]
    }    
    return output

if __name__ == '__main__':

    entry = {
        "ClientAddr":"172.29.0.1:35360",
        "ClientHost":"172.29.0.1",
        "ClientPort":"35360",
        "ClientUsername":"-",
        "DownstreamContentSize":6843,
        "DownstreamStatus":200,
        "Duration":1105237,
        "OriginContentSize":6843,
        "OriginDuration":866799,
        "OriginStatus":200,
        "Overhead":238438,
        "RequestAddr":"draw.secure.my-domain.com",
        "RequestContentSize":0,
        "RequestCount":338081,
        "RequestHost":"draw.secure.my-domain.com",
        "RequestMethod":"GET",
        "RequestPath":"/",
        "RequestPort":"-",
        "RequestProtocol":"HTTP/2.0",
        "RequestScheme":"https",
        "RetryAttempts":0,
        "RouterName":"draw-secure@file",
        "ServiceAddr":"excalidraw:80",
        "ServiceName":"draw-service@file",
        "ServiceURL":"http://excalidraw:80",
        "StartLocal":"2026-11-13T18:29:16.173468855+01:00",
        "StartUTC":"2026-11-13T17:29:16.173468855Z",
        "TLSCipher":"TLS_AES_128_GCM_SHA256",
        "TLSVersion":"1.3",
        "entryPointName":"websecure",
        "level":"info",
        "msg":"",
        "time":"2026-11-13T18:29:16+01:00"
        }
    filter = Filters("RequestMethod='GET' && DownstreamStatus = 200")
    print(f"{filter.expr} : {filter.match(entry)}")