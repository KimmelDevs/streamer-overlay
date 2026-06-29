import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil

# ── Paths (all relative to the script's own folder) ──────────────────────────

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR  = os.path.join(SCRIPT_DIR, "images")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "keybindings.txt")

os.makedirs(IMAGES_DIR, exist_ok=True)

# ── Config: plain .txt notepad format ────────────────────────────────────────
#
#   Lines look like:
#       default = default.png
#       w = walk.png
#       space = jump.png
#
#   Image filenames are relative to the images/ folder.

def load_config():
    cfg = {"default_image": "", "keys": {}}
    if not os.path.exists(CONFIG_FILE):
        return cfg
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if key == "default":
                cfg["default_image"] = os.path.join(IMAGES_DIR, val) if val else ""
            else:
                cfg["keys"][key] = os.path.join(IMAGES_DIR, val) if val else ""
    return cfg

def save_config(cfg):
    lines = ["# Streamer Emote Overlay — key bindings",
             "# Format:  key = image_filename.png",
             "# Special: default = image shown when no key is held",
             "#",
             "# Images live in the 'images' folder next to this script.",
             "# You can edit this file in Notepad too — just save and restart.",
             ""]
    default_path = cfg.get("default_image", "")
    default_name = os.path.basename(default_path) if default_path else ""
    lines.append(f"default = {default_name}")
    lines.append("")
    for k, path in cfg.get("keys", {}).items():
        fname = os.path.basename(path) if path else ""
        lines.append(f"{k} = {fname}")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def import_image(src_path):
    """Copy an image into the images/ folder and return the destination path."""
    if not src_path:
        return ""
    fname = os.path.basename(src_path)
    dest = os.path.join(IMAGES_DIR, fname)
    if os.path.abspath(src_path) != os.path.abspath(dest):
        shutil.copy2(src_path, dest)
    return dest

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

        tk.Label(self, text="🎮  Streamer Emote Overlay",
                 font=("Segoe UI", 22, "bold"), fg="#e8e6ff", bg="#0f0f13"
                 ).pack(pady=(60, 8))

        tk.Label(self, text="Press a key → show an emote. Simple.",
                 font=("Segoe UI", 11), fg="#7a78a0", bg="#0f0f13"
                 ).pack(pady=(0, 6))

        # Show where the config file lives
        tk.Label(self, text=f"📄  {CONFIG_FILE}",
                 font=("Segoe UI", 8), fg="#3C3489", bg="#0f0f13"
                 ).pack(pady=(0, 36))

        btn_frame = tk.Frame(self, bg="#0f0f13")
        btn_frame.pack()

        self._btn(btn_frame, "▶  Start", "#534AB7", "#e8e6ff", on_start).pack(
            side="left", padx=10, ipadx=18, ipady=10)
        self._btn(btn_frame, "⚙  Settings", "#1e1d2a", "#9993cc", on_settings,
                  border="#534AB7").pack(side="left", padx=10, ipadx=18, ipady=10)

    def _btn(self, parent, text, bg, fg, cmd, border=None):
        return tk.Button(parent, text=text, font=("Segoe UI", 12, "bold"),
                         bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                         relief="flat", cursor="hand2", command=cmd,
                         highlightthickness=2 if border else 0,
                         highlightbackground=border or bg,
                         highlightcolor=border or bg)

# ── Settings Screen ───────────────────────────────────────────────────────────

