import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import threading

CONFIG_FILE = "streamer_config.json"
DEFAULT_IMAGE_PATH = ""

# ── Helpers ──────────────────────────────────────────────────────────────────

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"default_image": "", "keys": {}}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def load_pil_image(path, size=(220, 220)):
    if not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        img.thumbnail(size, Image.LANCZOS)
        return img
    except Exception:
        return None

# ── Home Screen ───────────────────────────────────────────────────────────────

class HomeScreen(tk.Frame):
    def __init__(self, master, on_start, on_settings):
        super().__init__(master, bg="#0f0f13")
        self.pack(fill="both", expand=True)

        tk.Label(
            self, text="🎮  Streamer Emote Overlay",
            font=("Segoe UI", 22, "bold"), fg="#e8e6ff", bg="#0f0f13"
        ).pack(pady=(60, 8))

        tk.Label(
            self, text="Press a key → show an emote. Simple.",
            font=("Segoe UI", 11), fg="#7a78a0", bg="#0f0f13"
        ).pack(pady=(0, 48))

        btn_frame = tk.Frame(self, bg="#0f0f13")
        btn_frame.pack()

        self._make_btn(btn_frame, "▶  Start", "#534AB7", "#e8e6ff", on_start).pack(
            side="left", padx=10, ipadx=18, ipady=10
        )
        self._make_btn(btn_frame, "⚙  Settings", "#1e1d2a", "#9993cc", on_settings,
                       border="#534AB7").pack(
            side="left", padx=10, ipadx=18, ipady=10
        )

    def _make_btn(self, parent, text, bg, fg, cmd, border=None):
        btn = tk.Button(
            parent, text=text, font=("Segoe UI", 12, "bold"),
            bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
            relief="flat", cursor="hand2", command=cmd,
            highlightthickness=2 if border else 0,
            highlightbackground=border or bg,
            highlightcolor=border or bg,
        )
        return btn

# ── Settings Screen ───────────────────────────────────────────────────────────

