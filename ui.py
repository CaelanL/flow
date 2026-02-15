import tkinter as tk

TRANSPARENT = "#ff00ff"

WIDTH_IDLE = 28
WIDTH_ACTIVE = 70
HEIGHT = 28
RADIUS = 14


class FlowUI:
    ICONS = {
        "recording": "\u223F",         # ∿  wave
        "locked": "\u223F",            # ∿  wave
        "transcribing": "\u2026",      # …  dots
    }
    ACCENT = {
        "idle": "#555555",
        "recording": "#e74c3c",
        "locked": "#e74c3c",
        "transcribing": "#f39c12",
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Flow")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9)
        self.root.configure(bg=TRANSPARENT)
        self.root.attributes("-transparentcolor", TRANSPARENT)
        self._cancel_callback = None
        self._current_width = WIDTH_IDLE

        self.canvas = tk.Canvas(
            self.root,
            width=WIDTH_ACTIVE,
            height=HEIGHT,
            bg=TRANSPARENT,
            highlightthickness=0,
        )
        self.canvas.pack()

        # These get drawn/redrawn on state change
        self._pill = None
        self._border = None
        self._dot = None
        self._icon = None
        self._cancel = None

        self._draw_idle()
        self._position_window(WIDTH_IDLE)

    def _clear(self):
        self.canvas.delete("all")

    def _draw_idle(self):
        self._clear()
        w = WIDTH_IDLE
        self._current_width = w
        self._pill = self._draw_pill(0, 0, w, HEIGHT, RADIUS, "#1a1a1a", "")
        self._dot = self.canvas.create_oval(
            w // 2 - 4, HEIGHT // 2 - 4, w // 2 + 4, HEIGHT // 2 + 4,
            fill="#555555", outline="",
        )

    def _draw_active(self, state):
        self._clear()
        w = WIDTH_ACTIVE
        self._current_width = w
        accent = self.ACCENT.get(state, "#e74c3c")
        icon = self.ICONS.get(state, "\u223F")

        self._pill = self._draw_pill(0, 0, w, HEIGHT, RADIUS, "#1a1a1a", "")

        # Border for locked
        if state == "locked":
            self._border = self._draw_pill(0, 0, w, HEIGHT, RADIUS, "", "#ffffff")

        # Dot on left
        self._dot = self.canvas.create_oval(
            12, HEIGHT // 2 - 4, 20, HEIGHT // 2 + 4,
            fill=accent, outline="",
        )

        # Icon in middle
        self._icon = self.canvas.create_text(
            36, HEIGHT // 2,
            text=icon, fill="#cccccc",
            font=("Segoe UI", 11), anchor="center",
        )

        # X button for recording/locked
        if state in ("recording", "locked"):
            self._cancel = self.canvas.create_text(
                w - 14, HEIGHT // 2,
                text="X", fill="#888888",
                font=("Segoe UI", 8, "bold"), anchor="center",
            )
            self.canvas.tag_bind(self._cancel, "<Button-1>", self._on_cancel_click)
            self.canvas.tag_bind(self._cancel, "<Enter>", lambda e: self.canvas.itemconfigure(self._cancel, fill="#ffffff"))
            self.canvas.tag_bind(self._cancel, "<Leave>", lambda e: self.canvas.itemconfigure(self._cancel, fill="#888888"))

    def _draw_pill(self, x1, y1, x2, y2, r, fill, outline):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.canvas.create_polygon(
            points, fill=fill, outline=outline, smooth=True, width=2,
        )

    def _position_window(self, w):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = screen_h - 100
        self.root.geometry(f"{WIDTH_ACTIVE}x{HEIGHT}+{x}+{y}")

    def set_cancel_callback(self, callback):
        self._cancel_callback = callback

    def _on_cancel_click(self, event):
        if self._cancel_callback:
            self._cancel_callback()

    def set_state(self, state):
        self.root.after(0, self._update, state)

    def _update(self, state):
        if state == "idle":
            self._draw_idle()
        else:
            self._draw_active(state)
        self._position_window(self._current_width)

    def run(self):
        self.root.mainloop()

    def quit(self):
        self.root.quit()
