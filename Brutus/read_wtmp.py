import os
import sys
import utmp


class WtmpReader:
    def __init__(self, log_path: str) -> None:
        self.log_path = log_path
        self.entries = []

    def open_log(self) -> None:
        with open(self.log_path, 'rb') as file:
            for entry in utmp.read(file.read()):
                self.entries.append(entry)


def main() -> None:
    try:
        log_path = sys.argv[1]
    except IndexError:
        print("[!] Provide a full path to a wtmp file as the argument.")
        sys.exit(1)

    if os.path.exists(log_path):
        wtmp_reader = WtmpReader(log_path)
    else:
        print(f"[!] wtmp file does not exist at path: {log_path}")
        sys.exit(1)

    wtmp_reader.open_log()

    for entry in wtmp_reader.entries:
        print(f"{entry.time} | {entry.type} | {entry.host} | {entry.user}")


if __name__ == "__main__":
    main()
