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
SLOT_DISPLAY = {
    "Front":        "Front (前髪)",
    "Back":         "Back (後ろ髪)",
    "Sideburns":    "Sideburns (横髪)",
    "Ahoge":        "Ahoge (アホ毛)",
    "Extensions":   "Extensions (エクステ)",
    "Extra":        "Extra (ハネ毛)",
    "Overall_Hair": "Overall Hair (全体)",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VRoid Hair Slot Converter")
        self.resizable(True, True)
        self.minsize(560, 460)
        self._build_ui()
        self._enable_drop()

    # ── UI Layout ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        PAD = 10

        # ── File row ──────────────────────────────────────────────────────────
        file_frame = ttk.LabelFrame(self, text="Input file  (.vroidcustomitem)", padding=PAD)
        file_frame.pack(fill="x", padx=PAD, pady=(PAD, 0))

        self.file_var = tk.StringVar()
        entry = ttk.Entry(file_frame, textvariable=self.file_var, width=52)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ttk.Button(file_frame, text="Browse…", command=self._browse).pack(side="left")

        # ── Target slot ───────────────────────────────────────────────────────
        slot_frame = ttk.LabelFrame(self, text="Convert TO slot", padding=PAD)
        slot_frame.pack(fill="x", padx=PAD, pady=(PAD, 0))

        self.slot_var = tk.StringVar(value=SLOT_NAMES[0])

        for name in SLOT_NAMES:
            rb = ttk.Radiobutton(
                slot_frame, text=SLOT_DISPLAY[name],
                variable=self.slot_var, value=name
            )
            rb.pack(anchor="w")

        # ── Output location ───────────────────────────────────────────────────
        out_frame = ttk.LabelFrame(self, text="Output", padding=PAD)
        out_frame.pack(fill="x", padx=PAD, pady=(PAD, 0))

        self.out_var = tk.StringVar(value="Same folder as input file")
        ttk.Label(out_frame, textvariable=self.out_var, foreground="#555").pack(anchor="w")

        # ── Convert button ────────────────────────────────────────────────────
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=PAD, pady=PAD)

        self.convert_btn = ttk.Button(
            btn_frame, text="▶  Convert", command=self._convert, width=18
        )
        self.convert_btn.pack(side="left")

        self.status_lbl = ttk.Label(btn_frame, text="", foreground="gray")
        self.status_lbl.pack(side="left", padx=12)

        # ── Log ───────────────────────────────────────────────────────────────
        log_frame = ttk.LabelFrame(self, text="Log", padding=PAD)
        log_frame.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))

        self.log = scrolledtext.ScrolledText(
            log_frame, height=8, state="disabled",
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
            self._log("⚠  Dropped file is not a .vroidcustomitem")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select a .vroidcustomitem file",
            filetypes=[("VRoid custom item", "*.vroidcustomitem"), ("All files", "*")]
        )
        if path:
            self.file_var.set(path)

    def _update_out_label(self):
        p = self.file_var.get()
        if p:
            folder = os.path.dirname(os.path.abspath(p))
            self.out_var.set(folder)
        else:
            self.out_var.set("Same folder as input file")

    def _log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_status(self, text, color="gray"):
        self.status_lbl.configure(text=text, foreground=color)

    # ── Conversion ────────────────────────────────────────────────────────────
    def _convert(self):
        path = self.file_var.get().strip()
        target = self.slot_var.get()

        if not path:
            messagebox.showwarning("No file", "Please select a .vroidcustomitem file first.")
            return
        if not os.path.isfile(path):
            messagebox.showerror("File not found", f"Cannot find:\n{path}")
            return

        self.convert_btn.configure(state="disabled")
        self._set_status("Converting…", "orange")
        self._log(f"\n{'='*55}")
        self._log(f"  Input  : {os.path.basename(path)}")
        self._log(f"  Target : {target}")
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
        self._log(f"\n✓ Done! Saved to:\n  {out_path}\n")
        self._set_status("✓ Success!", "green")
        self.convert_btn.configure(state="normal")
        messagebox.showinfo("Done",
            f"Converted successfully!\n\n{os.path.basename(out_path)}\n\nSaved in:\n{os.path.dirname(out_path)}")

    def _on_error(self, msg):
        self._log(f"\n✗ Error: {msg}\n")
        self._set_status("✗ Error", "red")
        self.convert_btn.configure(state="normal")
        messagebox.showerror("Conversion failed", msg)


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
