"""
Этот скрипт представляет собой простую графическую утилиту на основе tkinter для открытия изображений и
рисования на них прямоугольников с помощью мыши. Прямоугольники можно сохранять в JSON файл для последующего использования.

Класс RectangleDrawer создает пользовательский интерфейс, который позволяет:
- Открыть изображение для аннотации, используя кнопку "Open Image".
- Рисовать прямоугольники на изображении, удерживая левую кнопку мыши и перемещая курсор.
- Сохранять координаты нарисованных прямоугольников в файл 'rectangles.json' посредством кнопки "Save Rectangles".

Пользовательский интерфейс включает в себя:
- Кнопки для открытия изображения и сохранения данных.
- Холст для отображения и аннотации изображения.
- Полосы прокрутки для навигации по изображению.

Использование:
1. Запустить скрипт.
2. Используя кнопку "Open Image", открыть нужное изображение.
3. Нарисовать прямоугольники, удерживая левую кнопку мыши.
4. Сохранить прямоугольники с помощью кнопки "Save Rectangles".
"""


import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json

class RectangleDrawer:
    def __init__(self, master):
        self.master = master
        self.rect = None
        self.start_x = None
        self.start_y = None

        # Создаем фрейм для размещения холста и полос прокрутки
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Создаем холст внутри фрейма
        self.canvas = tk.Canvas(self.frame, bg='white')

        # Добавляем вертикальную полосу прокрутки
        self.v_scroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        # Добавляем горизонтальную полосу прокрутки
        self.h_scroll = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=self.canvas.xview)  # Изменено на master
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(xscrollcommand=self.h_scroll.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.open_button = tk.Button(master, text="Open Image", command=self.open_image)
        self.open_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(master, text="Save Rectangles", command=self.save_rectangles)
        self.save_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.image = Image.open(file_path)
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tkimage)
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))

    def on_click(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x+1, self.start_y+1, outline='red', tags=("rectangle",))

    def on_drag(self, event):
        curX, curY = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def save_rectangles(self):
        # Инициализируем новый список для хранения координат прямоугольников
        rectangles = []
        # Перебираем все элементы с тегом 'rectangle' на холсте
        for rect_id in self.canvas.find_withtag('rectangle'):
            # Получаем координаты текущего прямоугольника и добавляем в список
            rectangles.append(self.canvas.coords(rect_id))
        # Проверяем, что список координат не пуст
        if rectangles:
            # Сохраняем координаты прямоугольников в JSON-файл
            with open('rectangles.json', 'w') as f:
                json.dump(rectangles, f)
            print("Rectangles saved to rectangles.json")
        else:
            print("No rectangles to save.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Rectangle Drawer")
    rd = RectangleDrawer(root)
    root.mainloop()
