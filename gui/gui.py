import json
import logging
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection

LAYER_COLORS = {
    "M1": "#1f77b4",
    "M2": "#d62728",
    "M3": "#2ca02c",
    "M4": "#9467bd",
    "VIA": "#ff7f0e",
}
DEFAULT_COLOR = "#7f7f7f"
NET_COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf"]
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"


class TkLogHandler(logging.Handler):
    def __init__(self, widget: tk.Text):
        super().__init__()
        self.widget = widget

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self.widget.after(0, self._append, message)

    def _append(self, message: str) -> None:
        self.widget.configure(state="normal")
        self.widget.insert("end", f"{message}\n")
        self.widget.see("end")
        self.widget.configure(state="disabled")


class SteinerTreeViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Steiner Tree Viewer")
        self.geometry("1600x900")
        self.minsize(800, 550)
        self.current_file: Path | None = None
        self.data: dict | list | None = None

        self._create_menu()
        self._create_layout()
        self._configure_logging()
        self._log("Выберите JSON-файл с деревом.")

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Открыть JSON...", command=self.open_json, accelerator="Ctrl+O")
        file_menu.add_command(label="Перерисовать", command=self.draw_tree, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.destroy, accelerator="Ctrl+Q")
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        view_menu = tk.Menu(menu_bar, tearoff=False)
        view_menu.add_command(label="Очистить логи", command=self.clear_logs)
        menu_bar.add_cascade(label="Вид", menu=view_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="О программе", command=self.show_about)
        menu_bar.add_cascade(label="Справка", menu=help_menu)
        self.config(menu=menu_bar)

        self.bind_all("<Control-o>", lambda _: self.open_json())
        self.bind_all("<F5>", lambda _: self.draw_tree())
        self.bind_all("<Control-q>", lambda _: self.destroy())

    def _create_layout(self) -> None:
        main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        chart_frame = ttk.Frame(main_pane, padding=6)
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        toolbar = NavigationToolbar2Tk(self.canvas, chart_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(fill=tk.X)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        main_pane.add(chart_frame, weight=4)

        log_frame = ttk.LabelFrame(main_pane, text="Логи", padding=6)
        self.log_text = tk.Text(log_frame, height=9, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_pane.add(log_frame, weight=1)

    def _configure_logging(self) -> None:
        self.logger = logging.getLogger("steiner_viewer")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        handler = TkLogHandler(self.log_text)
        handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)s  %(message)s", "%H:%M:%S"))
        self.logger.addHandler(handler)

    def _log(self, message: str) -> None:
        self.logger.info(message)

    def open_json(self) -> None:
        filename = filedialog.askopenfilename(
            title="Открыть результат построения",
            initialdir=OUTPUT_DIR,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if filename:
            self.load_json(Path(filename))

    def load_json(self, file_path: Path) -> None:
        try:
            with file_path.open("r", encoding="utf-8") as source:
                data = json.load(source)
            nets = data.get("nets") if isinstance(data, dict) else data
            if not isinstance(nets, list):
                raise ValueError("ожидается объект с массивом 'nets' или массив сетей")
        except (OSError, json.JSONDecodeError, ValueError) as error:
            self._log(f"Не удалось загрузить {file_path.name}: {error}")
            messagebox.showerror("Ошибка загрузки", f"Не удалось прочитать JSON-файл:\n{error}")
            return

        self.current_file = file_path
        self.data = data
        self.title(f"Steiner Tree Viewer — {file_path.name}")
        self._log(f"Загружен файл {file_path.name}: сетей {len(nets)}.")
        self.draw_tree()

    def draw_tree(self) -> None:
        self.axes.clear()
        if self.data is None:
            self.axes.set_title("Откройте JSON-файл с деревом")
            self.canvas.draw_idle()
            return

        nets = self.data.get("nets", []) if isinstance(self.data, dict) else self.data
        segments: list[list[tuple[float, float]]] = []
        colors: list[str] = []
        points: set[tuple[float, float]] = set()
        labels: list[tuple[float, float, str]] = []

        for net_index, net in enumerate(nets):
            net_id = str(net.get("net_id", f"N{net_index + 1}"))
            color = NET_COLORS[net_index % len(NET_COLORS)]
            for edge in net.get("edges", []):
                try:
                    start, end = edge["from"], edge["to"]
                    x1, y1 = float(start["x"]), float(start["y"])
                    x2, y2 = float(end["x"]), float(end["y"])
                except (KeyError, TypeError, ValueError):
                    self._log(f"Сеть {net_id}: пропущено ребро с некорректными координатами.")
                    continue
                segments.append([(x1, y1), (x2, y2)])
                colors.append(color)
                points.update(((x1, y1), (x2, y2)))
            labels.append(((x1 + x2) / 2 + 5, (y1 + y2) / 2 + 5, net_id))

        if segments:
            self.axes.add_collection(LineCollection(segments, colors=colors, linewidths=2.2))
            xs, ys = zip(*points)
            self.axes.scatter(xs, ys, color="#202020", s=18, zorder=3)
            for x, y, net_id in labels:
                self.axes.annotate(net_id, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8, color="#333333")
            self.axes.autoscale()
            self.axes.margins(0.08)
            self._log(f"Отрисовано рёбер: {len(segments)}.")
        else:
            self.axes.text(0.5, 0.5, "В JSON нет рёбер для отображения", ha="center", va="center", transform=self.axes.transAxes)
            self._log("Рёбра для отображения не найдены.")

        self.axes.set_title("Дерево Штейнера")
        self.axes.set_xlabel("X")
        self.axes.set_ylabel("Y")
        self.axes.grid(True, linestyle="--", alpha=0.35)
        self.axes.set_aspect("equal", adjustable="box")
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def clear_logs(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def show_about(self) -> None:
        messagebox.showinfo("О программе", "Steiner Tree Viewer\nПросмотр JSON-результатов из папки output.")


if __name__ == "__main__":
    SteinerTreeViewer().mainloop()

        