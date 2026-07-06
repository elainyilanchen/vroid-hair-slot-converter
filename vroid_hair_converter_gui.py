#!/usr/bin/env python3
"""
vroid_hair_converter_gui.py
===========================
Simple drag-or-browse GUI for vroid_hair_type_converter.py

Usage:
    python vroid_hair_converter_gui.py
    -- or double-click it, or use run_converter.bat --

You can also drag a .vroidcustomitem file onto the window to load it.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys, os, threading

# ── locate the converter module ──────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

try:
    from vroid_hair_type_converter import convert, SLOTS
except ImportError as e:
    import tkinter as tk
    root = tk.Tk(); root.withdraw()
    import tkinter.messagebox as mb
    mb.showerror("Import error",
        f"Cannot import vroid_hair_type_converter:\n{e}\n\n"
        "Make sure vroid_hair_type_converter.py is in the same folder.")
    sys.exit(1)


SLOT_NAMES = list(SLOTS.keys())   # Front, Back, Sideburns, Ahoge, Extensions, Extra, Overall_Hair

# Per-language slot labels. The Japanese term (VRoid's native label) is kept
# in parentheses in both languages so it stays recognizable in-app.
SLOT_DISPLAY = {
    "en": {
        "Front":        "Front (前髪)",
        "Back":         "Back (後ろ髪)",
        "Sideburns":    "Sideburns (横髪)",
        "Ahoge":        "Ahoge (アホ毛)",
        "Extensions":   "Extensions (エクステ)",
        "Extra":        "Extra (ハネ毛)",
        "Overall_Hair": "Overall Hair (全体)",
    },
    "zh": {
        "Front":        "前发 (前髪)",
        "Back":         "后发 (後ろ髪)",
        "Sideburns":    "鬓发 (横髪)",
        "Ahoge":        "呆毛 (アホ毛)",
        "Extensions":   "接发 (エクステ)",
        "Extra":        "翘发 (ハネ毛)",
        "Overall_Hair": "整体发型 (全体)",
    },
}

# ── UI string table (English / Simplified Chinese) ───────────────────────────
LANGUAGES = [("English", "en"), ("简体中文", "zh")]

I18N = {
    "en": {
        "title":            "VRoid Hair Slot Converter",
        "lang_label":       "Language:",
        "file_frame":       "Input file  (.vroidcustomitem)",
        "browse":           "Browse…",
        "slot_frame":       "Convert TO slot",
        "out_frame":        "Output",
        "out_same":         "Same folder as input file",
        "convert":          "▶  Convert",
        "log_frame":        "Log",
        "status_converting":"Converting…",
        "status_success":   "✓ Success!",
        "status_error":     "✗ Error",
        "drop_not_item":    "⚠  Dropped file is not a .vroidcustomitem",
        "browse_title":     "Select a .vroidcustomitem file",
        "filetype_item":    "VRoid custom item",
        "filetype_all":     "All files",
        "warn_nofile_t":    "No file",
        "warn_nofile_m":    "Please select a .vroidcustomitem file first.",
        "err_notfound_t":   "File not found",
        "err_notfound_m":   "Cannot find:\n{path}",
        "done_t":           "Done",
        "done_m":           "Converted successfully!\n\n{name}\n\nSaved in:\n{folder}",
        "err_convert_t":    "Conversion failed",
        "log_input":        "  Input  : ",
        "log_target":       "  Target : ",
        "log_done":         "✓ Done! Saved to:",
        "log_error":        "✗ Error: ",
    },
    "zh": {
        "title":            "VRoid 发型槽位转换器",
        "lang_label":       "语言：",
        "file_frame":       "输入文件  (.vroidcustomitem)",
        "browse":           "浏览…",
        "slot_frame":       "转换到目标槽位",
        "out_frame":        "输出",
        "out_same":         "与输入文件相同的文件夹",
        "convert":          "▶  转换",
        "log_frame":        "日志",
        "status_converting":"转换中…",
        "status_success":   "✓ 成功！",
        "status_error":     "✗ 错误",
        "drop_not_item":    "⚠  拖入的文件不是 .vroidcustomitem 文件",
        "browse_title":     "选择一个 .vroidcustomitem 文件",
        "filetype_item":    "VRoid 自定义物品",
        "filetype_all":     "所有文件",
        "warn_nofile_t":    "未选择文件",
        "warn_nofile_m":    "请先选择一个 .vroidcustomitem 文件。",
        "err_notfound_t":   "文件未找到",
        "err_notfound_m":   "找不到：\n{path}",
        "done_t":           "完成",
        "done_m":           "转换成功！\n\n{name}\n\n保存在：\n{folder}",
        "err_convert_t":    "转换失败",
        "log_input":        "  输入  : ",
        "log_target":       "  目标  : ",
        "log_done":         "✓ 完成！已保存到：",
        "log_error":        "✗ 错误: ",
    },
}


def _make_dpi_aware():
    """Tell Windows this process handles DPI itself, so the UI is rendered
    crisply instead of being bitmap-stretched (blurry) on scaled/high-DPI
    displays. Must run *before* the first Tk window is created."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        try:
            # PROCESS_SYSTEM_DPI_AWARE = 1  → sharp text, single scale factor
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            # Older Windows without shcore.dll
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self._apply_dpi_scaling()
        self.lang = "en"            # current UI language ("en" | "zh")
        self._status_key = ""       # current status message key (for re-texting)
        self.resizable(True, True)
        self.minsize(int(560 * self._scale), int(460 * self._scale))
        self._build_ui()
        self._enable_drop()
        self._retext()              # apply initial language to every widget

    # ── Translation helpers ─────────────────────────────────────────────────────
    def _t(self, key: str) -> str:
        """Look up a UI string for the current language (falls back to English)."""
        return I18N.get(self.lang, I18N["en"]).get(key, I18N["en"].get(key, key))

    def _slot_display(self, name: str) -> str:
        return SLOT_DISPLAY.get(self.lang, SLOT_DISPLAY["en"])[name]

    def _on_lang_change(self, *_):
        sel = self.lang_combo.get()
        self.lang = dict(LANGUAGES).get(sel, "en")
        self._retext()

    def _retext(self):
        """Re-apply every user-facing string for the current language."""
        self.title(self._t("title"))
        self.lang_lbl.config(text=self._t("lang_label"))
        self.file_frame.config(text=self._t("file_frame"))
        self.browse_btn.config(text=self._t("browse"))
        self.slot_frame.config(text=self._t("slot_frame"))
        for name, rb in self.slot_rbs.items():
            rb.config(text=self._slot_display(name))
        self.out_frame.config(text=self._t("out_frame"))
        self.convert_btn.config(text=self._t("convert"))
        self.log_frame.config(text=self._t("log_frame"))
        self._update_out_label()
        self._set_status(self._status_key)

    # ── High-DPI scaling ──────────────────────────────────────────────────────
    def _apply_dpi_scaling(self):
        """Match Tk's point→pixel scaling to the real screen DPI so fonts and
        widgets are both sharp and correctly sized. Pairs with _make_dpi_aware()."""
        try:
            dpi = self.winfo_fpixels("1i")   # pixels-per-inch reported by the OS
        except Exception:
            dpi = 96.0
        self._scale = max(dpi / 96.0, 1.0)
        try:
            # Tk measures points as 1/72 inch; align it to the actual DPI.
            self.tk.call("tk", "scaling", dpi / 72.0)
        except Exception:
            pass

    # ── UI Layout ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        PAD = 10

        # ── Language switcher (top bar) ───────────────────────────────────────
        top = ttk.Frame(self)
        top.pack(fill="x", padx=PAD, pady=(PAD, 0))

        self.lang_combo = ttk.Combobox(
            top, width=10, state="readonly",
            values=[label for label, _ in LANGUAGES]
        )
        self.lang_combo.set(LANGUAGES[0][0])
        self.lang_combo.pack(side="right")
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_lang_change)

        self.lang_lbl = ttk.Label(top, text="")
        self.lang_lbl.pack(side="right", padx=(0, 6))

        # ── File row ──────────────────────────────────────────────────────────
        self.file_frame = ttk.LabelFrame(self, text="", padding=PAD)
        self.file_frame.pack(fill="x", padx=PAD, pady=(PAD, 0))

        self.file_var = tk.StringVar()
        entry = ttk.Entry(self.file_frame, textvariable=self.file_var, width=52)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.browse_btn = ttk.Button(self.file_frame, text="", command=self._browse)
        self.browse_btn.pack(side="left")

        # ── Target slot ───────────────────────────────────────────────────────
        self.slot_frame = ttk.LabelFrame(self, text="", padding=PAD)
        self.slot_frame.pack(fill="x", padx=PAD, pady=(PAD, 0))

        self.slot_var = tk.StringVar(value=SLOT_NAMES[0])
        self.slot_rbs = {}
        for name in SLOT_NAMES:
            rb = ttk.Radiobutton(
                self.slot_frame, text="",
                variable=self.slot_var, value=name
            )
            rb.pack(anchor="w")
            self.slot_rbs[name] = rb

        # ── Output location ───────────────────────────────────────────────────
        self.out_frame = ttk.LabelFrame(self, text="", padding=PAD)
        self.out_frame.pack(fill="x", padx=PAD, pady=(PAD, 0))

        self.out_var = tk.StringVar()
        ttk.Label(self.out_frame, textvariable=self.out_var, foreground="#555").pack(anchor="w")

        # ── Convert button ────────────────────────────────────────────────────
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=PAD, pady=PAD)

        self.convert_btn = ttk.Button(
            btn_frame, text="", command=self._convert, width=18
        )
        self.convert_btn.pack(side="left")

        self.status_lbl = ttk.Label(btn_frame, text="", foreground="gray")
        self.status_lbl.pack(side="left", padx=12)

        # ── Log ───────────────────────────────────────────────────────────────
        self.log_frame = ttk.LabelFrame(self, text="", padding=PAD)
        self.log_frame.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))

        self.log = scrolledtext.ScrolledText(
            self.log_frame, height=8, state="disabled",
            font=("Consolas", 9), wrap="word"
        )
        self.log.pack(fill="both", expand=True)

        # Update output label when file path changes
        self.file_var.trace_add("write", lambda *_: self._update_out_label())

    # ── Enable drag-and-drop (Windows) ────────────────────────────────────────
    def _enable_drop(self):
        try:
            self.drop_target_register("DND_Files")
            self.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass   # tkinterdnd2 not installed – silently skip

    def _on_drop(self, event):
        path = event.data.strip("{}")
        if path.lower().endswith(".vroidcustomitem"):
            self.file_var.set(path)
        else:
            self._log(self._t("drop_not_item"))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _browse(self):
        path = filedialog.askopenfilename(
            title=self._t("browse_title"),
            filetypes=[(self._t("filetype_item"), "*.vroidcustomitem"),
                       (self._t("filetype_all"), "*")]
        )
        if path:
            self.file_var.set(path)

    def _update_out_label(self):
        p = self.file_var.get()
        if p:
            folder = os.path.dirname(os.path.abspath(p))
            self.out_var.set(folder)
        else:
            self.out_var.set(self._t("out_same"))

    def _log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # Status message key → (i18n string key, colour)
    _STATUS = {
        "converting": ("status_converting", "orange"),
        "success":    ("status_success", "green"),
        "error":      ("status_error", "red"),
    }

    def _set_status(self, key, color=None):
        """Set the status label by message key so it re-texts on language switch."""
        self._status_key = key
        if not key:
            self.status_lbl.configure(text="", foreground="gray")
            return
        str_key, default_color = self._STATUS.get(key, (key, "gray"))
        self.status_lbl.configure(text=self._t(str_key), foreground=color or default_color)

    # ── Conversion ────────────────────────────────────────────────────────────
    def _convert(self):
        path = self.file_var.get().strip()
        target = self.slot_var.get()

        if not path:
            messagebox.showwarning(self._t("warn_nofile_t"), self._t("warn_nofile_m"))
            return
        if not os.path.isfile(path):
            messagebox.showerror(self._t("err_notfound_t"),
                                 self._t("err_notfound_m").format(path=path))
            return

        self.convert_btn.configure(state="disabled")
        self._set_status("converting")
        self._log(f"\n{'='*55}")
        self._log(self._t("log_input") + os.path.basename(path))
        self._log(self._t("log_target") + target)
        self._log(f"{'='*55}")

        # Run in background thread so the UI stays responsive
        threading.Thread(target=self._run_convert, args=(path, target), daemon=True).start()

    def _run_convert(self, path, target):
        # Redirect stdout to the log widget
        old_stdout = sys.stdout
        sys.stdout = _LogRedirect(self._log)
        try:
            out_path = convert(path, target)
            sys.stdout = old_stdout
            self.after(0, self._on_success, out_path)
        except Exception as exc:
            sys.stdout = old_stdout
            self.after(0, self._on_error, str(exc))

    def _on_success(self, out_path):
        self._log("\n" + self._t("log_done") + f"\n  {out_path}\n")
        self._set_status("success")
        self.convert_btn.configure(state="normal")
        messagebox.showinfo(self._t("done_t"),
            self._t("done_m").format(name=os.path.basename(out_path),
                                     folder=os.path.dirname(out_path)))

    def _on_error(self, msg):
        self._log("\n" + self._t("log_error") + f"{msg}\n")
        self._set_status("error")
        self.convert_btn.configure(state="normal")
        messagebox.showerror(self._t("err_convert_t"), msg)


class _LogRedirect:
    """Redirect sys.stdout lines to the GUI log widget."""
    def __init__(self, log_fn):
        self._log = log_fn
        self._buf = ""

    def write(self, text):
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._log(line)

    def flush(self):
        if self._buf:
            self._log(self._buf)
            self._buf = ""


if __name__ == "__main__":
    # Make the process DPI-aware *before* any Tk window exists (fixes blur).
    _make_dpi_aware()

    # Try to enable drag-and-drop via tkinterdnd2 if available
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk
    except ImportError:
        root = None

    if root:
        class App2(App, root): pass
        app = App2()
    else:
        app = App()

    app.mainloop()