class SettingsScreen(tk.Frame):
    def __init__(self, master, config, on_back, on_save):
        super().__init__(master, bg="#0f0f13")
        self.pack(fill="both", expand=True)
        self.config = config
        self.on_save = on_save
        self.rows = []          # list of {key_var, path_var, preview_label}
        self._build(on_back)

    def _build(self, on_back):
        # ── Header
        header = tk.Frame(self, bg="#0f0f13")
        header.pack(fill="x", padx=24, pady=(20, 0))

        tk.Button(
            header, text="← Back", font=("Segoe UI", 10), fg="#9993cc",
            bg="#0f0f13", activebackground="#0f0f13", activeforeground="#e8e6ff",
            relief="flat", cursor="hand2", command=on_back
        ).pack(side="left")

        tk.Label(
            header, text="Settings", font=("Segoe UI", 16, "bold"),
            fg="#e8e6ff", bg="#0f0f13"
        ).pack(side="left", padx=16)

        tk.Button(
            header, text="Save", font=("Segoe UI", 10, "bold"),
            fg="#e8e6ff", bg="#534AB7", activebackground="#3C3489",
            activeforeground="#e8e6ff", relief="flat", cursor="hand2",
            padx=14, pady=4, command=self._save
        ).pack(side="right")

        sep = tk.Frame(self, bg="#1e1d2a", height=1)
        sep.pack(fill="x", pady=10)

        # ── Default image
        def_frame = tk.Frame(self, bg="#0f0f13")
        def_frame.pack(fill="x", padx=24, pady=(4, 8))

        tk.Label(
            def_frame, text="Default image  (shown when no key is held)",
            font=("Segoe UI", 10), fg="#7a78a0", bg="#0f0f13"
        ).pack(side="left")

        self.default_var = tk.StringVar(value=self.config.get("default_image", ""))
        self.default_preview = tk.Label(def_frame, bg="#0f0f13", fg="#534AB7",
                                        font=("Segoe UI", 9), cursor="hand2")
        self.default_preview.pack(side="right")
        self.default_preview.bind("<Button-1>", lambda e: self._pick_default())
        self._update_default_label()

        tk.Button(
            def_frame, text="Browse", font=("Segoe UI", 9),
            bg="#1e1d2a", fg="#9993cc", activebackground="#2a2940",
            activeforeground="#e8e6ff", relief="flat", cursor="hand2",
            command=self._pick_default
        ).pack(side="right", padx=8)

        sep2 = tk.Frame(self, bg="#1e1d2a", height=1)
        sep2.pack(fill="x", pady=(4, 0))

        # ── Key rows (scrollable)
        tk.Label(
            self, text="Key → Emote bindings",
            font=("Segoe UI", 11, "bold"), fg="#e8e6ff", bg="#0f0f13"
        ).pack(anchor="w", padx=24, pady=(10, 4))

        canvas = tk.Canvas(self, bg="#0f0f13", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="#0f0f13")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(24, 0))
        scrollbar.pack(side="right", fill="y")

        # Existing bindings
        for key, path in self.config.get("keys", {}).items():
            self._add_row(key, path)

        # ── Add row button
        add_frame = tk.Frame(self, bg="#0f0f13")
        add_frame.pack(fill="x", padx=24, pady=10)
        tk.Button(
            add_frame, text="+ Add key binding",
            font=("Segoe UI", 10), fg="#9993cc", bg="#1e1d2a",
            activebackground="#2a2940", activeforeground="#e8e6ff",
            relief="flat", cursor="hand2", padx=12, pady=5,
            command=lambda: self._add_row()
        ).pack(side="left")

    def _add_row(self, key="", path=""):
        row_frame = tk.Frame(self.scroll_frame, bg="#13121a",
                             highlightthickness=1, highlightbackground="#1e1d2a")
        row_frame.pack(fill="x", pady=4, padx=4)

        # Key capture
        key_var = tk.StringVar(value=key)
        key_lbl = tk.Label(row_frame, text="Key:", font=("Segoe UI", 10),
                           fg="#7a78a0", bg="#13121a")
        key_lbl.pack(side="left", padx=(10, 4), pady=8)

        key_entry = tk.Entry(row_frame, textvariable=key_var, width=10,
                             font=("Segoe UI Mono", 11, "bold"),
                             bg="#1e1d2a", fg="#e8e6ff",
                             insertbackground="#534AB7",
                             relief="flat", highlightthickness=1,
                             highlightbackground="#534AB7")
        key_entry.pack(side="left", padx=4, ipady=4)

        capture_btn = tk.Button(
            row_frame, text="Capture", font=("Segoe UI", 9),
            bg="#1e1d2a", fg="#9993cc", activebackground="#2a2940",
            activeforeground="#e8e6ff", relief="flat", cursor="hand2"
        )
        capture_btn.pack(side="left", padx=6)

        def start_capture():
            capture_btn.config(text="Press key…", bg="#2a2940", fg="#e8e6ff")
            key_entry.focus_set()
            def on_key(event):
                k = event.keysym
                key_var.set(k)
                capture_btn.config(text="Capture", bg="#1e1d2a", fg="#9993cc")
                key_entry.unbind("<KeyPress>")
            key_entry.bind("<KeyPress>", on_key)

        capture_btn.config(command=start_capture)

        # Separator
        tk.Frame(row_frame, bg="#1e1d2a", width=1).pack(
            side="left", fill="y", padx=6, pady=4)

        # Image picker
        path_var = tk.StringVar(value=path)

        preview_lbl = tk.Label(row_frame, bg="#13121a", width=8)
        preview_lbl.pack(side="left", padx=4)
        self._refresh_thumb(preview_lbl, path_var.get())

        def pick_image():
            p = filedialog.askopenfilename(
                title="Choose emote image",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp"), ("All", "*.*")]
            )
            if p:
                path_var.set(p)
                self._refresh_thumb(preview_lbl, p)

        tk.Button(
            row_frame, text="Pick image", font=("Segoe UI", 9),
            bg="#1e1d2a", fg="#9993cc", activebackground="#2a2940",
            activeforeground="#e8e6ff", relief="flat", cursor="hand2",
            command=pick_image
        ).pack(side="left", padx=4)

        path_name_lbl = tk.Label(row_frame, textvariable=path_var,
                                 font=("Segoe UI", 8), fg="#534AB7",
                                 bg="#13121a", width=22, anchor="w")
        path_name_lbl.pack(side="left", padx=4)

        # Delete button
        def delete_row():
            row_frame.destroy()
            self.rows = [r for r in self.rows
                         if r["key_var"] is not key_var]

        tk.Button(
            row_frame, text="✕", font=("Segoe UI", 10),
            bg="#13121a", fg="#7a78a0", activebackground="#13121a",
            activeforeground="#e24b4a", relief="flat", cursor="hand2",
            command=delete_row
        ).pack(side="right", padx=8)

        self.rows.append({
            "key_var": key_var,
            "path_var": path_var,
            "preview_label": preview_lbl,
        })

    def _refresh_thumb(self, label, path, size=(40, 40)):
        img = load_pil_image(path, size)
        if img:
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo, text="")
            label._photo = photo
        else:
            label.config(image="", text="No img", fg="#534AB7",
                         font=("Segoe UI", 8))

    def _pick_default(self):
        p = filedialog.askopenfilename(
            title="Choose default image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp"), ("All", "*.*")]
        )
        if p:
            self.default_var.set(p)
            self._update_default_label()

    def _update_default_label(self):
        p = self.default_var.get()
        name = os.path.basename(p) if p else "None set"
        self.default_preview.config(text=name)

    def _save(self):
        keys = {}
        for row in self.rows:
            k = row["key_var"].get().strip()
            p = row["path_var"].get().strip()
            if k:
                keys[k] = p
        self.config["default_image"] = self.default_var.get()
        self.config["keys"] = keys
        save_config(self.config)
        self.on_save(self.config)
        messagebox.showinfo("Saved", "Settings saved! ✓")

