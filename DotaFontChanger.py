import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
import datetime
import traceback
import subprocess
import sys
import random

# Константы
DOTA_PATH_FILE = "dotaPath.txt"
LOGS_DIR = "logs"
OUT_FONT_NAME = "radiance-light.otf"
CONF_NAME = "42-repl-global.conf"
FORCE_FAMILY = "Feereeks Font"

shnyaga = ["Прочитал - 25 ммр залутал", "Прочитал - хуй отсосал", "Прочитал - молодец", "Прочитал - лузстрик поймал", 
"Прочитал - я ничего не придумал", "Я уже так заебался тут что-то придумывать", "Эээээээээээээээээээ"]

class DotaFontInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title(random.choice(shnyaga))
        self.root.geometry("500x630")
        self.root.resizable(False, False)

        # Переменные
        self.dota_path = tk.StringVar()
        self.font_file_path = tk.StringVar()
        self.scale_percent_letters = tk.StringVar(value="100")
        self.scale_percent_numbers = tk.StringVar(value="100")
        self.gen_lowercase = tk.BooleanVar(value=False)
        self.lowercase_reduction = tk.StringVar(value="20")

        os.makedirs(LOGS_DIR, exist_ok=True)

        self.load_saved_path()
        self.build_ui()

    def load_saved_path(self):
        if os.path.exists(DOTA_PATH_FILE):
            try:
                with open(DOTA_PATH_FILE, "r", encoding="utf-8") as f:
                    p = f.read().strip()
                if p and os.path.exists(p):
                    self.dota_path.set(p)
            except: pass

    def build_ui(self):
        main = tk.Frame(self.root, padx=20, pady=10)
        main.pack(fill="both", expand=True)

        tk.Label(main, text="DotaFontChanger (by фирикс)", font=("Arial", 16, "bold")).pack(pady=(0,15))

        # Чел указывает путь к дотке
        tk.Label(main, text="Путь к папке 'dota 2 beta':").pack(anchor="w")
        pframe = tk.Frame(main); pframe.pack(fill="x", pady=5)
        tk.Entry(pframe, textvariable=self.dota_path, width=63).pack(side="left", padx=(0,5))
        tk.Button(pframe, text="Папка", width=10, command=self.browse_dota).pack(side="left")

        # Чел указывает путь к шрифту
        tk.Label(main, text="Путь к шрифту (TTF/OTF):").pack(anchor="w", pady=(5,0))
        fframe = tk.Frame(main); fframe.pack(fill="x", pady=5)
        tk.Entry(fframe, textvariable=self.font_file_path, width=63).pack(side="left", padx=(0,5))
        tk.Button(fframe, text="Файлик", width=10, command=self.browse_font).pack(side="left")

        # Масштабированние
        scale_box = tk.LabelFrame(main, text="Масштаб шрифта", padx=10, pady=5)
        scale_box.pack(fill="x", pady=5)
        
        row1 = tk.Frame(scale_box); row1.pack(fill="x", pady=2)
        tk.Label(row1, text="Буквы (%):", width=9, anchor="w").pack(side="left")
        tk.Entry(row1, textvariable=self.scale_percent_letters, width=5).pack(side="left")
        
        row2 = tk.Frame(scale_box); row2.pack(fill="x", pady=2)
        tk.Label(row2, text="Цифры/Спецсимволы (%):", width=22, anchor="w").pack(side="left")
        tk.Entry(row2, textvariable=self.scale_percent_numbers, width=5).pack(side="left")

        # Заглавные в строчные
        sc_box = tk.LabelFrame(main, text="Юзайте только тогда, когда в шрифте нету маленьких букв, а всё капсом", padx=10, pady=10)
        sc_box.pack(fill="x", pady=1)
        
        tk.Checkbutton(sc_box, text="Сгенерировать маленькие буквы", variable=self.gen_lowercase).pack(anchor="w")
        
        row3 = tk.Frame(sc_box); row3.pack(fill="x", pady=3)
        tk.Label(row3, text="Уменьшить маленькие буквы относительно больших на (%):").pack(side="left")
        tk.Entry(row3, textvariable=self.lowercase_reduction, width=5).pack(side="left", padx=10)
        tk.Label(sc_box, text="(Пример: 20% значит, что маленькие буквы будут 80% от размера больших)", font=("Arial", 8), fg="gray").pack(anchor="w")

        # БОЛЬШАЯ КРУТАЯ КНОПКА ХАХАХАХА
        tk.Button(main, text="УСТАНОВИТЬ ШРИФТ ( ДАДАДА ТЫКАЙ СЮДА )", bg="#1164B4", fg="white", font=("Arial", 13, "bold"),
                command=self.run_process, height=2).pack(fill="x", pady=5)

        # Приколы 
        ctrl_frame = tk.LabelFrame(main, text="Приколы :D", padx=10, pady=10)
        ctrl_frame.pack(fill="x", pady=10)
        
        # Сеточка родная
        ctrl_frame.columnconfigure(0, weight=1)
        ctrl_frame.columnconfigure(1, weight=1)

        # Ряд 1
        tk.Button(ctrl_frame, text="ЗАПУСТИТЬ дотку2", height=2, bg="#44944A", fg="white", 
                font=("Arial", 10, "bold"), command=self.run_dota).grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
                
        tk.Button(ctrl_frame, text="УБИТЬ дотку2", height=2, bg="#960018", fg="white", 
                font=("Arial", 10, "bold"), command=self.kill_dota).grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Ряд 2
        tk.Button(ctrl_frame, text="СДЕЛАТЬ бекап", height=2, bg="white", fg="black", 
                font=("Arial", 10, "bold"), relief="solid", borderwidth=1, command=self.create_backup).grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        tk.Button(ctrl_frame, text="ОТКАТИТЬ всё", height=2, bg="white", fg="black", 
                font=("Arial", 10, "bold"), relief="solid", borderwidth=1, command=self.restore_backup).grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.status = tk.Label(self.root, text="Hello World! Ver. : 1.0 (Realese)", bd=1, relief="sunken", anchor="w")

        self.status.pack(side="bottom", fill="y") 

    def browse_dota(self):
        f = filedialog.askdirectory(); 
        if f: self.dota_path.set(f)
    
    def browse_font(self):
        f = filedialog.askopenfilename(filetypes=[("Fonts", "*.ttf *.otf")]); 
        if f: self.font_file_path.set(f)

    def kill_dota(self):
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/IM", "dota2.exe"], check=False)
            else:
                subprocess.run(["pkill", "-9", "dota2"], check=False)
            messagebox.showinfo("УСПЕХ!!!", "Дота2 удалена с вашего компютера")
        except Exception as e:
            messagebox.showerror("Вот блин(", f"Не удалось удалить доту2. Ошибка: {e}")

    def run_dota(self):
        try:
            if sys.platform == "win32":
                os.startfile("steam://rungameid/570")
            else:
                subprocess.Popen(["xdg-open", "steam://rungameid/570"])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить доту2: {e}")

    def create_backup(self):
        """Создать бекап ТЕКУЩЕГО шрифта Dota"""
        dota = self.dota_path.get()
        if not dota:
            messagebox.showwarning("Ошибка", "Укажи путь к Dota 2")
            return
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = os.path.join(os.getcwd(), "manual-backups", timestamp)
            os.makedirs(backup_folder, exist_ok=True)
            
            font_src = os.path.join(dota, "game/dota/panorama/fonts", OUT_FONT_NAME)
            conf_src = os.path.join(dota, "game/core/panorama/fonts/conf.d", CONF_NAME)
            
            if os.path.exists(font_src):
                shutil.copy2(font_src, os.path.join(backup_folder, OUT_FONT_NAME))
            if os.path.exists(conf_src):
                shutil.copy2(conf_src, os.path.join(backup_folder, CONF_NAME))
            
            messagebox.showinfo("Опа", f"Бекап создан в папке:\nmanual-backups/{timestamp}")
        except Exception as e:
            messagebox.showerror("Не опа", f"Не удалось создать бекап: {e}")

    def restore_backup(self):
        """Восстановить шрифт из бекапа"""
        backup_root = os.path.join(os.getcwd(), "manual-backups")
        if not os.path.exists(backup_root):
            messagebox.showwarning("Ошибка", "Ты не сделал ни одного бекапа...")
            return
        
        # Найти последний бекап
        backups = [d for d in os.listdir(backup_root) if os.path.isdir(os.path.join(backup_root, d))]
        if not backups:
            messagebox.showwarning("Ошибка", "Ты не сделал ни одного бекапа...")
            return
        
        backups.sort(reverse=True)
        latest = backups[0]
        backup_folder = os.path.join(backup_root, latest)
        
        dota = self.dota_path.get()
        if not dota:
            messagebox.showwarning("Ошибка", "Укажи путь к дотке2")
            return
        
        try:
            font_src = os.path.join(backup_folder, OUT_FONT_NAME)
            conf_src = os.path.join(backup_folder, CONF_NAME)
            
            font_dst = os.path.join(dota, "game/dota/panorama/fonts", OUT_FONT_NAME)
            conf_dst = os.path.join(dota, "game/core/panorama/fonts/conf.d", CONF_NAME)
            
            if os.path.exists(font_src):
                shutil.copy2(font_src, font_dst)
            if os.path.exists(conf_src):
                shutil.copy2(conf_src, conf_dst)
            
            messagebox.showinfo("Готово", f"Восстановлен бекап {latest}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Код ошибки: {e}")

    def ensure_glyf_integrity(self, font):
        if 'hmtx' not in font: font['hmtx'] = newTable('hmtx')
        if 'glyf' not in font: 
            font['glyf'] = newTable('glyf')
            font['glyf'].glyphs = {}

    def scale_glyph_outline(self, font, glyph_name, scale):
        """Масштабирует outline глифа"""
        if 'glyf' not in font or not hasattr(font['glyf'], 'glyphs'):
            return
        
        try:
            glyph_set = font.getGlyphSet()
            pen = TTGlyphPen(glyph_set)
            t = Transform(scale, 0, 0, scale, 0, 0)
            tpen = TransformPen(pen, t)
            glyph_set[glyph_name].draw(tpen)
            font['glyf'].glyphs[glyph_name] = pen.glyph()
        except Exception as e:
            pass

    # Мейн часть / запуск всей хуйни
    def run_process(self):
        try:
            sc_letters = float(self.scale_percent_letters.get()) / 100.0
            sc_numbers = float(self.scale_percent_numbers.get()) / 100.0
            reduction = float(self.lowercase_reduction.get()) / 100.0
            
            dota = self.dota_path.get()
            font_path = self.font_file_path.get()
            
            if not dota or not font_path:
                messagebox.showerror("Ошибка", "Ты заполнил не все поля")
                return

            self.status.config(text="Обработка...")
            
            # Сохранение пути к дотке
            with open(DOTA_PATH_FILE, "w", encoding="utf-8") as f:
                f.write(dota)

            font = TTFont(font_path)
            self.ensure_glyf_integrity(font)
            
            cmap = font.getBestCmap()
            glyph_set = font.getGlyphSet()
            
            # Масштабирование
            for code, gname in cmap.items():
                scale = 1.0
                if (65 <= code <= 90) or (97 <= code <= 122) or (1040 <= code <= 1103):
                    scale = sc_letters
                elif (48 <= code <= 57) or (32 <= code <= 47) or (58 <= code <= 64):
                    scale = sc_numbers
                
                if abs(scale - 1.0) > 0.001:
                    self.scale_glyph_outline(font, gname, scale)
                    
                    w, lsb = font['hmtx'].metrics[gname]
                    font['hmtx'].metrics[gname] = (int(w * scale), int(lsb * scale))

            # Генерация маленьких букавок ня :3
            if self.gen_lowercase.get() and 'glyf' in font:
                ranges = [(65, 91, 32), (1040, 1072, 32)]
                for start, end, offset in ranges:
                    for up_code in range(start, end):
                        low_code = up_code + offset
                        up_name, low_name = cmap.get(up_code), cmap.get(low_code)
                        if up_name and low_name:
                            outline_scale = (1.0 - reduction)
                            pen = TTGlyphPen(glyph_set)
                            t = Transform(outline_scale, 0, 0, outline_scale, 0, 0)
                            tpen = TransformPen(pen, t)
                            glyph_set[up_name].draw(tpen)
                            font['glyf'].glyphs[low_name] = pen.glyph()
                            
                            up_w, up_lsb = font['hmtx'].metrics[up_name]
                            font['hmtx'].metrics[low_name] = (int(up_w * outline_scale), int(up_lsb * outline_scale))

            # ХАХАХХА ПОШЛО НАХУЙ ДЕФОЛТНОЕ СЕМЕЙСТВО ШРИФТА
            for name in font['name'].names:
                if name.nameID in [1, 4]:
                    font['name'].setName(FORCE_FAMILY, name.nameID, name.platformID, name.platEncID, name.langID)

            # Сохранение
            out_path = os.path.join(os.getcwd(), OUT_FONT_NAME)
            font.save(out_path)

            # Установка в папку доты
            font_dst_dir = os.path.join(dota, "game/dota/panorama/fonts")
            os.makedirs(font_dst_dir, exist_ok=True)
            orig_in_dota = os.path.join(font_dst_dir, OUT_FONT_NAME)
            
            shutil.copy2(out_path, orig_in_dota)
            
            # Создание кфг
            conf_dir = os.path.join(dota, "game/core/panorama/fonts/conf.d")
            os.makedirs(conf_dir, exist_ok=True)
            with open(os.path.join(conf_dir, CONF_NAME), "w", encoding="utf-8") as f:
                f.write(f"""<?xml version='1.0'?>
<!DOCTYPE fontconfig SYSTEM 'fonts.dtd'>
<fontconfig>

<match target=\"font\">
    <test name=\"family\">
        <string>Radiance</string>
    </test>
    <edit name=\"family\" mode=\"assign\">
        <string>{FORCE_FAMILY}</string>
    </edit>
</match>
<match target=\"pattern\">
    <test name=\"family\">
        <string>Radiance</string>
    </test>
    <edit name=\"family\" mode=\"prepend\" binding=\"strong\">
        <string>{FORCE_FAMILY}</string>
    </edit>
</match>
</fontconfig>""")

            self.status.config(text="Установлено (вроде)")
            messagebox.showinfo("Поздравляю", "Всё должно работать!")

        except Exception as e:
            messagebox.showerror("Ошибка", traceback.format_exc())

if __name__ == "__main__":
    root = tk.Tk()
    app = DotaFontInstaller(root)
    root.mainloop()