import os


def tail_lines(filepath, n=500) -> list:
    """
    Returns the last n lines of a file.
    """
    try:
        with open(filepath, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            block = 4096
            data = b""
            lines = []
            while size > 0 and len(lines) <= n:
                read_size = block if size - block > 0 else size
                f.seek(size - read_size)
                data = f.read(read_size) + data
                size -= read_size
                lines = data.splitlines()
            # decode + keep last n
            decoded = [ln.decode("utf-8", errors="ignore") for ln in lines[-n:]]
            return decoded
    except Exception:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().splitlines()[-n:]
        except Exception:
            return []
