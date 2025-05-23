import os
import csv
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def select_video():
    path = filedialog.askopenfilename(filetypes=[("Fichiers vidéo", "*.mp4 *.mov *.avi *.mkv")])
    if path:
        video_path_var.set(path)

def select_csv():
    path = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv")])
    if path:
        csv_path_var.set(path)

def select_output_dir():
    path = filedialog.askdirectory()
    if path:
        output_dir_var.set(path)

def time_to_seconds(time_str, fps=50):
    parts = time_str.strip().split(':')
    if len(parts) != 3:
        raise ValueError(f"Format invalide : '{time_str}'. Attendu MM:SS:FF à {fps} FPS")
    m, s, f = parts
    m = int(m)
    s = int(s)
    f = int(f)
    return m * 60 + s + f / fps

def cut_videos():
    csv_path = csv_path_var.get()
    video_path = video_path_var.get()
    output_dir = output_dir_var.get()
    output_format = format_var.get()
    prefix = prefix_var.get().strip()
    extend_one_second = add_padding_var.get()  # ✅ CheckBox status

    if not all([csv_path, video_path, output_dir, output_format]):
        messagebox.showerror("Erreur", "Veuillez sélectionner tous les champs requis.")
        return

    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile, delimiter=';'))
            total = len(reader)
            progress_bar["maximum"] = total
            progress_bar["value"] = 0
            log_text.delete(1.0, tk.END)

            for i, row in enumerate(reader):
                clip_id = row['id']
                start_time = row['start_time']
                end_time = row['end_time']

                try:
                    start_seconds = time_to_seconds(start_time)
                    end_seconds = time_to_seconds(end_time)
                except ValueError as e:
                    log_text.insert(tk.END, f"[{i+1}/{total}] ❌ Erreur format temps pour {clip_id} : {e}\n")
                    continue

                # ✅ Ajouter 1s avant/après si activé
                if extend_one_second:
                    start_seconds = max(0, start_seconds - 1)
                    end_seconds += 1

                duration = end_seconds - start_seconds
                if duration <= 0:
                    log_text.insert(tk.END, f"[{i+1}/{total}] ⚠️ Durée invalide pour {clip_id} (start ≥ end)\n")
                    continue

                filename = f"{prefix}{clip_id}.{output_format}"
                output_file = os.path.join(output_dir, filename)

                cmd = [
                    'ffmpeg',
                    '-ss', str(start_seconds),
                    '-i', video_path,
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-preset', 'veryfast',
                    '-crf', '23',
                    '-c:a', 'aac',
                    output_file
                ]

                log_text.insert(tk.END, f"[{i+1}/{total}] 🎬 {filename} : {start_time} → {end_time} {'(+1s)' if extend_one_second else ''}\n")
                log_text.see(tk.END)
                root.update()

                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

                progress_bar["value"] = i + 1
                root.update()

        messagebox.showinfo("Succès", "Toutes les vidéos ont été découpées avec succès !")

    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue :\n{str(e)}")

# === Interface Graphique ===

root = tk.Tk()
root.title("Découpe Vidéo avec CSV (MM:SS:FF à 50 FPS)")
root.geometry("640x680")
root.resizable(False, False)

video_path_var = tk.StringVar()
csv_path_var = tk.StringVar()
output_dir_var = tk.StringVar()
format_var = tk.StringVar(value="mp4")
prefix_var = tk.StringVar()
add_padding_var = tk.BooleanVar(value=False)  # ✅ Ajout padding

# Fichier vidéo
tk.Label(root, text="Fichier vidéo d'entrée :").pack(anchor='w', padx=10, pady=(10, 0))
tk.Entry(root, textvariable=video_path_var, width=70).pack(padx=10)
tk.Button(root, text="Choisir...", command=select_video).pack(pady=5)

# Fichier CSV
tk.Label(root, text="Fichier CSV (séparateur ;) :").pack(anchor='w', padx=10)
tk.Entry(root, textvariable=csv_path_var, width=70).pack(padx=10)
tk.Button(root, text="Choisir...", command=select_csv).pack(pady=5)

# Dossier de sortie
tk.Label(root, text="Dossier de sortie :").pack(anchor='w', padx=10)
tk.Entry(root, textvariable=output_dir_var, width=70).pack(padx=10)
tk.Button(root, text="Choisir...", command=select_output_dir).pack(pady=5)

# Format de sortie
tk.Label(root, text="Format de sortie :").pack(anchor='w', padx=10, pady=(10, 0))
tk.OptionMenu(root, format_var, "mp4", "avi", "mov", "mkv").pack(padx=10)

# Préfixe
tk.Label(root, text="Préfixe pour le nom des fichiers :").pack(anchor='w', padx=10, pady=(10, 0))
tk.Entry(root, textvariable=prefix_var, width=30).pack(padx=10)

# ✅ Checkbox pour ajouter 1s avant/après
tk.Checkbutton(root, text="Ajouter 1 seconde avant et après chaque extrait", variable=add_padding_var).pack(pady=5)

# Bouton de découpe
tk.Button(root, text="Découper les vidéos", command=cut_videos, bg='green', fg='white', font=('Arial', 12, 'bold')).pack(pady=15)

# Barre de progression
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.pack(pady=10)

# Log
tk.Label(root, text="Journal des opérations :").pack(anchor='w', padx=10)
log_text = tk.Text(root, height=12, width=80)
log_text.pack(padx=10, pady=(0, 10))

root.mainloop()