class SettingsScreen(tk.Frame):
    def __init__(self, master, config, on_back, on_save):
        super().__init__(master, bg="#0f0f13")
        self.pack(fill="both", expand=True)
        self.config = config
        self.on_save = on_save
        self.rows = []
        self._build(on_back)

    def _build(self, on_back):
        # Header
        header = tk.Frame(self, bg="#0f0f13")
        header.pack(fill="x", padx=24, pady=(20, 0))

        tk.Button(header, text="← Back", font=("Segoe UI", 10), fg="#9993cc",
                  bg="#0f0f13", activebackground="#0f0f13", activeforeground="#e8e6ff",
                  relief="flat", cursor="hand2", command=on_back).pack(side="left")

        tk.Label(header, text="Settings", font=("Segoe UI", 16, "bold"),
                 fg="#e8e6ff", bg="#0f0f13").pack(side="left", padx=16)

        tk.Button(header, text="Save", font=("Segoe UI", 10, "bold"),
                  fg="#e8e6ff", bg="#534AB7", activebackground="#3C3489",
                  activeforeground="#e8e6ff", relief="flat", cursor="hand2",
                  padx=14, pady=4, command=self._save).pack(side="right")

        # Open notepad button
        tk.Button(header, text="📄 Open keybindings.txt", font=("Segoe UI", 9),
                  fg="#7a78a0", bg="#0f0f13", activebackground="#0f0f13",
                  activeforeground="#9993cc", relief="flat", cursor="hand2",
                  command=self._open_notepad).pack(side="right", padx=8)

        tk.Frame(self, bg="#1e1d2a", height=1).pack(fill="x", pady=10)

        # Images folder info
        info = tk.Frame(self, bg="#13121a", highlightthickness=1,
                        highlightbackground="#1e1d2a")
        info.pack(fill="x", padx=24, pady=(0, 8))
        tk.Label(info, text="📁  Images folder:", font=("Segoe UI", 9),
                 fg="#7a78a0", bg="#13121a").pack(side="left", padx=10, pady=6)
        tk.Label(info, text=IMAGES_DIR, font=("Segoe UI", 8),
                 fg="#534AB7", bg="#13121a").pack(side="left")
        tk.Button(info, text="Open folder", font=("Segoe UI", 8),
                  fg="#9993cc", bg="#1e1d2a", activebackground="#2a2940",
                  activeforeground="#e8e6ff", relief="flat", cursor="hand2",
                  command=lambda: os.startfile(IMAGES_DIR)).pack(side="right", padx=8)

        # Default image
        def_frame = tk.Frame(self, bg="#0f0f13")
        def_frame.pack(fill="x", padx=24, pady=(4, 8))

        tk.Label(def_frame, text="Default image  (shown when no key is held)",
                 font=("Segoe UI", 10), fg="#7a78a0", bg="#0f0f13").pack(side="left")

        self.default_var = tk.StringVar(value=self.config.get("default_image", ""))
        self.default_preview = tk.Label(def_frame, bg="#0f0f13", fg="#534AB7",
                                        font=("Segoe UI", 9), cursor="hand2")
        self.default_preview.pack(side="right")
        self.default_preview.bind("<Button-1>", lambda e: self._pick_default())
        self._update_default_label()

        tk.Button(def_frame, text="Browse", font=("Segoe UI", 9),
                  bg="#1e1d2a", fg="#9993cc", activebackground="#2a2940",
                  activeforeground="#e8e6ff", relief="flat", cursor="hand2",
                  command=self._pick_default).pack(side="right", padx=8)

        tk.Frame(self, bg="#1e1d2a", height=1).pack(fill="x", pady=(4, 0))

        # Key rows
        tk.Label(self, text="Key → Emote bindings",
                 font=("Segoe UI", 11, "bold"), fg="#e8e6ff", bg="#0f0f13"
                 ).pack(anchor="w", padx=24, pady=(10, 4))

        canvas = tk.Canvas(self, bg="#0f0f13", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="#0f0f13")
        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(24, 0))
        scrollbar.pack(side="right", fill="y")

        for key, path in self.config.get("keys", {}).items():
            self._add_row(key, path)

        # Add row button
        add_frame = tk.Frame(self, bg="#0f0f13")
        add_frame.pack(fill="x", padx=24, pady=10)
        tk.Button(add_frame, text="+ Add key binding",
                  font=("Segoe UI", 10), fg="#9993cc", bg="#1e1d2a",
                  activebackground="#2a2940", activeforeground="#e8e6ff",
                  relief="flat", cursor="hand2", padx=12, pady=5,
                  command=lambda: self._add_row()).pack(side="left")

    def _add_row(self, key="", path=""):
        row_frame = tk.Frame(self.scroll_frame, bg="#13121a",
                             highlightthickness=1, highlightbackground="#1e1d2a")
        row_frame.pack(fill="x", pady=4, padx=4)

        key_var = tk.StringVar(value=key)
        tk.Label(row_frame, text="Key:", font=("Segoe UI", 10),
                 fg="#7a78a0", bg="#13121a").pack(side="left", padx=(10, 4), pady=8)

        key_entry = tk.Entry(row_frame, textvariable=key_var, width=10,
                             font=("Segoe UI Mono", 11, "bold"),
                             bg="#1e1d2a", fg="#e8e6ff",
                             insertbackground="#534AB7", relief="flat",
                             highlightthickness=1, highlightbackground="#534AB7")
        key_entry.pack(side="left", padx=4, ipady=4)

        capture_btn = tk.Button(row_frame, text="Capture", font=("Segoe UI", 9),
                                bg="#1e1d2a", fg="#9993cc", activebackground="#2a2940",
                                activeforeground="#e8e6ff", relief="flat", cursor="hand2")
        capture_btn.pack(side="left", padx=6)

        def start_capture():
            capture_btn.config(text="Press key…", bg="#2a2940", fg="#e8e6ff")
            key_entry.focus_set()
            def on_key(event):
                key_var.set(event.keysym)
                capture_btn.config(text="Capture", bg="#1e1d2a", fg="#9993cc")
                key_entry.unbind("<KeyPress>")
            key_entry.bind("<KeyPress>", on_key)

        capture_btn.config(command=start_capture)

        tk.Frame(row_frame, bg="#1e1d2a", width=1).pack(side="left", fill="y", padx=6, pady=4)

        path_var = tk.StringVar(value=path)
        preview_lbl = tk.Label(row_frame, bg="#13121a", width=8)
        preview_lbl.pack(side="left", padx=4)
        self._refresh_thumb(preview_lbl, path_var.get())

        def pick_image():
            p = filedialog.askopenfilename(
                title="Choose emote image",
                initialdir=IMAGES_DIR,
                filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp"), ("All", "*.*")])
            if p:
                dest = import_image(p)   # copy into images/ folder
                path_var.set(dest)
                self._refresh_thumb(preview_lbl, dest)
                fname_lbl.config(text=os.path.basename(dest))

        tk.Button(row_frame, text="Pick image", font=("Segoe UI", 9),
                  bg="#1e1d2a", fg="#9993cc", activebackground="#2a2940",
                  activeforeground="#e8e6ff", relief="flat", cursor="hand2",
                  command=pick_image).pack(side="left", padx=4)

        fname_lbl = tk.Label(row_frame,
                             text=os.path.basename(path_var.get()) if path_var.get() else "no image",
                             font=("Segoe UI", 8), fg="#534AB7",
                             bg="#13121a", width=20, anchor="w")
        fname_lbl.pack(side="left", padx=4)

        def delete_row():
            row_frame.destroy()
            self.rows = [r for r in self.rows if r["key_var"] is not key_var]

        tk.Button(row_frame, text="✕", font=("Segoe UI", 10),
                  bg="#13121a", fg="#7a78a0", activebackground="#13121a",
                  activeforeground="#e24b4a", relief="flat", cursor="hand2",
                  command=delete_row).pack(side="right", padx=8)

        self.rows.append({"key_var": key_var, "path_var": path_var,
                          "preview_label": preview_lbl})

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
            title="Choose default image", initialdir=IMAGES_DIR,
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp"), ("All", "*.*")])
        if p:
            dest = import_image(p)
            self.default_var.set(dest)
            self._update_default_label()

    def _update_default_label(self):
        p = self.default_var.get()
        self.default_preview.config(text=os.path.basename(p) if p else "None set")

    def _open_notepad(self):
        if not os.path.exists(CONFIG_FILE):
            save_config({"default_image": "", "keys": {}})
        os.startfile(CONFIG_FILE)

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
        messagebox.showinfo("Saved", "Settings saved!\n\nkeybindings.txt updated ✓")

# ── Overlay Window ─────────────────────────────────────────────────────────────

class OverlayWindow(tk.Toplevel):
    SIZE = 240

    def __init__(self, master, config, on_stop):
        super().__init__(master)
        self.config = config
        self.on_stop = on_stop
        self._cache = {}
        self._active_key = None

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#010101")
        self.configure(bg="#010101")

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        pad = 24
        self.geometry(f"{self.SIZE}x{self.SIZE+40}+"
                      f"{sw-self.SIZE-pad}+{sh-self.SIZE-60-pad}")

        self.canvas = tk.Canvas(self, width=self.SIZE, height=self.SIZE,
                                bg="#010101", highlightthickness=0)
        self.canvas.pack()

        tk.Button(self, text="■  Stop", font=("Segoe UI", 9, "bold"),
                  fg="#e8e6ff", bg="#3C3489", activebackground="#26215C",
                  activeforeground="#e8e6ff", relief="flat", cursor="hand2",
                  command=self._stop).pack(fill="x", ipady=5)

        self._load_images()
        self._show_image(self.config.get("default_image", ""))

        master.bind("<KeyPress>", self._on_key_press, add=True)
        master.bind("<KeyRelease>", self._on_key_release, add=True)
        self.bind("<KeyPress>", self._on_key_press, add=True)
        self.bind("<KeyRelease>", self._on_key_release, add=True)

        self.canvas.bind("<Button-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)

    def _drag_start(self, e): self._dx, self._dy = e.x, e.y
    def _drag_move(self, e):
        self.geometry(f"+{self.winfo_x()+e.x-self._dx}+{self.winfo_y()+e.y-self._dy}")

    def _load_images(self):
        paths = {self.config.get("default_image", "")}
        paths.update(self.config.get("keys", {}).values())
        for p in paths:
            if p:
                self._cache_image(p)

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
            self.canvas.create_image(self.SIZE//2, self.SIZE//2, image=photo, anchor="center")
        else:
            self.canvas.create_rectangle(10, 10, self.SIZE-10, self.SIZE-10,
                                         fill="#1e1d2a", outline="#534AB7", width=2)
            self.canvas.create_text(self.SIZE//2, self.SIZE//2,
                                    text="No image\nassigned",
                                    fill="#534AB7", font=("Segoe UI", 12), justify="center")

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

# ── App ───────────────────────────────────────────────────────────────────────

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Streamer Emote Overlay")
        self.root.geometry("480x340")
        self.root.configure(bg="#0f0f13")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar",
                        background="#1e1d2a", troughcolor="#0f0f13",
                        bordercolor="#0f0f13", arrowcolor="#534AB7")

        self.config = load_config()
        self.current_frame = None
        self.show_home()
        self.root.mainloop()

    def _clear(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_home(self):
        self._clear()
        self.root.geometry("480x340")
        self.current_frame = HomeScreen(self.root, self.start_overlay, self.show_settings)

    def show_settings(self):
        self._clear()
        self.root.geometry("600x540")
        self.current_frame = SettingsScreen(self.root, self.config,
                                            on_back=self.show_home,
                                            on_save=lambda c: setattr(self, "config", c))

    def start_overlay(self):
        self._clear()
        self.root.geometry("480x180")
        frame = tk.Frame(self.root, bg="#0f0f13")
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="● Overlay running",
                 font=("Segoe UI", 14, "bold"), fg="#1D9E75", bg="#0f0f13"
                 ).pack(pady=(40, 6))
        tk.Label(frame,
                 text="Hold a configured key to swap the emote.\n"
                      "Use the ■ Stop button on the overlay to return home.",
                 font=("Segoe UI", 10), fg="#7a78a0", bg="#0f0f13", justify="center"
                 ).pack()
        self.current_frame = frame
        OverlayWindow(self.root, self.config, on_stop=self.show_home).lift()

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageTk
    App()
