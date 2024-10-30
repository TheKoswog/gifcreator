import os
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import imageio
from typing import List, Tuple
import json

class ModernGIFCreator:
    def __init__(self, master):
        self.master = master
        self.master.title("Modern GIF Creator")
        self.master.geometry("1000x600")
        self.master.configure(bg="#f0f2f5")
        
        # Tema renkleri
        self.colors = {
            "primary": "#2196f3",
            "secondary": "#e3f2fd",
            "accent": "#1976d2",
            "text": "#333333",
            "bg": "#f0f2f5"
        }
        
        # Temel değişkenler
        self.gif_folder = "gif"
        self.output_folder = "output"
        self.images: List[str] = []
        self.image_paths: List[str] = []
        self.delay = 0.5
        self.preview_size = (300, 300)
        self.random_order = tk.BooleanVar(value=False)
        
        # Klasörleri oluştur
        self._create_required_folders()
        
        # Arayüz oluştur
        self._setup_styles()
        self._create_main_layout()
        self._create_widgets()
        
        # Resimleri yükle
        self.load_images()
        
        # Ayarları yükle
        self._load_settings()

    def _create_required_folders(self):
        """Gerekli klasörleri oluşturur."""
        for folder in [self.gif_folder, self.output_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def _setup_styles(self):
        """TTK stillerini ayarlar."""
        self.style = ttk.Style()
        self.style.configure(
            "Custom.TButton",
            padding=(10, 5),
            font=("Helvetica", 10)
        )
        
        self.style.configure(
            "Preview.TFrame",
            background=self.colors["secondary"],
            relief="flat"
        )

    def _create_main_layout(self):
        """Ana düzen oluşturur."""
        # Ana container
        self.main_container = ttk.Frame(self.master)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Sol panel (Liste ve kontroller)
        self.left_panel = ttk.Frame(self.main_container)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Sağ panel (Önizleme ve ayarlar)
        self.right_panel = ttk.Frame(self.main_container)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

    def _create_widgets(self):
        """Tüm widget'ları oluşturur."""
        self._create_list_section()
        self._create_control_buttons()
        self._create_preview_section()
        self._create_settings_section()

    def _create_list_section(self):
        """Liste bölümünü oluşturur."""
        # Liste başlığı
        list_header = ttk.Label(
            self.left_panel,
            text="Resim Listesi",
            font=("Helvetica", 12, "bold")
        )
        list_header.pack(anchor=tk.W, pady=(0, 10))

        # Liste kutusu ve kaydırma çubuğu
        list_frame = ttk.Frame(self.left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            font=("Helvetica", 10),
            bg="white",
            fg=self.colors["text"],
            selectbackground=self.colors["primary"],
            selectforeground="white",
            activestyle="none"
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind('<<ListboxSelect>>', self.show_preview)

    def _create_control_buttons(self):
        """Kontrol düğmelerini oluşturur."""
        btn_frame = ttk.Frame(self.left_panel)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        # Düğme stilleri
        button_style = {
            "width": 15,
            "bg": self.colors["primary"],
            "fg": "white",
            "font": ("Helvetica", 10),
            "pady": 5,
            "relief": tk.FLAT,
            "cursor": "hand2"
        }

        tk.Button(
            btn_frame,
            text="↑ Yukarı Taşı",
            command=self.move_up,
            **button_style
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="↓ Aşağı Taşı",
            command=self.move_down,
            **button_style
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame,
            text="🗑️ Sil",
            command=self.delete_image,
            **button_style
        ).pack(side=tk.LEFT, padx=2)

    def _create_preview_section(self):
        """Önizleme bölümünü oluşturur."""
        preview_frame = ttk.Frame(self.right_panel, style="Preview.TFrame")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # Önizleme başlığı
        preview_header = ttk.Label(
            preview_frame,
            text="Önizleme",
            font=("Helvetica", 12, "bold")
        )
        preview_header.pack(pady=(0, 10))

        # Önizleme alanı
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(pady=10)

        # Önizleme kontrolleri
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        button_style = {
            "bg": self.colors["primary"],
            "fg": "white",
            "font": ("Helvetica", 10),
            "pady": 5,
            "relief": tk.FLAT,
            "cursor": "hand2"
        }

        tk.Button(
            controls_frame,
            text="🔄 Önizle",
            command=self.preview_gif,
            **button_style
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls_frame,
            text="💾 GIF Oluştur",
            command=self.create_gif,
            **button_style
        ).pack(side=tk.LEFT, padx=5)

    def _create_settings_section(self):
        """Ayarlar bölümünü oluşturur."""
        settings_frame = ttk.LabelFrame(
            self.right_panel,
            text="Ayarlar",
            padding=10
        )
        settings_frame.pack(fill=tk.X, pady=(20, 0))

        # Gecikme ayarı
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            delay_frame,
            text="Gecikme (saniye):"
        ).pack(side=tk.LEFT)

        self.delay_var = tk.DoubleVar(value=0.5)
        delay_options = [0.1, 0.3, 0.5, 1.0, 2.0]
        self.delay_menu = ttk.Combobox(
            delay_frame,
            textvariable=self.delay_var,
            values=delay_options,
            width=10,
            state="readonly"
        )
        self.delay_menu.pack(side=tk.LEFT, padx=(10, 0))

        # Rastgele sıralama seçeneği
        random_frame = ttk.Frame(settings_frame)
        random_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            random_frame,
            text="Rastgele Sırala",
            variable=self.random_order
        ).pack(side=tk.LEFT)

    def show_preview(self, event=None):
        """Seçili resmin önizlemesini gösterir."""
        selected = self.listbox.curselection()
        if not selected:
            return

        try:
            index = selected[0]
            image_path = self.image_paths[index]
            img = Image.open(image_path)
            img.thumbnail(self.preview_size)
            self.preview_image = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_image)
        except Exception as e:
            messagebox.showerror("Hata", f"Önizleme gösterilirken hata oluştu: {e}")

    def preview_gif(self):
        """GIF önizlemesi gösterir."""
        if not self.image_paths:
            messagebox.showerror("Hata", "Önizleme için resim ekleyin.")
            return

        try:
            delay = int(self.delay_var.get() * 1000)  # milisaniyeye çevir
            paths = self.image_paths.copy()

            if self.random_order.get():
                random.shuffle(paths)

            frames = []
            for path in paths:
                img = Image.open(path)
                img = img.convert('RGBA')
                img.thumbnail(self.preview_size)
                frames.append(img)

            # Geçici bir GIF oluştur
            temp_gif = os.path.join(self.output_folder, "temp_preview.gif")
            frames[0].save(
                temp_gif,
                save_all=True,
                append_images=frames[1:],
                duration=delay,
                loop=0
            )

            # Önizlemeyi göster
            preview_img = ImageTk.PhotoImage(file=temp_gif)
            self.preview_label.config(image=preview_img)
            self.preview_label.image = preview_img  # Referansı sakla

            # Geçici dosyayı sil
            os.remove(temp_gif)

        except Exception as e:
            messagebox.showerror("Hata", f"Önizleme oluşturulamadı: {str(e)}")

    def create_gif(self):
        """GIF dosyası oluşturur."""
        if not self.image_paths:
            messagebox.showerror("Hata", "GIF oluşturmak için resim ekleyin.")
            return

        try:
            # Kayıt yolu seç
            output_path = filedialog.asksaveasfilename(
                defaultextension=".gif",
                filetypes=[("GIF dosyası", "*.gif")],
                initialdir=self.output_folder,
                title="GIF'i Kaydet"
            )

            if not output_path:
                return

            delay = int(self.delay_var.get() * 1000)  # milisaniyeye çevir
            paths = self.image_paths.copy()

            if self.random_order.get():
                random.shuffle(paths)

            frames = []
            for path in paths:
                img = Image.open(path)
                img = img.convert('RGBA')
                frames.append(img)

            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=delay,
                loop=0,
                optimize=True
            )

            self._save_settings()  # Ayarları kaydet
            messagebox.showinfo("Başarılı", f"GIF başarıyla oluşturuldu:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"GIF oluşturulurken hata oluştu:\n{str(e)}")

    def _load_settings(self):
        """Kaydedilmiş ayarları yükler."""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.delay_var.set(settings.get('delay', 0.5))
                    self.random_order.set(settings.get('random_order', False))
        except Exception as e:
            print(f"Ayarlar yüklenirken hata oluştu: {e}")

    def _save_settings(self):
        """Mevcut ayarları kaydeder."""
        try:
            settings = {
                'delay': self.delay_var.get(),
                'random_order': self.random_order.get()
            }
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata oluştu: {e}")

    def load_images(self):
        """Resimleri yükler ve listeyi günceller."""
        self.listbox.delete(0, tk.END)
        self.images = []
        self.image_paths = []

        if not os.path.exists(self.gif_folder):
            messagebox.showerror(
                "Hata",
                f"'{self.gif_folder}' klasörü bulunamadı."
            )
            return

        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        try:
            for file in sorted(os.listdir(self.gif_folder)):
                if file.lower().endswith(valid_extensions):
                    full_path = os.path.join(self.gif_folder, file)
                    self.image_paths.append(full_path)
                    self.listbox.insert(tk.END, file)

            if not self.image_paths:
                messagebox.showinfo(
                    "Bilgi",
                    "GIF oluşturmak için 'gif' klasörüne resim ekleyin."
                )
        except Exception as e:
            messagebox.showerror("Hata", f"Resimler yüklenirken hata oluştu: {e}")

    def move_up(self):
        """Seçili resmi listede yukarı taşır."""
        selected = self.listbox.curselection()
        if not selected or selected[0] == 0:
            return

        index = selected[0]
        self.image_paths[index], self.image_paths[index - 1] = \
            self.image_paths[index - 1], self.image_paths[index]
        
        self.refresh_listbox()
        self.listbox.select_set(index - 1)

    def move_down(self):
        """Seçili resmi listede aşağı taşır."""
        selected = self.listbox.curselection()
        if not selected or selected[0] == len(self.image_paths) - 1:
            return

        index = selected[0]
        self.image_paths[index], self.image_paths[index + 1] = \
            self.image_paths[index + 1], self.image_paths[index]
        
        self.refresh_listbox()
        self.listbox.select_set(index + 1)

    def delete_image(self):
        """Seçili resmi listeden siler."""
        selected = self.listbox.curselection()
        if not selected:
            return

        if messagebox.askyesno("Onay", "Seçili resmi listeden silmek istiyor musunuz?"):
            index = selected[0]
            del self.image_paths[index]
            self.refresh_listbox()

    def refresh_listbox(self):
        """Liste kutusunu yeniler."""
        self.listbox.delete(0, tk.END)
        for path in self.image_paths:
            self.listbox.insert(tk.END, os.path.basename(path))

    def show_preview(self, event=None):
        """Seçili resmin önizlemesini gösterir."""
        selected = self.listbox.curselection()
        if not selected:
            return

        try:
            index = selected[0]
            image_path = self.image_paths[index]
            img = Image.open(image_path)
            img.thumbnail(self.preview_size)
            self.preview_image = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_image)
        except Exception as e:
            messagebox.showerror("Hata", f"Önizleme gösterilirken hata oluştu: {e}")

    def preview_gif(self):
        """GIF önizlemesi gösterir."""
        if not self.image_paths:
            messagebox.showerror("Hata", "Önizleme için resim ekleyin.")
            return

        try:
            delay = int(self.delay_var.get() * 1000)  # milisaniyeye çevir
            paths = self.image_paths.copy()

            if self.random_order.get():
                random.shuffle(paths)

            frames = []
            for path in paths:
                img = Image.open(path)
                img = img.convert('RGBA')
                img.thumbnail(self.preview_size)
                frames.append(img)

            # Geçici bir GIF oluştur
            temp_gif = os.path.join(self.output_folder, "temp_preview.gif")
            frames[0].save(
                temp_gif,
                save_all=True,
                append_images=frames[1:],
                duration=delay,
                loop=0
            )

            # Önizlemeyi göster
            preview_img = ImageTk.PhotoImage(file=temp_gif)
            self.preview_label.config(image=preview_img)
            self.preview_label.image = preview_img  # Referansı sakla

            # Geçici dosyayı sil
            os.remove(temp_gif)

        except Exception as e:
            messagebox.showerror("Hata", f"Önizleme oluşturulamadı: {str(e)}")

    def create_gif(self):
        """GIF dosyası oluşturur."""
        if not self.image_paths:
            messagebox.showerror("Hata", "GIF oluşturmak için resim ekleyin.")
            return

        try:
            # Kayıt yolu seç
            output_path = filedialog.asksaveasfilename(
                defaultextension=".gif",
                filetypes=[("GIF dosyası", "*.gif")],
                initialdir=self.output_folder,
                title="GIF'i Kaydet"
            )

            if not output_path:
                return

            delay = int(self.delay_var.get() * 1000)  # milisaniyeye çevir
            paths = self.image_paths.copy()

            if self.random_order.get():
                random.shuffle(paths)

            frames = []
            for path in paths:
                img = Image.open(path)
                img = img.convert('RGBA')
                frames.append(img)

            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=delay,
                loop=0,
                optimize=True
            )

            self._save_settings()  # Ayarları kaydet
            messagebox.showinfo("Başarılı", f"GIF başarıyla oluşturuldu:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"GIF oluşturulurken hata oluştu:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernGIFCreator(root)
    root.mainloop()
