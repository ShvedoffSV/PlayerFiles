import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pygame
from datetime import timedelta
import os
from mutagen.mp3 import MP3
import pygetwindow as gw
import pyautogui
import threading
import time

# Ініціалізація Pygame
pygame.init()

# Глобальні змінні
rewind_interval = 100  # Інтервал перемотки у мілісекундах
rewind_increment = 5  # Кількість секунд перемотки при кожному кроці
initial_volume = 0.8  # Початковий рівень гучності
MIN_HEIGHT = 450  # Мінімальна висота вікна
MIN_WIDTH = 550   # Мінімальна ширина вікна
MAX_SIZE = 700    # Максимальний розмір (висота та ширина)
hotkeys_window = None  # Оголосити змінну заздалегідь
filename = None
track_length = 0
def choose_file():
    global filename
    filename = filedialog.askopenfilename()
    update_track_info()

def play_music():
    pygame.mixer.init(buffer=1024)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.set_volume(initial_volume)  # Задати початкову гучність
    pygame.mixer.music.play()
    update_track_info()

def play_playlist(playlist):
    for filename in playlist:
        pygame.mixer.init(buffer=1024)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(initial_volume)  # Задати початкову гучність
        pygame.mixer.music.play()
        update_track_info()

def decrease_volume():
    global initial_volume
    current_volume = pygame.mixer.music.get_volume()
    if current_volume >= 0.1:
        initial_volume = max(0.0, initial_volume - 0.1)
        pygame.mixer.music.set_volume(initial_volume)
    else:
        pygame.mixer.music.set_volume(0.0)  # Гарантуємо, що гучність не буде меншою за 0.0
def stop_music():
    pygame.mixer.music.stop()
    update_track_info()

def change_volume(amount):
    current_volume = pygame.mixer.music.get_volume()
    new_volume = min(1.0, max(0.0, current_volume + amount))
    pygame.mixer.music.set_volume(new_volume)
    volume_percent = int(new_volume * 100)  # Переведення відсотків у ціле число
    volume_label.config(text=f"Рівень гучності: {volume_percent}%")

is_rewinding = False
def rewind_music(delta):
    global is_rewinding, track_length
    if is_rewinding:
        return  # Якщо вже відбувається перемотка, вийти з функції
    is_rewinding = True
    if pygame.mixer.music.get_busy():  # Перевірка, чи відтворюється музика
        current_pos = pygame.mixer.music.get_pos() / 1000  # Поточна позиція в секундах
        new_pos = max(0, min(track_length, current_pos + delta))  # Нова позиція в межах треку
        pygame.mixer.music.rewind()  # Перемотування на початок
        pygame.mixer.music.set_pos(new_pos)  # Встановлення нової позиції
        # Оновлення значення тривалості треку
        track_length -= delta
        if track_length < 0:
            track_length = 0
        track_length_str = str(timedelta(seconds=round(track_length)))
        track_info_label.config(text=f"Довжина треку: {track_length_str}")  # Оновлення мітки з тривалістю треку
    else:
        print("Музика не відтворюється")
    is_rewinding = False  # Повернути значення is_rewinding в False після завершення перемотки

music_paused = False
def pause_resume_music():
    global music_paused
    if music_paused:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()
    music_paused = not music_paused
    update_track_info()

# Прив'язка подій клавіш до функцій
def key(event):
    if event.keysym == 'space':
        play_music()
    elif event.keysym == 'Escape':
        stop_music()
    elif event.keysym == 'Up':
        change_volume(0.03)
    elif event.keysym == 'Down':
        change_volume(-0.03)
    elif event.keysym == 'p':
        pause_resume_music()
    elif event.keysym == 'i':
        toggle_hotkeys_info()
    elif event.keysym == 'o':
        choose_file()

def update_track_info():
    global track_length
    # Перевірка, чи вибрано файл
    if not filename:
        return

    # Отримання інформації про трек
    is_playing = pygame.mixer.music.get_busy()

    # Отримання назви треку
    track_name = os.path.splitext(os.path.basename(filename))[0]

    # Оновлення мітки з інформацією про трек
    if is_playing:
        current_pos = pygame.mixer.music.get_pos() / 1000
        remaining_time = track_length - current_pos
        remaining_time_str = str(timedelta(seconds=round(remaining_time)))
        track_info_label.config(text=f"Довжина треку: {remaining_time_str}")
    else:
        track_length_str = str(timedelta(seconds=round(track_length)))
        track_info_label.config(text=f"Довжина треку: {track_length_str}")

    track_name_label.config(text=f"Назва треку: {track_name}")

    # Оновлення позиції повзунка
    if track_length > 0:
        current_pos = pygame.mixer.music.get_pos() / 1000
        position_slider.config(to=track_length)
        position_slider.set(current_pos)

def choose_file():
    global filename, track_length
    filename = filedialog.askopenfilename()
    track_length = MP3(filename).info.length
    update_track_info()

def set_position(position):
    # Зміна позиції відтворення відповідно до значення повзунка
    position = float(position)
    pygame.mixer.music.set_pos(position)

