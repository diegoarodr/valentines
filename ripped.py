import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
import concurrent.futures

object_image, rip_texture, displayed_image = None, None, None

def process_image():
    global object_image, rip_texture, displayed_image

    object_path = object_entry.get()
    rip_path = rip_entry.get()

    if not object_path or not rip_path:
        status_label.config(text="Please select both object and rip texture images.")
        return

    try:
        object_image = cv2.imread(object_path, cv2.IMREAD_UNCHANGED)
        rip_texture = cv2.imread(rip_path, cv2.IMREAD_GRAYSCALE)

        if object_image is None or rip_texture is None:
            raise Exception("Error loading images. Check file paths.")

        rip_texture = cv2.bitwise_not(rip_texture)
        rip_texture = cv2.GaussianBlur(rip_texture, (5, 5), 0)

        alpha = object_image[:, :, 3]
        alpha_blurred = cv2.GaussianBlur(alpha, (5, 5), 0)
        _, border = cv2.threshold(alpha_blurred, 150, 255, cv2.THRESH_BINARY)

        def displace_pixels(y_range):
            local_image = object_image.copy()
            for y in y_range:
                for x in range(border.shape[1]):
                    if border[y, x] > 0:
                        displacement = rip_texture[y % rip_texture.shape[0], x % rip_texture.shape[1]] * strength_scale.get()

                        sobelx = cv2.Sobel(alpha, cv2.CV_64F, 1, 0, ksize=3)
                        sobely = cv2.Sobel(alpha, cv2.CV_64F, 0, 1, ksize=3)
                        magnitude = np.sqrt(sobelx**2 + sobely**2)
                        if magnitude[y, x] > 0:
                            normal_x = -sobely[y, x] / magnitude[y, x]
                            normal_y = sobelx[y, x] / magnitude[y, x]
                        else:
                            normal_x = 0
                            normal_y = 0

                        offset_x = int(round(x + displacement * normal_x))
                        offset_y = int(round(y + displacement * normal_y))

                        if 0 <= offset_x < local_image.shape[1] and 0 <= offset_y < local_image.shape[0]:
                            local_image[y, x] = local_image[offset_y, offset_x]
            return local_image

        start_time = time.time()
        num_threads = 8
        chunk_size = border.shape[0] // num_threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(displace_pixels, range(i * chunk_size, (i + 1) * chunk_size)) for i in range(num_threads)]
            if border.shape[0] % num_threads != 0:
                 futures.append(executor.submit(displace_pixels, range(num_threads * chunk_size, border.shape[0])))

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                object_image = future.result()

                progress = int((i + 1) / num_threads * 100)
                progress_bar["value"] = progress
                window.update_idletasks()

        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.2f} seconds")

        object_image_rgb = cv2.cvtColor(object_image, cv2.COLOR_BGRA2RGBA)
        pil_image = Image.fromarray(object_image_rgb)
        displayed_image = ImageTk.PhotoImage(pil_image)

        image_label.config(image=displayed_image)
        status_label.config(text="Image processed successfully!")

    except Exception as e:
        status_label.config(text=f"Error: {e}")
        progress_bar["value"] = 0


def browse_object():
    filepath = filedialog.askopenfilename()
    object_entry.delete(0, tk.END)
    object_entry.insert(0, filepath)


def browse_rip():
    filepath = filedialog.askopenfilename()
    rip_entry.delete(0, tk.END)
    rip_entry.insert(0, filepath)


window = tk.Tk()
window.title("Ripped Paper Effect")

object_label = tk.Label(window, text="Object Image:")
object_label.grid(row=0, column=0, padx=5, pady=5)

object_entry = tk.Entry(window, width=40)
object_entry.grid(row=0, column=1, padx=5, pady=5)

object_button = tk.Button(window, text="Browse", command=browse_object)
object_button.grid(row=0, column=2, padx=5, pady=5)

rip_label = tk.Label(window, text="Rip Texture:")
rip_label.grid(row=1, column=0, padx=5, pady=5)

rip_entry = tk.Entry(window, width=40)
rip_entry.grid(row=1, column=1, padx=5, pady=5)

rip_button = tk.Button(window, text="Browse", command=browse_rip)
rip_button.grid(row=1, column=2, padx=5, pady=5)

strength_label = tk.Label(window, text="Rip Strength:")
strength_label.grid(row=2, column=0, padx=5, pady=5)

strength_scale = tk.Scale(window, from_=1, to=30, orient=tk.HORIZONTAL)
strength_scale.set(10)
strength_scale.grid(row=2, column=1, padx=5, pady=5)

process_button = tk.Button(window, text="Process Image", command=process_image)
process_button.grid(row=3, column=0, columnspan=3, pady=10)

progress_bar = ttk.Progressbar(window, mode="determinate", length=200)
progress_bar.grid(row=4, column=0, columnspan=3, pady=(5, 10))

image_label = tk.Label(window)
image_label.grid(row=5, column=0, columnspan=3)

status_label = tk.Label(window, text="")
status_label.grid(row=6, column=0, columnspan=3, pady=(0, 5))

window.mainloop()