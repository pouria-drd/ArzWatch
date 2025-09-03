import json


def parse_json_lines(lines) -> list:
    """
    Parses JSON lines from a list of strings.
    """
    parsed = []
    for ln in lines:
        try:
            obj = json.loads(ln)
            parsed.append(
                {
                    "time": obj.get("time", ""),
                    "level": obj.get("level", ""),
                    "name": obj.get("name", ""),
                    "message": obj.get("message", ln),
                    "raw": ln,
                }
            )
        except json.JSONDecodeError:
            parsed.append(
                {
                    "time": "",
                    "level": "",
                    "name": "",
                    "message": ln,
                    "raw": ln,
                }
            )
    return parsed
