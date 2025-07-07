import sys, threading, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

def check_venv():
    script_dir = Path(__file__).parent
    venv_path = script_dir / ".venv312"
    if venv_path.exists() and (venv_path / "Scripts" / "pythonw.exe").exists():
        venv_python = str(venv_path / "Scripts" / "pythonw.exe")
        if sys.executable != venv_python:
            print(f"Switching to virtual environment: {venv_python}")
            import subprocess
            subprocess.run([venv_python, __file__] + sys.argv[1:])
            sys.exit(0)

if not getattr(sys, 'frozen', False):
    check_venv()

try:
    import numpy as np
except ImportError:
    messagebox.showerror("Missing Library", "NumPy is not installed. Please install it with: pip install numpy")
    sys.exit(1)

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
        base_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
        icon_path = base_dir / 'icon.ico'
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except tk.TclError:
                print(f"Warning: Could not set icon from {icon_path}")
        else:
            print(f"Warning: Icon file not found at {icon_path}")
        self.files = []
        self.dir = None
        self.output_dir = None
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
        src = None
        if ovr:
            if self.files:
                src = Path(self.files[0]).parent
            elif self.dir:
                src = self.dir
            self.b_out.config(state="disabled")
            if src:
                txt = f"{src.resolve().as_posix()} (Overwriting original images)"
            else:
                txt = "Please select an input first (Overwriting original images)"
        else:
            self.b_out.config(state="normal")
            d = self.output_dir
            if d:
                txt = f"{d / 'premult'}"
            elif self.files:
                src = Path(self.files[0]).parent
                txt = f"{src / 'premult'}"
            elif self.dir:
                txt = f"{self.dir / 'premult'}"
            else:
                txt = "Please select an input first"
        self.l_out.config(text=txt)

    def img_count(self):
        if self.files:
            return len(self.files)
        if self.dir:
            return len([f for f in self.dir.iterdir() if f.is_file() and f.suffix.lower() == '.png' and not f.name.endswith('_premult.png')])
        return 0

    def upd_btn_text(self):
        n = self.img_count()
        self.b_proc.config(text=f"Process {n} Images" if n else "Process Images")

    def pick_files(self):
        files = filedialog.askopenfilenames(title="Select PNG Images", filetypes=[("PNG images", "*.png"), ("All images", "*.*")])
        if files:
            self.files = list(files)
            self.dir = None
            self.l_files.config(text=f"{len(files)} images selected")
            self.l_dir.config(text="No directory selected")
            self.reset()
            self.log(f"Selected {len(files)} images")
            self.set_output_disp()
            self.upd_btn_text()
        self.update_process_button_state()

    def pick_dir(self):
        dir_path = filedialog.askdirectory(title="Select Directory")
        if dir_path:
            self.dir = Path(dir_path)
            self.files = []
            n = self.img_count()
            self.l_dir.config(text=f"{self.dir} ({n} images)")
            self.l_files.config(text="No images selected")
            self.reset()
            self.log(f"Selected directory: {self.dir} ({n} images)")
            self.upd_btn_text()
            self.set_output_disp()
        self.update_process_button_state()

    def pick_out(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir = Path(dir_path)
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

    def out_path(self, file_path):
        input_path = Path(file_path)
        if self.overwrite.get():
            return input_path
        d_path = self.output_dir if self.output_dir else input_path.parent
        premult_dir = d_path / "premult"
        premult_dir.mkdir(parents=True, exist_ok=True)
        output_filename = input_path.stem + '.png'
        return premult_dir / output_filename

    def proc_one(self, file_path):
        try:
            with Image.open(file_path) as img:
                if img.format != 'PNG':
                    self.log(f"✗ Error processing {Path(file_path).name}: Not a PNG image.")
                    return False
                oimg = self.premult(img)
                opath = self.out_path(file_path)
                oimg.save(opath)
                self.log(f"✓ Processed: {Path(file_path).name}")
                return True
        except UnidentifiedImageError:
            self.log(f"✗ Error processing {Path(file_path).name}: Could not identify image file. It might be corrupted or not an image.")
            return False
        except Exception as e:
            self.log(f"✗ Error processing {Path(file_path).name}: {e}")
            return False

    def proc_thread(self):
        try:
            self.busy = True
            self.b_proc.config(state="disabled")
            self.progress.set(0)
            if self.files:
                fs = self.files
            elif self.dir:
                fs = [str(f) for f in self.dir.iterdir() 
                      if f.is_file() and f.suffix.lower() == '.png' and not f.name.endswith('_premult.png')]
            else:
                fs = []
                
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