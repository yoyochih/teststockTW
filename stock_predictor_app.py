import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import base64
import requests

class StockPredictorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("台股明日報酬率預測器")
        self.geometry("800x600")

        self.label = tk.Label(self, text="輸入台股代碼 (例如 2330.TW):")
        self.label.pack(pady=10)

        self.entry = tk.Entry(self, width=20)
        self.entry.pack(pady=5)
        self.entry.insert(0, "2330.TW")

        self.btn = tk.Button(self, text="預測", command=self.predict)
        self.btn.pack(pady=10)

        self.result_label = tk.Label(self, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

        self.canvas_return = tk.Canvas(self, width=700, height=200)
        self.canvas_return.pack()
        self.canvas_price = tk.Canvas(self, width=700, height=200)
        self.canvas_price.pack()

    def predict(self):
        ticker = self.entry.get().strip()
        if not ticker:
            messagebox.showerror("錯誤", "請輸入股票代碼")
            return

        url = f"http://127.0.0.1:5000/api/predict?ticker={ticker}"
        try:
            response = requests.get(url)
            data = response.json()
            if "error" in data:
                messagebox.showerror("API 錯誤", data["error"])
                return

            self.result_label.config(text=data['message'])

            self.show_image(data['charts']['return_chart'], self.canvas_return)
            self.show_image(data['charts']['price_chart'], self.canvas_price)

        except Exception as e:
            messagebox.showerror("錯誤", str(e))

    def show_image(self, b64str, canvas):
        img_data = b64str.split(",")[1]
        img = Image.open(io.BytesIO(base64.b64decode(img_data)))
        img = img.resize((700, 200))
        self.photo = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor="nw", image=self.photo)
        canvas.image = self.photo  # 防止被回收

if __name__ == "__main__":
    app = StockPredictorApp()
    app.mainloop()
