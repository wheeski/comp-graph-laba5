import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.messagebox import showinfo
import colorsys


class PixelTransformation:
    def __init__(self, root):
        self.root = root
        self.root.title("Преобразование изображений")
        self.root.geometry("1500x800")
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.f1 = tk.Frame(root, width=500, height=500, relief="solid", bg="white")
        self.f1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.f1.pack_propagate(False)
        self.f2 = tk.Frame(root, width=500, height=500, relief="solid", bg="white")
        self.f2.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.f2.pack_propagate(False)
        self.f3 = tk.Frame(root, width=500, height=500, relief="solid", bg="white")
        self.f3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.f3.pack_propagate(False)
        self.f4 = tk.Frame(root, width=500, height=500, relief="solid", bg="white")
        self.f4.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        self.f4.pack_propagate(False)

        self.frame1 = tk.Label(self.f1, bg="black", borderwidth=0, highlightthickness=0)
        self.frame1.pack(fill=tk.BOTH, expand=True)
        self.frame1.bind("<Configure>", self.refresh_preview)
        self.frame2 = tk.Label(self.f2, bg="black", borderwidth=0, highlightthickness=0)
        self.frame2.pack(fill=tk.BOTH, expand=True)
        self.frame2.bind("<Configure>", self.refresh_preview)
        self.frame3 = tk.Label(self.f3, bg="black", borderwidth=0, highlightthickness=0)
        self.frame3.pack(fill=tk.BOTH, expand=True)
        self.frame3.bind("<Configure>", self.refresh_preview)
        self.frame4 = tk.Label(self.f4, bg="black", borderwidth=0, highlightthickness=0)
        self.frame4.pack(fill=tk.BOTH, expand=True)
        self.frame4.bind("<Configure>", self.refresh_preview)

        self.control_frame1 = ttk.Frame(root)
        self.control_frame1.grid(row=0, column=1, padx=20, pady=20)
        ttk.Button(self.control_frame1, text="Открыть 1 фото", command=self.open_first_image).pack(pady=5)
        ttk.Button(self.control_frame1, text="Преобразовать", command=self.increase_saturation).pack(pady=5)
        ttk.Button(self.control_frame1, text="Сохранить", command=lambda: self.save_result("saturation")).pack(pady=5)

        self.control_frame2 = ttk.Frame(root)
        self.control_frame2.grid(row=1, column=1, padx=20, pady=20)
        ttk.Button(self.control_frame2, text="Открыть 2 фото", command=self.open_second_image).pack(pady=5)
        ttk.Button(self.control_frame2, text="Наложить", command=self.transparency).pack(pady=5)
        ttk.Button(self.control_frame2, text="Сохранить", command=lambda: self.save_result("overlay")).pack(pady=5)

        self.img1 = None
        self.img_bytes1 = None
        self.img2 = None
        self.img_bytes2 = None
        self.saturation_result = None
        self.overlay_result = None

    def open_first_image(self):
        file_path = self.open_image()
        if not file_path:
            return
        image = tk.PhotoImage(file=file_path)
        self.img1 = image
        self.img_bytes1 = self.get_file_bytes(file_path)
        self.display_image(self.frame1, *self.img_bytes1)

    def open_second_image(self):
        file_path = self.open_image()
        if not file_path:
            return
        image = tk.PhotoImage(file=file_path)
        self.img2 = image
        self.img_bytes2 = self.get_file_bytes(file_path)
        self.display_image(self.frame3, *self.img_bytes2)

    def open_image(self):
        return filedialog.askopenfilename(
            title="Выберите PPM файл",
            filetypes=[("PPM files", "*.ppm"), ("All files", "*.*")]
        )

    def get_file_bytes(self, file_path):
        with open(file_path, 'rb') as f:
            signature = f.readline().strip()
            if signature != b'P6':
                raise ValueError("Это не PPM файл")
            width, height = f.readline().split()
            width, height = int(width), int(height)
            f.readline()
            blist = list(bytearray(f.read()))
        return width, height, blist

    def increase_saturation(self):
        """Увеличение насыщенности на 30% у точек с яркостью меньше 50%"""
        if not self.img_bytes1:
            showinfo("Ошибка", "Сначала откройте первое изображение")
            return

        width, height, pixels = self.img_bytes1
        new_pixels = bytearray()

        for i in range(0, len(pixels), 3):
            r, g, b = pixels[i], pixels[i + 1], pixels[i + 2]

            # Увеличение насыщенности на 30% при яркости меньше 50%
            h, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if value < 0.5:
                red, green, blue = colorsys.hsv_to_rgb(h, min(1.0, saturation * 3), value)
                new_pixels.extend([round(red * 255), round(green * 255), round(blue * 255)])
            else:
                new_pixels.extend([r, g, b])

        self.saturation_result = self.create_photoimage_from_bytes(width, height, new_pixels)
        self.display_image(self.frame2, width, height, new_pixels)

    def transparency(self):
        """Наложение с прозрачностью 50%"""
        if not self.img_bytes1 or not self.img_bytes2:
            showinfo("Ошибка", "Недостаточно изображений")
            return

        width1, height1, pixels1 = self.img_bytes1
        width2, height2, pixels2 = self.img_bytes2

        # Пропорции холста совпадают с окошком результата. Разрешение
        # выбираем по оригиналам, чтобы не сохранять маленький предпросмотр.
        box_width = max(1, self.frame4.winfo_width())
        box_height = max(1, self.frame4.winfo_height())
        resolution = max(width1 / box_width, height1 / box_height,
                         width2 / box_width, height2 / box_height)
        width = max(1, round(box_width * resolution))
        height = max(1, round(box_height * resolution))
        fitted1 = self.fit_to_canvas(width1, height1, pixels1, width, height)
        fitted2 = self.fit_to_canvas(width2, height2, pixels2, width, height)
        # Прозрачность 50%, включая чёрные полосы общего холста.
        new_pixels = bytearray((a + b) // 2 for a, b in zip(fitted1, fitted2))

        self.overlay_result = self.create_photoimage_from_bytes(width, height, new_pixels)
        self.display_image(self.frame4, width, height, new_pixels)

    def fit_to_canvas(self, width, height, pixels, canvas_width, canvas_height):
        """Вписать изображение целиком по центру, заполнив поля чёрным."""
        scale = min(canvas_width / width, canvas_height / height)
        fitted_width = max(1, min(canvas_width, round(width * scale)))
        fitted_height = max(1, min(canvas_height, round(height * scale)))
        offset_x = (canvas_width - fitted_width) // 2
        offset_y = (canvas_height - fitted_height) // 2
        result = bytearray(canvas_width * canvas_height * 3)
        for y in range(fitted_height):
            source_y = min(height - 1, int((y + 0.5) * height / fitted_height))
            for x in range(fitted_width):
                source_x = min(width - 1, int((x + 0.5) * width / fitted_width))
                source_index = (source_y * width + source_x) * 3
                target_index = ((y + offset_y) * canvas_width + x + offset_x) * 3
                result[target_index:target_index + 3] = bytes(pixels[source_index:source_index + 3])
        return result

    def display_image(self, target, width, height, pixels):
        """Храним оригинал отдельно от уменьшенной копии для просмотра."""
        target.preview_source = (width, height, bytes(pixels))
        self.refresh_preview(target=target)

    def refresh_preview(self, event=None, target=None):
        if target is None:
            target = event.widget
        source = getattr(target, "preview_source", None)
        if source is None:
            return
        width, height, pixels = source
        available_width = max(1, target.winfo_width())
        available_height = max(1, target.winfo_height())
        scale = min(1.0, available_width / width, available_height / height)
        preview_width = max(1, int(width * scale))
        preview_height = max(1, int(height * scale))
        # Масштабируем только предпросмотр, сохраняя пропорции.
        preview = bytearray()
        for y in range(preview_height):
            source_y = min(height - 1, int((y + 0.5) * height / preview_height))
            for x in range(preview_width):
                source_x = min(width - 1, int((x + 0.5) * width / preview_width))
                index = (source_y * width + source_x) * 3
                preview.extend(pixels[index:index + 3])
        data = self.create_photoimage_from_bytes(preview_width, preview_height, preview)
        image = tk.PhotoImage(data=data, format="PPM")
        target.config(image=image, anchor="center")
        target.image = image

    def create_photoimage_from_bytes(self, width, height, pixels):
        ppm_header = f"P6\n{width} {height}\n255\n".encode()
        result = ppm_header + pixels
        return result

    def save_result(self, mode="saturation"):
        data = None
        if mode == "saturation":
            data = self.saturation_result
            if not data:
                showinfo("Ошибка", "Нет результата преобразования насыщенности для сохранения")
                return
        elif mode == "overlay":
            data = self.overlay_result
            if not data:
                showinfo("Ошибка", "Нет результата наложения для сохранения")
                return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".ppm",
            filetypes=[("PPM files", "*.ppm"), ("All files", "*.*")],
            title="Сохранить результат"
        )
        if not file_path:
            return
        with open(file_path, 'wb') as f:
            f.write(data)
        showinfo("Успех", f"Изображение сохранено в {file_path}")


def main():
    root = tk.Tk()
    pt = PixelTransformation(root)
    root.mainloop()


if __name__ == '__main__':
    main()
