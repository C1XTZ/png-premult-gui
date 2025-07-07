import sys, os, threading, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import numpy as np

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:
    messagebox.showerror("Missing Library", "Pillow is not installed. Please install it with: pip install pillow")
    sys.exit(1)

class PNGPremultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG Alpha Premultiplication Tool")
        self.root.geometry("600x500")
        icon_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(icon_dir, 'icon.ico')
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        self.files = []
        self.dir = ""
        self.output_dir = ""
        self.overwrite = tk.BooleanVar(value=False)
        self.busy = False
        self.progress = tk.DoubleVar()
        self.build_ui()
        self.overwrite.trace_add('write', lambda *_: self.set_output_disp())
        self.update_process_button_state()

    def build_ui(self):
        f = ttk.Frame(self.root, padding=10)
        f.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)

        lf_file = ttk.LabelFrame(f, text="File Selection", padding=10)
        lf_file.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,10))
        lf_file.columnconfigure(1, weight=1)
        ttk.Button(lf_file, text="Select Images", command=self.pick_files, width=15).grid(row=0, column=0, padx=(0,10))
        self.l_files = ttk.Label(lf_file, text="No images selected")
        self.l_files.grid(row=0, column=1, sticky="ew")
        ttk.Button(lf_file, text="Select Directory", command=self.pick_dir, width=15).grid(row=1, column=0, padx=(0,10), pady=(10,0))
        self.l_dir = ttk.Label(lf_file, text="No directory selected")
        self.l_dir.grid(row=1, column=1, sticky="ew", pady=(10,0))

        lf_opt = ttk.LabelFrame(f, text="Options", padding=10)
        lf_opt.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0,10))
        ttk.Checkbutton(lf_opt, text="Overwrite original images", variable=self.overwrite).grid(row=0, column=0, sticky="w")

        lf_out = ttk.LabelFrame(f, text="Output Location", padding=10)
        lf_out.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0,10))
        lf_out.columnconfigure(0, weight=1)
        self.l_out = ttk.Label(lf_out, text="")
        self.l_out.grid(row=0, column=0, sticky="ew", pady=(0,5))
        self.b_out = ttk.Button(lf_out, text="Change Output Location", command=self.pick_out)
        self.b_out.grid(row=1, column=0, sticky="w")
        self.set_output_disp()

        self.b_proc = ttk.Button(f, text="Process Images", command=self.process, style="Accent.TButton")
        self.b_proc.grid(row=3, column=0, columnspan=3, pady=(0,10))
        self.pb = ttk.Progressbar(f, variable=self.progress, maximum=100)
        self.pb.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0,10))
        self.l_stat = ttk.Label(f, text="Ready")
        self.l_stat.grid(row=5, column=0, columnspan=3)

        lf_log = ttk.LabelFrame(f, text="Processing Log", padding=10)
        lf_log.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(10,0))
        lf_log.columnconfigure(0, weight=1)
        lf_log.rowconfigure(0, weight=1)
        f.rowconfigure(6, weight=1)
        self.t_log = tk.Text(lf_log, height=10, wrap=tk.WORD)
        sb = ttk.Scrollbar(lf_log, orient=tk.VERTICAL, command=self.t_log.yview)
        self.t_log.configure(yscrollcommand=sb.set)
        self.t_log.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

    def update_process_button_state(self):
        if self.files or self.dir:
            self.b_proc.config(state="normal")
        else:
            self.b_proc.config(state="disabled")

    def set_output_disp(self):
        ovr = self.overwrite.get()
        src = ""
        if ovr:
            if self.files:
                src = os.path.dirname(self.files[0])
            elif self.dir:
                src = self.dir
            self.b_out.config(state="disabled")
            if src:
                txt = f"{Path(src).resolve().as_posix()} (Overwriting original images)"
            else:
                txt = "Please select an input first (Overwriting original images)"
        else:
            self.b_out.config(state="normal")
            d = self.output_dir
            if d:
                txt = f"{Path(d).joinpath('premult').resolve().as_posix()}"
            elif self.files:
                src = os.path.dirname(self.files[0])
                txt = f"{Path(src).joinpath('premult').resolve().as_posix()}"
            elif self.dir:
                txt = f"{Path(self.dir).joinpath('premult').resolve().as_posix()}"
            else:
                txt = "Please select an input first"
        self.l_out.config(text=txt)

    def img_count(self):
        if self.files:
            return len(self.files)
        if self.dir:
            return len([f for f in os.listdir(self.dir) if f.lower().endswith('.png') and not f.endswith('_premult.png')])
        return 0

    def upd_btn_text(self):
        n = self.img_count()
        self.b_proc.config(text=f"Process {n} Images" if n else "Process Images")

    def pick_files(self):
        fs = filedialog.askopenfilenames(title="Select PNG Images", filetypes=[("PNG images", "*.png"), ("All images", "*.*")])
        if fs:
            self.files = list(fs)
            self.dir = ""
            self.l_files.config(text=f"{len(fs)} images selected")
            self.l_dir.config(text="No directory selected")
            self.reset()
            self.log(f"Selected {len(fs)} images")
            self.set_output_disp()
            self.upd_btn_text()
        self.update_process_button_state()

    def pick_dir(self):
        d = filedialog.askdirectory(title="Select Directory")
        if d:
            self.dir = d
            self.files = []
            n = len([f for f in os.listdir(d) if f.lower().endswith('.png') and not f.endswith('_premult.png')])
            self.l_dir.config(text=f"{d} ({n} images)")
            self.l_files.config(text="No images selected")
            self.reset()
            self.log(f"Selected directory: {d} ({n} images)")
            self.upd_btn_text()
            self.set_output_disp()
        self.update_process_button_state()

    def pick_out(self):
        d = filedialog.askdirectory(title="Select Output Directory")
        if d:
            self.output_dir = d
        self.set_output_disp()

    def reset(self):
        self.l_stat.config(text="Ready")
        self.progress.set(0)

    def log(self, msg):
        self.t_log.insert(tk.END, msg + "\n")
        self.t_log.see(tk.END)
        self.root.update_idletasks()

    def stat(self, msg):
        self.l_stat.config(text=msg)
        self.root.update_idletasks()

    def premult(self, img):
        img = img.convert("RGBA")
        arr = np.array(img, dtype=np.float32)
        alpha = arr[:, :, 3:4] / 255.0
        arr[:, :, :3] *= alpha
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    def out_path(self, fp):
        input_path = Path(fp)
        if self.overwrite.get():
            return input_path, input_path.name
        d_path = Path(self.output_dir) if self.output_dir else input_path.parent if input_path.parent else Path('.')
        pdir_path = d_path / "premult"
        pdir_path.mkdir(parents=True, exist_ok=True)
        output_filename = input_path.stem + '.png'
        return pdir_path / output_filename, output_filename

    def proc_one(self, fp):
        try:
            with Image.open(fp) as img:
                if img.format != 'PNG':
                    self.log(f"✗ Error processing {Path(fp).name}: Not a PNG image.")
                    return False
                oimg = self.premult(img)
                opath, disp = self.out_path(fp)
                oimg.save(opath)
                self.log(f"✓ Processed: {Path(fp).name}")
                return True
        except UnidentifiedImageError:
            self.log(f"✗ Error processing {Path(fp).name}: Could not identify image file. It might be corrupted or not an image.")
            return False
        except Exception as e:
            self.log(f"✗ Error processing {Path(fp).name}: {e}")
            return False

    def proc_thread(self):
        try:
            self.busy = True
            self.b_proc.config(state="disabled")
            self.progress.set(0)
            fs = self.files or [os.path.join(self.dir, f) for f in os.listdir(self.dir) if f.lower().endswith('.png') and not f.endswith('_premult.png')]
            if not fs:
                self.log("No images to process!")
                self.stat("Ready")
                return
            n = len(fs)
            ok = 0
            self.log(f"Starting processing of {n} images...")
            self.stat(f"Processing {n} images...")
            for i, fp in enumerate(fs):
                if self.proc_one(fp):
                    ok += 1
                self.progress.set((i+1)/n*100)
                self.stat(f"Processing {i+1}/{n}...")
            self.log(f"Processing complete! {ok}/{n} images processed successfully.")
            self.stat(f"Complete: {ok}/{n} processed")
        except Exception as e:
            self.log(f"Error during processing: {e}")
            self.stat("Error occurred")
        finally:
            self.busy = False
            self.b_proc.config(state="normal")
            self.progress.set(0)
            self.upd_btn_text()
            self.update_process_button_state()

    def process(self):
        if self.busy:
            return
        if not self.files and not self.dir:
            messagebox.showwarning("No Selection", "Please select images or a directory first!")
            return
        threading.Thread(target=self.proc_thread, daemon=True).start()

def main():
    root = tk.Tk()
    PNGPremultApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()