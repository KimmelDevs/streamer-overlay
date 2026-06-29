import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil

# ── Paths ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR  = os.path.join(SCRIPT_DIR, "images")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "keybindings.txt")

os.makedirs(IMAGES_DIR, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
#
#   keybindings.txt format:
#       default   = default.png
#       w         = walk.png
#       placement = 1420,800   (pixel x,y saved position)
#       locked    = 0          (1 = drag locked)
#       size      = 240        (overlay size in px)

def load_config():
    cfg = {"default_image": "", "keys": {},
           "placement": None, "locked": False, "size": 240}
    if not os.path.exists(CONFIG_FILE):
        return cfg
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if key == "default":
                cfg["default_image"] = os.path.join(IMAGES_DIR, val) if val else ""
            elif key == "placement":
                try:
                    x, y = val.split(",")
                    cfg["placement"] = (int(x), int(y))
                except Exception:
                    pass
            elif key == "locked":
                cfg["locked"] = val == "1"
            elif key == "size":
                try:
                    cfg["size"] = max(80, min(480, int(val)))
                except Exception:
                    pass
            else:
                cfg["keys"][key] = os.path.join(IMAGES_DIR, val) if val else ""
    return cfg

def save_config(cfg):
    lines = [
        "# Streamer Emote Overlay — config",
        "# Format:  key = image_filename.png",
        "# Special keys: default, placement, locked, size",
        "#",
        "# Images live in the 'images' folder next to this script.",
        "# You can edit this file in Notepad — save and restart to apply.",
        "",
    ]
    default_name = os.path.basename(cfg.get("default_image", ""))
    lines.append(f"default = {default_name}")
    placement = cfg.get("placement")
    if placement:
        lines.append(f"placement = {placement[0]},{placement[1]}")
    lines.append(f"locked = {'1' if cfg.get('locked') else '0'}")
    lines.append(f"size = {cfg.get('size', 240)}")
    lines.append("")
    for k, path in cfg.get("keys", {}).items():
        fname = os.path.basename(path) if path else ""
        lines.append(f"{k} = {fname}")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def import_image(src_path):
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

TAB_BG    = "#0f0f13"
TAB_ACT   = "#1e1d2a"
ROW_BG    = "#13121a"
ACCENT    = "#534AB7"
ACCENT2   = "#9993cc"
FG        = "#e8e6ff"
FG_MUTED  = "#7a78a0"
FG_DIM    = "#3C3489"

class SettingsScreen(tk.Frame):
    def __init__(self, master, config, on_back, on_save):
        super().__init__(master, bg=TAB_BG)
        self.pack(fill="both", expand=True)
        self.config = config
        self.on_save = on_save
        self.rows = []
        self._active_tab = tk.StringVar(value="keys")
        self._build(on_back)

    # ── Shell ──────────────────────────────────────────────────────────────────

    def _build(self, on_back):
        # Header
        header = tk.Frame(self, bg=TAB_BG)
        header.pack(fill="x", padx=24, pady=(20, 0))

        tk.Button(header, text="← Back", font=("Segoe UI", 10), fg=ACCENT2,
                  bg=TAB_BG, activebackground=TAB_BG, activeforeground=FG,
                  relief="flat", cursor="hand2", command=on_back).pack(side="left")
        tk.Label(header, text="Settings", font=("Segoe UI", 16, "bold"),
                 fg=FG, bg=TAB_BG).pack(side="left", padx=16)
        tk.Button(header, text="Save", font=("Segoe UI", 10, "bold"),
                  fg=FG, bg=ACCENT, activebackground="#3C3489",
                  activeforeground=FG, relief="flat", cursor="hand2",
                  padx=14, pady=4, command=self._save).pack(side="right")
        tk.Button(header, text="📄 Open keybindings.txt", font=("Segoe UI", 9),
                  fg=FG_MUTED, bg=TAB_BG, activebackground=TAB_BG,
                  activeforeground=ACCENT2, relief="flat", cursor="hand2",
                  command=self._open_notepad).pack(side="right", padx=8)

        tk.Frame(self, bg="#1e1d2a", height=1).pack(fill="x", pady=(10, 0))

        # Tab bar
        tab_bar = tk.Frame(self, bg=TAB_BG)
        tab_bar.pack(fill="x", padx=24, pady=(0, 0))

        self._tab_btns = {}
        for tab_id, label in [("keys", "🎹  Key bindings"), ("placement", "📐  Placement")]:
            btn = tk.Button(tab_bar, text=label, font=("Segoe UI", 10),
                            fg=FG, bg=TAB_BG, activebackground=TAB_ACT,
                            activeforeground=FG, relief="flat", cursor="hand2",
                            padx=14, pady=8,
                            command=lambda t=tab_id: self._switch_tab(t))
            btn.pack(side="left")
            self._tab_btns[tab_id] = btn

        self._tab_indicator = tk.Frame(self, bg=ACCENT, height=2)
        self._tab_indicator.pack(fill="x", padx=24)

        # Content area
        self._content = tk.Frame(self, bg=TAB_BG)
        self._content.pack(fill="both", expand=True)

        # Build both tab panels
        self._panel_keys = self._build_keys_tab()
        self._panel_placement = self._build_placement_tab()

        self._switch_tab("keys")

    def _switch_tab(self, tab_id):
        self._active_tab.set(tab_id)
        self._panel_keys.pack_forget()
        self._panel_placement.pack_forget()
        if tab_id == "keys":
            self._panel_keys.pack(fill="both", expand=True)
        else:
            self._panel_placement.pack(fill="both", expand=True)
        for tid, btn in self._tab_btns.items():
            btn.config(bg=TAB_ACT if tid == tab_id else TAB_BG,
                       fg=FG if tid == tab_id else FG_MUTED)

    # ── Keys tab ───────────────────────────────────────────────────────────────

    def _build_keys_tab(self):
        panel = tk.Frame(self._content, bg=TAB_BG)

        # Images folder info bar
        info = tk.Frame(panel, bg=ROW_BG, highlightthickness=1,
                        highlightbackground="#1e1d2a")
        info.pack(fill="x", padx=24, pady=(12, 6))
        tk.Label(info, text="📁  Images folder:", font=("Segoe UI", 9),
                 fg=FG_MUTED, bg=ROW_BG).pack(side="left", padx=10, pady=6)
        tk.Label(info, text=IMAGES_DIR, font=("Segoe UI", 8),
                 fg=FG_DIM, bg=ROW_BG).pack(side="left")
        tk.Button(info, text="Open folder", font=("Segoe UI", 8),
                  fg=ACCENT2, bg="#1e1d2a", activebackground="#2a2940",
                  activeforeground=FG, relief="flat", cursor="hand2",
                  command=lambda: os.startfile(IMAGES_DIR)).pack(side="right", padx=8)

        # Default image row
        def_frame = tk.Frame(panel, bg=TAB_BG)
        def_frame.pack(fill="x", padx=24, pady=(4, 8))
        tk.Label(def_frame, text="Default image  (shown at startup)",
                 font=("Segoe UI", 10), fg=FG_MUTED, bg=TAB_BG).pack(side="left")
        self.default_var = tk.StringVar(value=self.config.get("default_image", ""))
        self.default_preview = tk.Label(def_frame, bg=TAB_BG, fg=FG_DIM,
                                        font=("Segoe UI", 9), cursor="hand2")
        self.default_preview.pack(side="right")
        self.default_preview.bind("<Button-1>", lambda e: self._pick_default())
        self._update_default_label()
        tk.Button(def_frame, text="Browse", font=("Segoe UI", 9),
                  bg="#1e1d2a", fg=ACCENT2, activebackground="#2a2940",
                  activeforeground=FG, relief="flat", cursor="hand2",
                  command=self._pick_default).pack(side="right", padx=8)

        tk.Frame(panel, bg="#1e1d2a", height=1).pack(fill="x", padx=24, pady=(4, 0))
        tk.Label(panel, text="Key → Emote bindings",
                 font=("Segoe UI", 11, "bold"), fg=FG, bg=TAB_BG
                 ).pack(anchor="w", padx=24, pady=(10, 4))

        # Scrollable rows
        canvas = tk.Canvas(panel, bg=TAB_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=TAB_BG)
        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(24, 0))
        scrollbar.pack(side="right", fill="y")

        for key, path in self.config.get("keys", {}).items():
            self._add_row(key, path)

        add_frame = tk.Frame(panel, bg=TAB_BG)
        add_frame.pack(fill="x", padx=24, pady=10)
        tk.Button(add_frame, text="+ Add key binding",
                  font=("Segoe UI", 10), fg=ACCENT2, bg="#1e1d2a",
                  activebackground="#2a2940", activeforeground=FG,
                  relief="flat", cursor="hand2", padx=12, pady=5,
                  command=lambda: self._add_row()).pack(side="left")

        return panel

    def _add_row(self, key="", path=""):
        row_frame = tk.Frame(self.scroll_frame, bg=ROW_BG,
                             highlightthickness=1, highlightbackground="#1e1d2a")
        row_frame.pack(fill="x", pady=4, padx=4)

        key_var = tk.StringVar(value=key)
        tk.Label(row_frame, text="Key:", font=("Segoe UI", 10),
                 fg=FG_MUTED, bg=ROW_BG).pack(side="left", padx=(10, 4), pady=8)

        key_entry = tk.Entry(row_frame, textvariable=key_var, width=10,
                             font=("Segoe UI Mono", 11, "bold"),
                             bg="#1e1d2a", fg=FG, insertbackground=ACCENT,
                             relief="flat", highlightthickness=1,
                             highlightbackground=ACCENT)
        key_entry.pack(side="left", padx=4, ipady=4)

        capture_btn = tk.Button(row_frame, text="Capture", font=("Segoe UI", 9),
                                bg="#1e1d2a", fg=ACCENT2, activebackground="#2a2940",
                                activeforeground=FG, relief="flat", cursor="hand2")
        capture_btn.pack(side="left", padx=6)

        def start_capture():
            capture_btn.config(text="Press key…", bg="#2a2940", fg=FG)
            key_entry.focus_set()
            def on_key(event):
                key_var.set(event.keysym)
                capture_btn.config(text="Capture", bg="#1e1d2a", fg=ACCENT2)
                key_entry.unbind("<KeyPress>")
            key_entry.bind("<KeyPress>", on_key)
        capture_btn.config(command=start_capture)

        tk.Frame(row_frame, bg="#1e1d2a", width=1).pack(side="left", fill="y", padx=6, pady=4)

        path_var = tk.StringVar(value=path)
        preview_lbl = tk.Label(row_frame, bg=ROW_BG, width=8)
        preview_lbl.pack(side="left", padx=4)
        self._refresh_thumb(preview_lbl, path_var.get())

        fname_lbl = tk.Label(row_frame,
                             text=os.path.basename(path_var.get()) if path_var.get() else "no image",
                             font=("Segoe UI", 8), fg=FG_DIM, bg=ROW_BG, width=20, anchor="w")
        fname_lbl.pack(side="left", padx=4)

        def pick_image():
            p = filedialog.askopenfilename(
                title="Choose emote image", initialdir=IMAGES_DIR,
                filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp"), ("All", "*.*")])
            if p:
                dest = import_image(p)
                path_var.set(dest)
                self._refresh_thumb(preview_lbl, dest)
                fname_lbl.config(text=os.path.basename(dest))

        tk.Button(row_frame, text="Pick image", font=("Segoe UI", 9),
                  bg="#1e1d2a", fg=ACCENT2, activebackground="#2a2940",
                  activeforeground=FG, relief="flat", cursor="hand2",
                  command=pick_image).pack(side="left", padx=4)

        def delete_row():
            row_frame.destroy()
            self.rows = [r for r in self.rows if r["key_var"] is not key_var]

        tk.Button(row_frame, text="✕", font=("Segoe UI", 10),
                  bg=ROW_BG, fg=FG_MUTED, activebackground=ROW_BG,
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
            label.config(image="", text="No img", fg=FG_DIM, font=("Segoe UI", 8))

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

    # ── Placement tab ──────────────────────────────────────────────────────────

    def _build_placement_tab(self):
        panel = tk.Frame(self._content, bg=TAB_BG)

        # ── Size slider
        sec_label(panel, "Overlay size")
        size_row = tk.Frame(panel, bg=TAB_BG)
        size_row.pack(fill="x", padx=24, pady=(0, 16))

        self.size_var = tk.IntVar(value=self.config.get("size", 240))
        size_val_lbl = tk.Label(size_row, textvariable=self.size_var,
                                font=("Segoe UI Mono", 12, "bold"),
                                fg=FG, bg=TAB_BG, width=4)
        size_val_lbl.pack(side="right")
        tk.Label(size_row, text="px", font=("Segoe UI", 9),
                 fg=FG_MUTED, bg=TAB_BG).pack(side="right", padx=(0, 4))
        tk.Scale(size_row, from_=80, to=480, orient="horizontal",
                 variable=self.size_var, showvalue=False,
                 bg=TAB_BG, fg=FG, troughcolor="#1e1d2a",
                 highlightthickness=0, activebackground=ACCENT,
                 bd=0, sliderrelief="flat").pack(side="left", fill="x", expand=True)

        tk.Frame(panel, bg="#1e1d2a", height=1).pack(fill="x", padx=24, pady=(0, 16))

        # ── Lock toggle
        sec_label(panel, "Drag lock")
        lock_row = tk.Frame(panel, bg=TAB_BG)
        lock_row.pack(fill="x", padx=24, pady=(0, 4))

        self.locked_var = tk.BooleanVar(value=self.config.get("locked", False))
        lock_btn = tk.Button(lock_row, font=("Segoe UI", 10), relief="flat",
                             cursor="hand2", padx=12, pady=5,
                             command=lambda: self._toggle_lock(lock_btn))
        lock_row.pack(fill="x", padx=24, pady=(0, 8))
        self._refresh_lock_btn(lock_btn)
        lock_btn.pack(side="left")

        tk.Label(lock_row, text="Lock prevents accidental dragging on stream.",
                 font=("Segoe UI", 9), fg=FG_MUTED, bg=TAB_BG).pack(side="left", padx=12)

        tk.Frame(panel, bg="#1e1d2a", height=1).pack(fill="x", padx=24, pady=(8, 16))

        # ── Saved position
        sec_label(panel, "Saved position")

        placement = self.config.get("placement")
        pos_text = f"X: {placement[0]}   Y: {placement[1]}" if placement else "Not saved yet"

        pos_row = tk.Frame(panel, bg=ROW_BG, highlightthickness=1,
                           highlightbackground="#1e1d2a")
        pos_row.pack(fill="x", padx=24, pady=(0, 10))
        self.pos_lbl = tk.Label(pos_row, text=pos_text,
                                font=("Segoe UI Mono", 11), fg=FG, bg=ROW_BG)
        self.pos_lbl.pack(side="left", padx=14, pady=10)
        tk.Button(pos_row, text="Clear saved position", font=("Segoe UI", 9),
                  fg=FG_MUTED, bg="#1e1d2a", activebackground="#2a2940",
                  activeforeground="#e24b4a", relief="flat", cursor="hand2",
                  command=self._clear_position).pack(side="right", padx=8)

        tk.Label(panel,
                 text="The overlay saves its position automatically when you stop it.\n"
                      "On next launch it will appear in the same spot.",
                 font=("Segoe UI", 9), fg=FG_MUTED, bg=TAB_BG, justify="left"
                 ).pack(anchor="w", padx=24, pady=(0, 16))

        tk.Frame(panel, bg="#1e1d2a", height=1).pack(fill="x", padx=24, pady=(0, 16))

        # ── Corner suggestions
        sec_label(panel, "Quick position presets")
        tk.Label(panel,
                 text="Click a preset to save that corner as your position.",
                 font=("Segoe UI", 9), fg=FG_MUTED, bg=TAB_BG
                 ).pack(anchor="w", padx=24, pady=(0, 10))

        grid = tk.Frame(panel, bg=TAB_BG)
        grid.pack(padx=24, anchor="w")

        sw = panel.winfo_screenwidth() or 1920
        sh = panel.winfo_screenheight() or 1080

        presets = [
            ("↖  Top-left",     0,       0,       "nw"),
            ("↗  Top-right",    None,    0,       "ne"),
            ("↙  Bottom-left",  0,       None,    "sw"),
            ("↘  Bottom-right", None,    None,    "se"),
        ]

        for i, (label, px, py, corner) in enumerate(presets):
            def make_cmd(lx, ly, c):
                def cmd():
                    size = self.size_var.get()
                    rx = (sw - size) if lx is None else lx
                    ry = (sh - size) if ly is None else ly
                    self.config["placement"] = (rx, ry)
                    self.pos_lbl.config(text=f"X: {rx}   Y: {ry}")
                return cmd
            tk.Button(grid, text=label, font=("Segoe UI", 10),
                      fg=FG, bg="#1e1d2a", activebackground="#2a2940",
                      activeforeground=FG, relief="flat", cursor="hand2",
                      padx=14, pady=7, command=make_cmd(px, py, corner)
                      ).grid(row=i//2, column=i%2, padx=6, pady=4, sticky="w")

        return panel

    def _toggle_lock(self, btn):
        self.locked_var.set(not self.locked_var.get())
        self._refresh_lock_btn(btn)

    def _refresh_lock_btn(self, btn):
        if self.locked_var.get():
            btn.config(text="🔒  Locked", bg="#2a1a1a", fg="#e24b4a",
                       activebackground="#2a1a1a", activeforeground="#e24b4a")
        else:
            btn.config(text="🔓  Unlocked", bg="#1e1d2a", fg=ACCENT2,
                       activebackground="#2a2940", activeforeground=FG)

    def _clear_position(self):
        self.config["placement"] = None
        self.pos_lbl.config(text="Not saved yet")

    # ── Save ───────────────────────────────────────────────────────────────────

    def _save(self):
        keys = {}
        for row in self.rows:
            k = row["key_var"].get().strip()
            p = row["path_var"].get().strip()
            if k:
                keys[k] = p
        self.config["default_image"] = self.default_var.get()
        self.config["keys"] = keys
        self.config["locked"] = self.locked_var.get()
        self.config["size"] = self.size_var.get()
        save_config(self.config)
        self.on_save(self.config)
        messagebox.showinfo("Saved", "Settings saved!\n\nkeybindings.txt updated ✓")

# ── Helpers ───────────────────────────────────────────────────────────────────

def sec_label(parent, text):
    tk.Label(parent, text=text.upper(),
             font=("Segoe UI", 8, "bold"), fg=FG_DIM, bg=TAB_BG
             ).pack(anchor="w", padx=24, pady=(0, 6))

# ── Overlay Window ─────────────────────────────────────────────────────────────

class OverlayWindow(tk.Toplevel):
    def __init__(self, master, config, on_stop):
        super().__init__(master)
        self.config = config
        self.on_stop = on_stop
        self._cache = {}
        self._active_key = None
        self._locked = config.get("locked", False)
        self.SIZE = config.get("size", 240)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#010101")
        self.configure(bg="#010101")

        # Position: use saved or default bottom-right
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        placement = config.get("placement")
        if placement:
            ox, oy = placement
        else:
            ox, oy = sw - self.SIZE, sh - self.SIZE
        self.geometry(f"{self.SIZE}x{self.SIZE}+{ox}+{oy}")

        self.canvas = tk.Canvas(self, width=self.SIZE, height=self.SIZE,
                                bg="#010101", highlightthickness=0)
        self.canvas.pack(padx=0, pady=0)

        self._load_images()
        self._show_image(self.config.get("default_image", ""))

        master.bind("<KeyPress>", self._on_key_press, add=True)
        self.bind("<KeyPress>", self._on_key_press, add=True)

        if not self._locked:
            self.canvas.bind("<Button-1>", self._drag_start)
            self.canvas.bind("<B1-Motion>", self._drag_move)

    def _drag_start(self, e):
        self._dx, self._dy = e.x, e.y

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
            self.canvas.create_image(self.SIZE//2, self.SIZE//2,
                                     image=photo, anchor="center")
        else:
            self.canvas.create_rectangle(10, 10, self.SIZE-10, self.SIZE-10,
                                         fill="#1e1d2a", outline=ACCENT, width=2)
            self.canvas.create_text(self.SIZE//2, self.SIZE//2,
                                    text="No image\nassigned",
                                    fill=ACCENT, font=("Segoe UI", 12), justify="center")

    def _on_key_press(self, event):
        key = event.keysym
        keys_map = self.config.get("keys", {})
        if key in keys_map and key != self._active_key:
            self._active_key = key
            path = keys_map[key]
            if path and path not in self._cache:
                self._cache_image(path)
            self._show_image(path)

    def _stop(self):
        # Save current position back to config
        self.config["placement"] = (self.winfo_x(), self.winfo_y())
        save_config(self.config)
        self.master.unbind("<KeyPress>")
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
                        bordercolor="#0f0f13", arrowcolor=ACCENT)

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
        self.current_frame = HomeScreen(self.root, self.start_overlay, self.show_settings)

    def show_settings(self):
        self._clear()
        self.root.geometry("620x580")
        self.current_frame = SettingsScreen(self.root, self.config,
                                            on_back=self.show_home,
                                            on_save=lambda c: setattr(self, "config", c))

    def start_overlay(self):
        self._clear()
        self.root.geometry("480x220")
        frame = tk.Frame(self.root, bg="#0f0f13")
        frame.pack(fill="both", expand=True)

        lock_note = "  🔒 Drag locked" if self.config.get("locked") else "  drag to reposition"
        tk.Label(frame, text="● Overlay running",
                 font=("Segoe UI", 14, "bold"), fg="#1D9E75", bg="#0f0f13"
                 ).pack(pady=(36, 4))
        tk.Label(frame, text=f"Press a key to swap emote  ·{lock_note}",
                 font=("Segoe UI", 10), fg=FG_MUTED, bg="#0f0f13").pack()

        def stop_overlay():
            if self.overlay:
                self.overlay._stop()

        tk.Button(frame, text="■  Stop overlay", font=("Segoe UI", 10, "bold"),
                  fg=FG, bg="#3C3489", activebackground="#26215C",
                  activeforeground=FG, relief="flat", cursor="hand2",
                  padx=16, pady=6, command=stop_overlay).pack(pady=(20, 0))

        self.current_frame = frame
        self.overlay = OverlayWindow(self.root, self.config, on_stop=self.show_home)
        self.overlay.lift()

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageTk
    App()
