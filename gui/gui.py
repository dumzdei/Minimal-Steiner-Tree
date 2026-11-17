import json
import sys
from pathlib import Path
from typing import Any

if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parents[1]
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from validator.validator import validate

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from PyQt6.QtCore import QDir, QPoint, QProcess, Qt
from PyQt6.QtGui import QAction, QColor, QFileSystemModel, QFont, QIcon, QPainter, QPixmap, QPolygon, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULT_PATH = OUTPUT_DIR / "result.json"
PIPELINE_PATH = PROJECT_ROOT / "pipeline.py"
DEFAULT_EXECUTABLE = PROJECT_ROOT / ("SteinerTree.exe" if sys.platform == "win32" else "SteinerTree")
NET_COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf"]


class ResultWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.result_data: dict[str, Any] | list[Any] | None = None
        self.setWindowTitle("Результат — Steiner Tree")
        self.resize(900, 700)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        toolbar = NavigationToolbar2QT(self.canvas, self)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        self.setCentralWidget(content)
        self._draw_placeholder()

    def show_result(self, data: dict[str, Any] | list[Any]) -> None:
        self.result_data = data
        self.draw_result()
        self.show()
        self.raise_()
        self.activateWindow()

    def draw_result(self) -> None:
        self.axes.clear()
        if self.result_data is None:
            self._draw_placeholder()
            return
        nets = self.result_data.get("nets", []) if isinstance(self.result_data, dict) else self.result_data
        segments: list[list[tuple[float, float]]] = []
        colors: list[str] = []
        points: set[tuple[float, float]] = set()
        labels: list[tuple[float, float, str]] = []
        for index, net in enumerate(nets):
            if not isinstance(net, dict):
                continue
            net_id = str(net.get("net_id", f"N{index + 1}"))
            for edge in net.get("edges", []):
                try:
                    start, end = edge["from"], edge["to"]
                    x1, y1 = float(start["x"]), float(start["y"])
                    x2, y2 = float(end["x"]), float(end["y"])
                except (KeyError, TypeError, ValueError):
                    continue
                segments.append([(x1, y1), (x2, y2)])
                colors.append(NET_COLORS[index % len(NET_COLORS)])
                points.update(((x1, y1), (x2, y2)))
            labels.append(((x1 + x2) / 2, (y1 + y2) / 2, net_id))
        if segments:
            self.axes.add_collection(LineCollection(segments, colors=colors, linewidths=2.2))
            xs, ys = zip(*points)
            self.axes.scatter(xs, ys, color="#202020", s=20, zorder=3)
            for x, y, net_id in labels:
                self.axes.annotate(net_id, (x, y), xytext=(5, 5), textcoords="offset points", fontsize=9, color="#333333")
            self.axes.autoscale()
            self.axes.margins(0.08)
        else:
            self.axes.text(0.5, 0.5, "В JSON нет рёбер для отображения", ha="center", va="center", transform=self.axes.transAxes)
        self.axes.set_title("Дерево Штейнера")
        self.axes.set_xlabel("X")
        self.axes.set_ylabel("Y")
        self.axes.grid(True, linestyle="--", alpha=0.35)
        self.axes.set_aspect("equal", adjustable="box")
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _draw_placeholder(self) -> None:
        self.axes.clear()
        self.axes.text(0.5, 0.5, "Запустите расчёт, чтобы увидеть результат", ha="center", va="center", transform=self.axes.transAxes)
        self.axes.set_axis_off()
        self.canvas.draw_idle()


class SteinerTreeWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_input: Path | None = None
        self.input_editors: dict[QPlainTextEdit, Path] = {}
        self.result_data: dict[str, Any] | list[Any] | None = None
        self.result_window = ResultWindow(self)
        self.process: QProcess | None = None
        self.process_input: Path | None = None
        self.run_with_verification = False

        self.setWindowTitle("Steiner Tree")
        self.resize(1600, 950)
        self.setMinimumSize(1050, 650)
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_layout()
        self.setStatusBar(QStatusBar(self))
        self._log("Выберите JSON-файл.")

    def _create_actions(self) -> None:
        self.open_action = QAction("Открыть файл...", self, shortcut="Ctrl+O", triggered=self.open_input)
        self.save_action = QAction("Сохранить", self, shortcut="Ctrl+S", triggered=self.save_input)
        self.save_as_action = QAction("Сохранить как...", self, shortcut="Ctrl+Shift+S", triggered=self.save_input_as)
        self.open_result_action = QAction("Открыть результат", self, triggered=self.open_result)
        self.run_action = QAction("Запустить", self, shortcut="F5", triggered=self.run)
        self.run_verified_action = QAction("Запустить с верификацией", self, shortcut="Ctrl+F5", triggered=self.run_with_validation)
        self.validate_action = QAction("Проверить текущий результат", self, shortcut="F6", triggered=self.validate_result)
        self.exit_action = QAction("Выход", self, shortcut="Ctrl+Q", triggered=self.close)
        self.about_action = QAction("О программе", self, triggered=self.show_about)

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Файл")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.open_result_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        run_menu = self.menuBar().addMenu("Запуск")
        run_menu.addAction(self.run_action)
        run_menu.addAction(self.run_verified_action)
        run_menu.addSeparator()
        run_menu.addAction(self.validate_action)

        help_menu = self.menuBar().addMenu("Справка")
        help_menu.addAction(self.about_action)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Основные действия", self)
        toolbar.setMovable(False)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)

        self.run_button = QToolButton()
        self.run_button.setText("Запуск")
        self.run_button.setIcon(self._green_play_icon())
        self.run_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.run_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.run_button.clicked.connect(self.run)
        run_menu = QMenu(self.run_button)
        run_menu.addAction(self.run_action)
        run_menu.addAction(self.run_verified_action)
        self.run_button.setMenu(run_menu)
        toolbar.addWidget(self.run_button)
        self.addToolBar(toolbar)
    def _green_play_icon(self) -> QIcon:
        pixmap = QPixmap(18, 18)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#22a447"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygon([QPoint(4, 2), QPoint(4, 16), QPoint(16, 9)]))
        painter.end()
        return QIcon(pixmap)

    def _create_layout(self) -> None:
        self.file_model = QFileSystemModel(self)
        self.file_model.setRootPath(str(PROJECT_ROOT))
        self.file_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(str(INPUT_DIR)))
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setColumnHidden(1, True)
        self.file_tree.setColumnHidden(2, True)
        self.file_tree.setColumnHidden(3, True)
        self.file_tree.setAnimated(True)
        self.file_tree.clicked.connect(self._open_tree_file)

        explorer = QWidget()
        explorer_layout = QVBoxLayout(explorer)
        explorer_layout.setContentsMargins(4, 4, 4, 4)
        explorer_layout.addWidget(QLabel("Обозреватель решений"))
        explorer_layout.addWidget(self.file_tree)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self._tab_changed)

        self.log_output = QPlainTextEdit(readOnly=True)
        self.log_output.setFont(QFont("Consolas", 9))
        self.log_output.setMaximumBlockCount(2000)
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(4, 4, 4, 4)
        log_layout.addWidget(QLabel("Вывод"))
        log_layout.addWidget(self.log_output)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(explorer)
        main_splitter.addWidget(self.tabs)
        main_splitter.setSizes([330, 1270])
        overall_splitter = QSplitter(Qt.Orientation.Vertical)
        overall_splitter.addWidget(main_splitter)
        overall_splitter.addWidget(log_frame)
        overall_splitter.setSizes([720, 230])
        self.setCentralWidget(overall_splitter)

    def _log(self, message: str) -> None:
        self.log_output.appendPlainText(message.rstrip())
        cursor = self.log_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_output.setTextCursor(cursor)

    def _active_editor(self) -> QPlainTextEdit | None:
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, QPlainTextEdit) and widget in self.input_editors else None

    def _tab_changed(self, _: int) -> None:
        editor = self._active_editor()
        self.current_input = self.input_editors.get(editor) if editor is not None else None
        if self.current_input is not None:
            self.setWindowTitle(f"Steiner Tree — {self.current_input.name}")

    def _mark_modified(self) -> None:
        editor = self.sender()
        if isinstance(editor, QPlainTextEdit) and editor in self.input_editors:
            index = self.tabs.indexOf(editor)
            if index >= 0 and not self.tabs.tabText(index).endswith(" *"):
                self.tabs.setTabText(index, f"{self.input_editors[editor].name} *")

    def _open_tree_file(self, index: Any) -> None:
        path = Path(self.file_model.filePath(index))
        if path.is_file() and path.suffix.lower() == ".json":
            if path.parent == OUTPUT_DIR:
                self.load_result(path)
            else:
                self.load_input(path)

    def close_tab(self, index: int) -> None:
        widget = self.tabs.widget(index)
        if not isinstance(widget, QPlainTextEdit) or widget not in self.input_editors:
            return
        del self.input_editors[widget]
        self.tabs.removeTab(index)
        widget.deleteLater()

    def open_input(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть входной JSON", str(INPUT_DIR), "JSON (*.json);;Все файлы (*)")
        if filename:
            self.load_input(Path(filename))

    def load_input(self, path: Path) -> None:
        path = path.resolve()
        for editor, open_path in self.input_editors.items():
            if open_path == path:
                self.tabs.setCurrentWidget(editor)
                return
        try:
            text = path.read_text(encoding="utf-8")
            json.loads(text)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            self._show_error("Не удалось открыть входной JSON", str(error))
            return
        editor = QPlainTextEdit()
        editor.setFont(QFont("Consolas", 10))
        editor.setPlainText(text)
        editor.textChanged.connect(self._mark_modified)
        self.input_editors[editor] = path
        self.tabs.addTab(editor, path.name)
        self.tabs.setCurrentWidget(editor)
        self.current_input = path
        self.setWindowTitle(f"Steiner Tree — {path.name}")
        self._log(f"Открыт входной файл: {path.relative_to(PROJECT_ROOT)}")
        self.statusBar().showMessage(f"Открыт {path.name}")

    def save_input(self) -> bool:
        editor = self._active_editor()
        if editor is None:
            self._show_error("Нет входного файла", "Откройте и выберите входной JSON-файл.")
            return False
        return self._write_input(editor, self.input_editors[editor])

    def save_input_as(self) -> bool:
        editor = self._active_editor()
        if editor is None:
            self._show_error("Нет входного файла", "Откройте и выберите входной JSON-файл.")
            return False
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить входной JSON", str(INPUT_DIR / "design.json"), "JSON (*.json)")
        if not filename:
            return False
        path = Path(filename).with_suffix(".json").resolve()
        self.input_editors[editor] = path
        self.current_input = path
        return self._write_input(editor, path)

    def _write_input(self, editor: QPlainTextEdit, path: Path) -> bool:
        try:
            data = json.loads(editor.toPlainText())
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError) as error:
            self._show_error("Не удалось сохранить входной JSON", str(error))
            return False
        editor.blockSignals(True)
        editor.setPlainText(path.read_text(encoding="utf-8"))
        editor.blockSignals(False)
        index = self.tabs.indexOf(editor)
        if index >= 0:
            self.tabs.setTabText(index, path.name)
        self.setWindowTitle(f"Steiner Tree — {path.name}")
        self._log(f"Сохранён входной файл: {path.relative_to(PROJECT_ROOT)}")
        self.statusBar().showMessage(f"Сохранён {path.name}")
        return True

    def open_result(self) -> None:
        if not RESULT_PATH.is_file():
            self._show_error("Файл результата не найден", "Сначала запустите расчёт.")
            return
        self.load_result(RESULT_PATH)

    def load_result(self, path: Path) -> bool:
        path = path.resolve()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            nets = data.get("nets") if isinstance(data, dict) else data
            if not isinstance(nets, list):
                raise ValueError("ожидается объект с массивом 'nets' или массив сетей")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self._show_error("Не удалось открыть результат", str(error))
            return False
        self.result_data = data
        self.result_window.show_result(data)
        self._log(f"Открыт результат: {path.relative_to(PROJECT_ROOT)}; сетей: {len(nets)}")
        return True

    def run(self) -> None:
        self._start_run(verify=False)

    def run_with_validation(self) -> None:
        self._start_run(verify=True)

    def _start_run(self, verify: bool) -> None:
        if self.process is not None:
            return
        if not self.save_input():
            return
        editor = self._active_editor()
        if editor is None:
            return
        input_path = self.input_editors[editor]
        if not verify and not DEFAULT_EXECUTABLE.is_file():
            self._show_error("Программа не собрана", "Для первой сборки выберите «Запустить с верификацией».")
            return

        RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.process_input = input_path
        self.run_with_verification = verify
        self._log("=" * 60)
        self._log("Запуск с верификацией..." if verify else "Запуск расчёта...")
        self.process = QProcess(self)
        self.process.setWorkingDirectory(str(PROJECT_ROOT))
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_process_output)
        self.process.errorOccurred.connect(self._process_error)
        self.process.finished.connect(self._run_finished)
        self._set_running(True)
        if verify:
            self.process.start(sys.executable, [str(PIPELINE_PATH), str(input_path), str(RESULT_PATH)])
        else:
            self.process.start(str(DEFAULT_EXECUTABLE), [str(input_path), str(RESULT_PATH)])

    def _read_process_output(self) -> None:
        if self.process is not None:
            text = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
            if text:
                self._log(text)

    def _process_error(self, _: QProcess.ProcessError) -> None:
        if self.process is not None:
            self._log(f"Ошибка запуска: {self.process.errorString()}")

    def _run_finished(self, exit_code: int, _: QProcess.ExitStatus) -> None:
        self._read_process_output()
        verified = self.run_with_verification
        self._set_running(False)
        self.process = None
        if exit_code == 0:
            self._log("Расчёт и проверка завершены." if verified else "Расчёт успешно завершён.")
            self.statusBar().showMessage("Расчёт успешно завершён")
            self.load_result(RESULT_PATH)
        else:
            self._log(f"Расчёт завершился с кодом {exit_code}.")
            self.statusBar().showMessage("Расчёт завершился с ошибкой")
            self._show_error("Ошибка расчёта", "Подробности приведены в окне вывода.")

    def _set_running(self, running: bool) -> None:
        self.run_button.setEnabled(not running)
        self.run_action.setEnabled(not running)
        self.run_verified_action.setEnabled(not running)
        self.validate_action.setEnabled(not running)
        self.statusBar().showMessage("Выполняется расчёт..." if running else "Готово")

    def validate_result(self) -> None:
        if not self.save_input():
            return
        editor = self._active_editor()
        if editor is None:
            return
        input_path = self.input_editors[editor]
        if not RESULT_PATH.is_file():
            self._show_error("Файл результата не найден", "Сначала запустите расчёт.")
            return
        try:
            is_valid, message = validate(input_path, RESULT_PATH)
        except (OSError, ValueError) as error:
            self._show_error("Не удалось выполнить проверку", str(error))
            return
        if is_valid:
            self._log(f"Проверка пройдена: {message}")
            QMessageBox.information(self, "Проверка результата", message)
        else:
            self._log(f"Проверка не пройдена: {message}")
            self._show_error("Проверка результата", message)

    def _show_error(self, title: str, message: str) -> None:
        self._log(f"Ошибка: {message}")
        QMessageBox.critical(self, title, message)

    def show_about(self) -> None:
        QMessageBox.about(self, "О программе", "Steiner Tree\n\nРедактирование входных данных, запуск и визуализация дерева Штейнера.")

    def closeEvent(self, event: Any) -> None:
        if self.process is not None:
            answer = QMessageBox.question(self, "Расчёт выполняется", "Завершить выполняющийся расчёт и выйти?")
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.process.kill()
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Steiner Tree")
    window = SteinerTreeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

