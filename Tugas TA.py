import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import json

class KegiatanHarian:
    def __init__(self, nama="", waktu_mulai="", waktu_selesai="", lokasi=""):
        self.nama = nama
        self.waktu_mulai = waktu_mulai
        self.waktu_selesai = waktu_selesai
        self.lokasi = lokasi

    def to_dict(self):
        return {
            "nama": self.nama,
            "waktu_mulai": self.waktu_mulai,
            "waktu_selesai": self.waktu_selesai,
            "lokasi": self.lokasi
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nama"], data["waktu_mulai"], data["waktu_selesai"], data["lokasi"])

    def __str__(self):
        return f"{self.nama} dari {self.waktu_mulai} sampai {self.waktu_selesai} di {self.lokasi}"

class KegiatanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jadwal Kegiatan Harian")

        # Adding colors
        self.bg_color = "#dbe7ff"
        self.frame_color = "#98c1d9"
        self.button_color = "#3d5a80"
        self.button_text_color = "#ffffff"

        self.root.configure(bg=self.bg_color)

        self.hari_options = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        self.kegiatan_dict = {hari: [] for hari in self.hari_options}
        self.previous_state = None

        self.notebook = ttk.Notebook(root)
        self.frames = {hari: ttk.Frame(self.notebook) for hari in self.hari_options}
        for hari, frame in self.frames.items():
            self.notebook.add(frame, text=hari)
        self.notebook.grid(row=0, column=0, columnspan=4)

        self.nama_entry = tk.Entry(root, width=30)
        self.waktu_mulai_entry = ttk.Combobox(root, values=self.generate_time_options(), width=10)
        self.waktu_selesai_entry = ttk.Combobox(root, values=self.generate_time_options(), width=10)
        self.lokasi_entry = tk.Entry(root, width=30)

        self.nama_label = tk.Label(root, text="Nama Kegiatan:", bg=self.bg_color)
        self.waktu_mulai_label = tk.Label(root, text="Waktu Mulai:", bg=self.bg_color)
        self.waktu_selesai_label = tk.Label(root, text="Waktu Selesai:", bg=self.bg_color)
        self.lokasi_label = tk.Label(root, text="Lokasi:", bg=self.bg_color)
        self.hari_label = tk.Label(root, text="Hari:", bg=self.bg_color)

        self.hari_var = tk.StringVar(root)
        self.hari_var.set(self.hari_options[0])  # Default value
        self.hari_menu = ttk.Combobox(root, textvariable=self.hari_var, values=self.hari_options, state='readonly')

        self.tambah_button = tk.Button(root, text="Tambah Kegiatan", command=self.tambah_kegiatan,
                                       bg=self.button_color, fg=self.button_text_color)
        self.hapus_button = tk.Button(root, text="Hapus Kegiatan", command=self.hapus_kegiatan,
                                      bg=self.button_color, fg=self.button_text_color)
        self.reset_button = tk.Button(root, text="Reset", command=self.reset_fields,
                                      bg=self.button_color, fg=self.button_text_color)
        self.undo_button = tk.Button(root, text="Undo", command=self.undo_last_action,
                                      bg=self.button_color, fg=self.button_text_color)

        self.simpan_button = tk.Button(root, text="Simpan Jadwal", command=self.simpan_jadwal,
                                       bg=self.button_color, fg=self.button_text_color)
        self.muatan_button = tk.Button(root, text="Muat Jadwal", command=self.muat_jadwal,
                                       bg=self.button_color, fg=self.button_text_color)

        self.nama_label.grid(row=1, column=0, padx=10, pady=5)
        self.nama_entry.grid(row=1, column=1, padx=10, pady=5)
        self.waktu_mulai_label.grid(row=2, column=0, padx=10, pady=5)
        self.waktu_mulai_entry.grid(row=2, column=1, padx=10, pady=5)
        self.waktu_selesai_label.grid(row=2, column=2, padx=10, pady=5)
        self.waktu_selesai_entry.grid(row=2, column=3, padx=10, pady=5)
        self.lokasi_label.grid(row=3, column=0, padx=10, pady=5)
        self.lokasi_entry.grid(row=3, column=1, padx=10, pady=5)
        self.hari_label.grid(row=4, column=0, padx=10, pady=5)
        self.hari_menu.grid(row=4, column=1, padx=10, pady=5)
        self.tambah_button.grid(row=5, column=0, padx=10, pady=5)
        self.hapus_button.grid(row=5, column=1, padx=10, pady=5)
        self.reset_button.grid(row=5, column=2, padx=10, pady=5)
        self.undo_button.grid(row=5, column=3, padx=10, pady=5)
        self.simpan_button.grid(row=6, column=0, padx=10, pady=5)
        self.muatan_button.grid(row=6, column=1, padx=10, pady=5)

        self.kegiatan_listboxes = {}
        for hari, frame in self.frames.items():
            listbox = tk.Listbox(frame, height=10, width=50, bg=self.bg_color, selectmode=tk.MULTIPLE)
            listbox.pack(padx=10, pady=10)
            self.kegiatan_listboxes[hari] = listbox

    def generate_time_options(self):
        times = []
        for hour in range(24):
            for minute in ["00", "30"]:
                times.append(f"{hour:02}:{minute}")
        return times

    def save_previous_state(self):
        self.previous_state = {hari: [kegiatan.to_dict() for kegiatan in kegiatan_list] for hari, kegiatan_list in self.kegiatan_dict.items()}

    def tambah_kegiatan(self):
        nama = self.nama_entry.get()
        waktu_mulai = self.waktu_mulai_entry.get()
        waktu_selesai = self.waktu_selesai_entry.get()
        lokasi = self.lokasi_entry.get()
        hari = self.hari_var.get()

        if not nama or not waktu_mulai or not waktu_selesai or not lokasi:
            messagebox.showinfo("Info", "Semua kolom harus diisi.")
            return

        self.save_previous_state()

        kegiatan = KegiatanHarian(nama, waktu_mulai, waktu_selesai, lokasi)
        self.kegiatan_dict[hari].append(kegiatan)

        self.update_kegiatan_listbox(hari)
        self.reset_fields()

    def update_kegiatan_listbox(self, hari):
        listbox = self.kegiatan_listboxes[hari]
        listbox.delete(0, tk.END)
        for kegiatan in self.kegiatan_dict[hari]:
            listbox.insert(tk.END, str(kegiatan))

    def hapus_kegiatan(self):
        hari = self.hari_var.get()
        listbox = self.kegiatan_listboxes[hari]
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("Info", "Pilih kegiatan yang ingin dihapus.")
            return

        self.save_previous_state()

        for index in selected_indices[::-1]:
            del self.kegiatan_dict[hari][index]

        self.update_kegiatan_listbox(hari)

    def reset_fields(self):
        self.nama_entry.delete(0, tk.END)
        self.waktu_mulai_entry.set("")
        self.waktu_selesai_entry.set("")
        self.lokasi_entry.delete(0, tk.END)

    def undo_last_action(self):
        if self.previous_state:
            self.kegiatan_dict = {hari: [KegiatanHarian.from_dict(kegiatan) for kegiatan in kegiatan_list] for hari, kegiatan_list in self.previous_state.items()}
            for hari in self.hari_options:
                self.update_kegiatan_listbox(hari)
            self.previous_state = None
            messagebox.showinfo("Info", "Aksi terakhir telah dibatalkan.")
        else:
            messagebox.showinfo("Info", "Tidak ada aksi yang bisa dibatalkan.")

    def simpan_jadwal(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            data = {hari: [kegiatan.to_dict() for kegiatan in kegiatan_list] for hari, kegiatan_list in self.kegiatan_dict.items()}
            with open(file_path, 'w') as file:
                json.dump(data, file)
            messagebox.showinfo("Info", "Jadwal berhasil disimpan.")

    def muat_jadwal(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)
            self.kegiatan_dict = {hari: [KegiatanHarian.from_dict(kegiatan) for kegiatan in kegiatan_list] for hari, kegiatan_list in data.items()}
            for hari in self.hari_options:
                self.update_kegiatan_listbox(hari)
            messagebox.showinfo("Info", "Jadwal berhasil dimuat.")

class IntroScreen:
    def __init__(self, root, main_app_callback):
        self.root = root
        self.main_app_callback = main_app_callback
        self.root.title("Selamat Datang")

        self.frame = tk.Frame(root, bg="#dbe7ff")
        self.frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.frame, text="Selamat Datang di Aplikasi Jadwal Kegiatan Harian", 
                              font=("Helvetica", 16), bg="#dbe7ff", fg="#3d5a80")
        self.label.pack(pady=20)

        self.start_button = tk.Button(self.frame, text="Mulai", command=self.start_app, 
                                      bg="#3d5a80", fg="#ffffff", font=("Helvetica", 12))
        self.start_button.pack(pady=10)

    def start_app(self):
        self.frame.pack_forget()
        self.main_app_callback()

if __name__ == "__main__":
    root = tk.Tk()

    def start_main_app():
        KegiatanGUI(root)

    intro = IntroScreen(root, start_main_app)
    root.mainloop()