# ── Overlay Window ─────────────────────────────────────────────────────────────

class OverlayWindow(tk.Toplevel):
    """Transparent always-on-top overlay in the bottom-right corner."""

    SIZE = 240

    def __init__(self, master, config, on_stop):
        super().__init__(master)
        self.config = config
        self.on_stop = on_stop
        self._cache = {}        # path → ImageTk.PhotoImage
        self._active_key = None

        # Window chrome
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#010101")
        self.config_bg = "#010101"       # treated as transparent
        self.configure(bg=self.config_bg)

        # Position: bottom-right with margin
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        pad = 24
        self.geometry(
            f"{self.SIZE}x{self.SIZE+40}+"
            f"{sw - self.SIZE - pad}+{sh - self.SIZE - 60 - pad}"
        )

        # Image canvas
        self.canvas = tk.Canvas(
            self, width=self.SIZE, height=self.SIZE,
            bg=self.config_bg, highlightthickness=0
        )
        self.canvas.pack()

        # Stop button
        stop_btn = tk.Button(
            self, text="■  Stop", font=("Segoe UI", 9, "bold"),
            fg="#e8e6ff", bg="#3C3489", activebackground="#26215C",
            activeforeground="#e8e6ff", relief="flat", cursor="hand2",
            command=self._stop
        )
        stop_btn.pack(fill="x", ipady=5)

        # Pre-load images
        self._load_images()
        self._show_image(self.config.get("default_image", ""))

        # Key listeners on root so they fire even when overlay is focused
        master.bind("<KeyPress>", self._on_key_press, add=True)
        master.bind("<KeyRelease>", self._on_key_release, add=True)
        self.bind("<KeyPress>", self._on_key_press, add=True)
        self.bind("<KeyRelease>", self._on_key_release, add=True)

        # Make overlay draggable
        self.canvas.bind("<Button-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)

    def _drag_start(self, e):
        self._dx, self._dy = e.x, e.y

    def _drag_move(self, e):
        x = self.winfo_x() + e.x - self._dx
        y = self.winfo_y() + e.y - self._dy
        self.geometry(f"+{x}+{y}")

    def _load_images(self):
        paths = set()
        default = self.config.get("default_image", "")
        if default:
            paths.add(default)
        for p in self.config.get("keys", {}).values():
            if p:
                paths.add(p)
        for path in paths:
            self._cache_image(path)

    def _cache_image(self, path):
        if path in self._cache or not path:
            return
        img = load_pil_image(path, (self.SIZE, self.SIZE))
        if img:
            self._cache[path] = ImageTk.PhotoImage(img)

    def _show_image(self, path):
        self.canvas.delete("all")
        photo = self._cache.get(path)
        if photo:
            self.canvas.create_image(
                self.SIZE // 2, self.SIZE // 2,
                image=photo, anchor="center"
            )
        else:
            # Placeholder
            self.canvas.create_rectangle(
                10, 10, self.SIZE - 10, self.SIZE - 10,
                fill="#1e1d2a", outline="#534AB7", width=2
            )
            self.canvas.create_text(
                self.SIZE // 2, self.SIZE // 2,
                text="No image\nassigned",
                fill="#534AB7", font=("Segoe UI", 12), justify="center"
            )

    def _on_key_press(self, event):
        key = event.keysym
        keys_map = self.config.get("keys", {})
        if key in keys_map and key != self._active_key:
            self._active_key = key
            path = keys_map[key]
            if path and path not in self._cache:
                self._cache_image(path)
            self._show_image(path)

    def _on_key_release(self, event):
        if event.keysym == self._active_key:
            self._active_key = None
            self._show_image(self.config.get("default_image", ""))

    def _stop(self):
        self.master.unbind("<KeyPress>")
        self.master.unbind("<KeyRelease>")
        self.destroy()
        self.on_stop()

# ── App Controller ─────────────────────────────────────────────────────────────

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Streamer Emote Overlay")
        self.root.geometry("480x340")
        self.root.configure(bg="#0f0f13")
        self.root.resizable(False, False)

        try:
            self.root.iconbitmap("")
        except Exception:
            pass

        # Style scrollbar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar",
                         background="#1e1d2a", troughcolor="#0f0f13",
                         bordercolor="#0f0f13", arrowcolor="#534AB7")

        self.config = load_config()
        self.current_frame = None
        self.overlay = None

        self.show_home()
        self.root.mainloop()

    def _clear(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_home(self):
        self._clear()
        self.root.geometry("480x340")
        self.current_frame = HomeScreen(
            self.root,
            on_start=self.start_overlay,
            on_settings=self.show_settings
        )

    def show_settings(self):
        self._clear()
        self.root.geometry("560x520")
        self.current_frame = SettingsScreen(
            self.root,
            config=self.config,
            on_back=self.show_home,
            on_save=self._on_config_saved
        )

    def _on_config_saved(self, new_cfg):
        self.config = new_cfg

    def start_overlay(self):
        self._clear()
        # Show a minimal "running" indicator in main window
        self.root.geometry("480x180")
        indicator = tk.Frame(self.root, bg="#0f0f13")
        indicator.pack(fill="both", expand=True)

        tk.Label(
            indicator, text="● Overlay running",
            font=("Segoe UI", 14, "bold"), fg="#1D9E75", bg="#0f0f13"
        ).pack(pady=(40, 6))
        tk.Label(
            indicator,
            text="Hold a configured key to swap the emote.\n"
                 "Use the ■ Stop button on the overlay to return home.",
            font=("Segoe UI", 10), fg="#7a78a0", bg="#0f0f13", justify="center"
        ).pack()

        self.current_frame = indicator

        self.overlay = OverlayWindow(
            self.root, self.config, on_stop=self.show_home
        )
        # Bring overlay to front
        self.overlay.lift()

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageTk
    App()
