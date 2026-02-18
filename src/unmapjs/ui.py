import sys
import threading
import shutil


# ANSI colors
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    # Colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    # Bright
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
BAR_FILL = "━"
BAR_EMPTY = "─"
BAR_HEAD = "╸"

# Global lock so verbose logs don't collide with animations
_output_lock = threading.Lock()


def print_banner(text):
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("github:"):
            sys.stdout.write(f"{C.BRIGHT_YELLOW}{line.rstrip()}{C.RESET}\n")
        else:
            sys.stdout.write(f"{C.BRIGHT_RED}{C.BOLD}{line.rstrip()}{C.RESET}\n")
    sys.stdout.write("\n")
    sys.stdout.flush()


def log_verbose(msg):
    with _output_lock:
        sys.stdout.write(f"\r\033[K    {C.DIM}>{C.RESET} {C.DIM}{msg}{C.RESET}\n")
        sys.stdout.flush()


class Spinner:
    def __init__(self, message):
        self.message = message
        self._stop = threading.Event()
        self._thread = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self, final_message=None):
        self._stop.set()
        if self._thread:
            self._thread.join()
        msg = final_message if final_message else self.message
        with _output_lock:
            sys.stdout.write(f"\r\033[K  {C.GREEN}✓{C.RESET} {msg}\n")
            sys.stdout.flush()

    def update(self, message):
        self.message = message

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
            with _output_lock:
                sys.stdout.write(f"\r\033[K  {C.CYAN}{frame}{C.RESET} {C.DIM}{self.message}{C.RESET}")
                sys.stdout.flush()
            i += 1
            self._stop.wait(0.08)


class ProgressBar:
    def __init__(self, label, total):
        self.label = label
        self.total = total
        self.done = 0
        self._lock = threading.Lock()
        self._spinner_idx = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def update(self, done):
        with self._lock:
            self.done = done

    def _render(self):
        cols = shutil.get_terminal_size((80, 24)).columns
        frame = SPINNER_FRAMES[self._spinner_idx % len(SPINNER_FRAMES)]
        self._spinner_idx += 1

        with self._lock:
            done = self.done
            total = self.total

        if total == 0:
            pct = 0
        else:
            pct = done / total

        count_str = f"{done}/{total}"
        pct_str = f"{int(pct * 100)}%"

        # Raw prefix/suffix for width calc (no ANSI)
        prefix_raw = f"  {frame} {self.label} "
        suffix_raw = f" {pct_str} {count_str}"
        bar_width = cols - len(prefix_raw) - len(suffix_raw) - 1
        if bar_width < 10:
            bar_width = 10

        filled = int(bar_width * pct)
        if filled < bar_width and filled > 0:
            bar = BAR_FILL * (filled - 1) + BAR_HEAD + BAR_EMPTY * (bar_width - filled)
        elif filled >= bar_width:
            bar = BAR_FILL * bar_width
        else:
            bar = BAR_EMPTY * bar_width

        # Colored output
        prefix = f"  {C.CYAN}{frame}{C.RESET} {C.DIM}{self.label}{C.RESET} "
        bar_colored = f"{C.MAGENTA}{bar[:filled]}{C.RESET}{C.DIM}{bar[filled:]}{C.RESET}"
        suffix = f" {C.BRIGHT_WHITE}{pct_str}{C.RESET} {C.DIM}{count_str}{C.RESET}"

        with _output_lock:
            sys.stdout.write(f"\r\033[K{prefix}{bar_colored}{suffix}")
            sys.stdout.flush()

    def _animate(self):
        while not self._stop.is_set():
            self._render()
            self._stop.wait(0.08)

    def finish(self, final_text=None):
        self._stop.set()
        self._thread.join()
        with self._lock:
            done = self.done
            total = self.total
        msg = final_text if final_text else f"{self.label} {done}/{total}"
        with _output_lock:
            sys.stdout.write(f"\r\033[K  {C.GREEN}✓{C.RESET} {msg}\n")
            sys.stdout.flush()