# Функція для обмеження розміру вікна за висотою і шириною
def enforce_min_max_size(event):
    current_width = root.winfo_width()
    current_height = root.winfo_height()

    # Обмеження за висотою
    if current_height < MIN_HEIGHT:
        root.geometry(f"{current_width}x{MIN_HEIGHT}")
    elif current_height > MAX_SIZE:
        root.geometry(f"{current_width}x{MAX_SIZE}")

    # Обмеження за шириною
    if current_width < MIN_WIDTH:
        root.geometry(f"{MIN_WIDTH}x{current_height}")
    elif current_width > MAX_SIZE:
        root.geometry(f"{MAX_SIZE}x{current_height}")

def toggle_hotkeys_info():
    global hotkeys_window

    if hotkeys_window:
        if hotkeys_window.winfo_exists():
            hotkeys_window.destroy()  # Закрити вікно, якщо воно існує
            hotkeys_window = None  # Позначити, що вікно більше не існує
    else:
        hotkeys_window = tk.Toplevel(root)
        hotkeys_window.title("Інформація HotKeys")

        # Отримання рекомендованого розміру віджета Label
        label_width = 300
        label_height = 250

        # Отримання розміру головного вікна
        root_width = root.winfo_width()
        root_height = root.winfo_height()

        # Обчислення позиції для відображення вікна інформації про гарячі клавіші
        info_x = root.winfo_rootx() + root_width + 10
        info_y = root.winfo_rooty()

        # Задання розміру та позиції вікна
        hotkeys_window.geometry(f"{label_width}x{label_height}+{info_x}+{info_y}")
        hotkeys_window.resizable(False, False)

        # Додавання елементу Label з описом гарячих клавіш
        hotkeys_info = """
        Гарячі клавіші:
        O - Вибрати файли
        Пробіл - Відтворити/Призупинити відтворення
        Escape - Зупинити відтворення
        Up Arrow - Збільшити гучність
        Down Arrow - Зменшити гучність
        Right Arrow - Перемотати вперед
        Left Arrow - Перемотати назад
        P - Пауза/Старт
        I - Інформація...

        ***
        Вітання Алусику, Олежику та Андрійчику! ))
        ***
        """
        info_label = tk.Label(hotkeys_window, text=hotkeys_info)
        info_label.pack()

# Функція для вибору плейлисту
def choose_playlist():
    playlist = filedialog.askopenfilenames()
    if playlist:
        play_playlist(playlist)

# Створення графічного інтерфейсу
root = tk.Tk()
root.title("Музичний плеєр_alpha")
root.configure(bg="grey")  # Встановлення чорного фону для вікна

# Прив'язка функції до події зміни розміру вікна
root.bind("<Configure>", enforce_min_max_size)
root.resizable(True, True)  # Заборона зміни розміру вікна

# Кнопки для вибору файлу та управління відтворенням музики
# Визначення стилю для кнопок
style = ttk.Style()

# Встановлення властивостей стилю
style.configure('Custom.TButton', foreground='black', background='yellow', bordercolor='yellow')

# Створення кнопок з використанням визначеного стилю
choose_button = ttk.Button(root, text="Вибрати файли", command=choose_file, style='Custom.TButton', takefocus=0)
play_button = ttk.Button(root, text="Відтворити", command=play_music, style='Custom.TButton', takefocus=0)
pause_button = ttk.Button(root, text="Пауза/Старт", command=pause_resume_music, style='Custom.TButton', takefocus=0)
stop_button = ttk.Button(root, text="Стоп", command=stop_music, style='Custom.TButton', takefocus=0)
vup_button = ttk.Button(root, text="+", command=lambda: change_volume(0.02), style='Custom.TButton', takefocus=0)
vdown_button = ttk.Button(root, text="-", command=lambda: change_volume(-0.02), style='Custom.TButton', takefocus=0)
# Створення кнопки для виклику вікна з описом гарячих клавіш
hotkeys_button = ttk.Button(root, text="і...", command=toggle_hotkeys_info, style='Custom.TButton', takefocus=0)
# Призначення кнопки для вибору плейлисту
playlist_button = ttk.Button(root, text="Вибрати плейлист", command=choose_playlist, style='Custom.TButton', takefocus=0)

# Розміщення кнопок на графічному інтерфейсі
choose_button.grid(row=0, pady=10)
play_button.grid(row=1, pady=5)
pause_button.grid(row=2, pady=10)
stop_button.grid(row=3, pady=5)
vup_button.grid(row=0, column=1, padx=10, pady=10)
vdown_button.grid(row=1, column=1, padx=10, pady=10)
hotkeys_button.grid(row=2, column=1, pady=5)
playlist_button.grid(row=10, pady=10)

# Мітка для відображення інформації про трек
track_info_label = tk.Label(root, text="Тривалість треку: --:--:--")
track_info_label.grid(row=4, pady=5)

# Створення мітки для відображення назви треку
track_name_label = tk.Label(root, text="Назва треку: ---")
track_name_label.grid(row=5, pady=5)

# Створення мітки для відображення рівня гучності
volume_label = tk.Label(root, text="Рівень гучності: 80%")
volume_label.grid(row=6, pady=5)

# Створення повзунка для відтворення треку
position_slider = tk.Scale(root, from_=0, to=track_length, orient=tk.HORIZONTAL, length=200, command=set_position)
position_slider.grid(row=7, pady=10)

# Прив'язка клавіш зі стрілками до функцій перемотки
root.bind('<Key>', key)

# Прив'язка подій клавіш до функцій
root.mainloop()
