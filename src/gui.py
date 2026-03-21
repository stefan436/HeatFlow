import sys
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QFormLayout, QLineEdit, QPushButton, 
                             QComboBox, QLabel, QGroupBox, QListWidget, 
                             QMessageBox, QGraphicsView, QGraphicsScene, QCheckBox,
                             QListWidgetItem, QDialog, QDialogButtonBox, QStatusBar, QProgressBar)
from PyQt6.QtCore import Qt, QRectF, QThread, pyqtSignal
from PyQt6.QtGui import QBrush, QPen, QColor, QPalette, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import QTabWidget

from core.solver import HeatEquationSolver
from core.visualisation import plot_setup_dashboard, initial_state, final_state, interactive_heat_map, animate_heat
from core.material import material_db
from core.component_shapes import Rectangle, Square, Circle
from core.initialise_shapes import initialise_matrices

# Style sheet
APP_STYLE = """
/* GLOBAL APP STYLING - Modern Classic Dark (Subtle Edition) */
QMainWindow {
    background-color: #1e1e1e;
}

QGroupBox {
    background-color: #252526;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    margin-top: 5px;
    font-weight: bold;
    color: #cccccc;
}

QLineEdit {
    background-color: #333337;
    border: 1px solid #454545;
    border-radius: 2px;
    color: #f1f1f1;
    padding: 4px;
    selection-background-color: #4a6572;
}
QLineEdit:read-only {
    background-color: #2d2d30;
    color: #a0a0a0;
    font-style: italic;
}

/* BUTTONS */
QPushButton {
    background-color: #3e3e42;
    border: 1px solid #555555;
    color: #f1f1f1;
    padding: 5px 12px;
    border-radius: 3px;
    font-weight: normal;
}
QPushButton:hover {
    background-color: #505055;
    border-color: #4a6572;
}
QPushButton:pressed {
    background-color: #4a6572;
    color: white;
}

/* RIBBON TAB WIDGET */
QTabWidget::pane {
    border: 1px solid #3e3e42;
    background-color: #252526;
    top: -1px; 
}
QTabWidget::tab-bar {
    left: 5px; 
}
QTabBar::tab {
    background: #1e1e1e;
    color: #999999;
    padding: 8px 20px;
    border: 1px solid #3e3e42;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
    min-width: 80px;
}
QTabBar::tab:selected {
    background: #252526;
    color: #ffffff;
    border-bottom: 1px solid #252526; 
    border-top: 2px solid #4a6572;
    font-weight: bold;
}
QTabBar::tab:hover {
    background: #2d2d30;
    color: #eeeeee;
}

/* STATUS BAR */
QStatusBar {
    background-color: #252526;
    color: #cccccc;
    border-top: 1px solid #3e3e42;
}
QStatusBar QLabel {
    color: #cccccc;
    padding: 0 5px;
}

/* DIALOGS */
QDialog {
    background-color: #252526;
}
QLabel {
    color: #e1e1e1;
}
"""

def apply_native_dark_palette(app):
    app.setStyle("Fusion") 
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(37, 37, 38))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(62, 62, 66))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(74, 101, 114))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    
    app.setPalette(palette)


class SimulationWorker(QThread):
    """Hintergrund-Thread für den HeatEquationSolver, damit die GUI nicht einfriert."""
    finished = pyqtSignal(object)  
    error = pyqtSignal(str)

    def __init__(self, alpha, temp_rate_mat, u0, t_span, N, M, dx, dy, T_amb, cool_surface):
        super().__init__()
        self.args = (alpha, temp_rate_mat, u0, t_span, N, M, dx, dy, T_amb, cool_surface)

    def run(self):
        try:
            sol_tensor = HeatEquationSolver(*self.args)
            self.finished.emit(sol_tensor)
        except Exception as e:
            self.error.emit(str(e))


class ClearableListWidget(QListWidget):
    """Eine angepasste Liste, die Auswahlen aufhebt, wenn man ins Leere klickt."""
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if not item:
            self.clearSelection()
        super().mousePressEvent(event)


class EditComponentDialog(QDialog):
    def __init__(self, obj, shape, cat, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{shape} bearbeiten")
        self.shape = shape
        self.cat = cat
        self.layout = QFormLayout(self)

        self.input_x = QLineEdit(str(obj.x_center))
        self.input_y = QLineEdit(str(obj.y_center))
        self.layout.addRow("X Zentrum:", self.input_x)
        self.layout.addRow("Y Zentrum:", self.input_y)

        self.input_w, self.input_h, self.input_r = None, None, None
        if shape == "Square":
            self.input_w = QLineEdit(str(obj.side_length))
            self.layout.addRow("Seitenlänge:", self.input_w)
        elif shape == "Rectangle":
            self.input_w = QLineEdit(str(obj.x_length))
            self.input_h = QLineEdit(str(obj.y_length))
            self.layout.addRow("Breite (X):", self.input_w)
            self.layout.addRow("Höhe (Y):", self.input_h)
        elif shape == "Circle":
            self.input_r = QLineEdit(str(obj.radius))
            self.layout.addRow("Radius:", self.input_r)

        self.combo_mat, self.input_power, self.input_temp = None, None, None
        if cat in [0, 1]:  
            self.combo_mat = QComboBox()
            self.combo_mat.addItems(list(material_db.keys()))
            self.combo_mat.setCurrentText(obj.material)
            self.layout.addRow("Material:", self.combo_mat)
        
        if cat == 1:  
            self.input_power = QLineEdit(str(obj.power))
            self.layout.addRow("Power (W/m²):", self.input_power)
            
        if cat == 2:  
            self.input_temp = QLineEdit(str(obj.temp))
            self.layout.addRow("Temperatur (°C):", self.input_temp)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_values(self):
        x = int(self.input_x.text())
        y = int(self.input_y.text())
        w = int(self.input_w.text()) if self.input_w else 0
        h = int(self.input_h.text()) if self.input_h else 0
        r = float(self.input_r.text()) if self.input_r else 0.0
        mat = self.combo_mat.currentText() if self.combo_mat else None
        pwr = float(self.input_power.text()) if self.input_power else None
        tmp = float(self.input_temp.text()) if self.input_temp else None
        return x, y, w, h, r, mat, pwr, tmp


class InteractiveView(QGraphicsView):
    def __init__(self, scene, main_app):
        super().__init__(scene)
        self.main_app = main_app
        self.start_pos = None
        self.temp_item = None
        self.setRenderHint(self.renderHints().Antialiasing)
        self.scale(1, -1)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            click_pos = self.mapToScene(event.pos())
            item = self.scene().itemAt(click_pos, self.transform())
            if item and item.data(0) is not None:
                obj = item.data(0)
                self.main_app.select_item_by_obj(obj)
            else:
                self.main_app.list_items.clearSelection() 
            return

        if event.button() == Qt.MouseButton.RightButton:
            self.start_pos = self.mapToScene(event.pos())
            shape = self.main_app.combo_shape.currentText()
            pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine)
            brush = QBrush(QColor(150, 150, 150, 100))
            
            rect = QRectF(self.start_pos, self.start_pos)
            if shape in ["Square", "Rectangle"]:
                self.temp_item = self.scene().addRect(rect, pen, brush)
            elif shape == "Circle":
                self.temp_item = self.scene().addEllipse(rect, pen, brush)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() & Qt.MouseButton.RightButton and self.start_pos and self.temp_item:
            current_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, current_pos).normalized()
            shape = self.main_app.combo_shape.currentText()
            
            if shape in ["Square", "Circle"]:
                side = max(rect.width(), rect.height())
                rect.setWidth(side)
                rect.setHeight(side)
            
            self.temp_item.setRect(rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.start_pos and self.temp_item:
            current_pos = self.mapToScene(event.pos())
            rect = QRectF(self.start_pos, current_pos).normalized()
            
            self.scene().removeItem(self.temp_item)
            self.temp_item = None
            self.start_pos = None

            shape = self.main_app.combo_shape.currentText()
            
            if shape in ["Square", "Circle"]:
                side = max(rect.width(), rect.height())
                x_center = rect.left() + side / 2
                y_center = rect.top() + side / 2
                w, h, r = side, side, side / 2
            else: 
                x_center = rect.center().x()
                y_center = rect.center().y()
                w, h, r = rect.width(), rect.height(), 0

            if w > 0 or h > 0 or r > 0:
                self.main_app.add_component_from_mouse(int(x_center), int(y_center), int(w), int(h), r)


class SimulationResultsWindow(QDialog):
    """Ein separates Fenster, das alle Graphen in Reitern (Tabs) nativ einbettet."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simulationsergebnisse")
        self.resize(1000, 800)
        self.layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

    def add_plot_tab(self, fig, title):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Konvertiert die Matplotlib-Figure in ein Qt-Widget
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, tab)
        
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        self.tabs.addTab(tab, title)
        

class HeatFlowApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heat Flow Simulation - Interactive Setup")
        self.resize(1200, 750)

        self.dx = 0.001
        self.dy = 0.001

        self.components = []
        self.heat_sources = []
        self.initial_heat_spots = []

        self.worker = None
        self.current_alpha = None 

        self._build_ui()
        self._update_preview()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # ==========================================
        # LINKE SPALTE
        # ==========================================
        left_layout = QVBoxLayout()
        
        group_settings = QGroupBox("1. Simulations-Parameter")
        form_settings = QFormLayout()

        self.input_m = QLineEdit("100")
        self.input_n = QLineEdit("100")
        self.input_m.textChanged.connect(self._update_preview)
        self.input_n.textChanged.connect(self._update_preview)

        self.input_tstart = QLineEdit("1")
        self.input_tend = QLineEdit("60")
        self.input_tamb = QLineEdit("23")
        
        self.combo_substrate = QComboBox()
        self.combo_substrate.addItems(list(material_db.keys())) 
        self.combo_substrate.setCurrentText("PC (polycarbonate) at 25 °C")

        self.check_cool = QCheckBox("Oberflächenkühlung aktiv")
        self.check_cool.setChecked(True)

        form_settings.addRow("Breite (mm):", self.input_m)
        form_settings.addRow("Höhe (mm):", self.input_n)
        form_settings.addRow("Startzeit (s):", self.input_tstart)
        form_settings.addRow("Endzeit (s):", self.input_tend)
        form_settings.addRow("Umgebungstemperatur (°C):", self.input_tamb)
        form_settings.addRow("Substrat:", self.combo_substrate)
        form_settings.addRow("", self.check_cool)
        
        group_settings.setLayout(form_settings)
        left_layout.addWidget(group_settings)

        group_tools = QGroupBox("2. Zeichen-Werkzeuge")
        form_tools = QFormLayout()

        self.combo_type = QComboBox()
        self.combo_type.addItems(["Passives Bauteil", "Perm. Wärmequelle (Heizt/Kühlt)", "Initiale Hitze (Start-Temp)"])
        
        self.combo_shape = QComboBox()
        self.combo_shape.addItems(["Rectangle", "Square", "Circle"]) 
        
        self.combo_mat = QComboBox()
        self.combo_mat.addItems(list(material_db.keys()))
        self.combo_mat.setCurrentText("Silicon")

        self.input_power = QLineEdit("1000000")
        self.input_temp = QLineEdit("100")

        form_tools.addRow("Kategorie:", self.combo_type)
        form_tools.addRow("Form:", self.combo_shape)
        form_tools.addRow("Material:", self.combo_mat)
        form_tools.addRow("Power (W/m²):", self.input_power)
        form_tools.addRow("Temperatur (°C):", self.input_temp)

        group_tools.setLayout(form_tools)
        left_layout.addWidget(group_tools)

        self.list_items = ClearableListWidget()
        self.list_items.itemSelectionChanged.connect(self._update_preview)
        self.list_items.itemDoubleClicked.connect(self.edit_selected_item)
        
        left_layout.addWidget(QLabel("3. Platzierte Elemente (Doppelklick zum Editieren):"))
        left_layout.addWidget(self.list_items)

        btn_delete = QPushButton("Gewähltes Element löschen")
        btn_delete.clicked.connect(self.delete_selected_item)
        left_layout.addWidget(btn_delete)

        self.btn_run = QPushButton("SIMULATION STARTEN")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; margin-top: 10px;")
        self.btn_run.clicked.connect(self.run_simulation)
        left_layout.addWidget(self.btn_run)

        main_layout.addLayout(left_layout, 1)

        # ==========================================
        # RECHTE SPALTE
        # ==========================================
        right_layout = QVBoxLayout()
        
        # Erstelle das Tab-Widget für die rechte Seite
        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)

        # Tab 1: Interaktive Vorschau erstellen
        self.tab_preview = QWidget()
        preview_layout = QVBoxLayout(self.tab_preview)
        preview_layout.addWidget(QLabel("RECHTSKLICK + Ziehen = Neu erstellen | LINKSKLICK = Markieren | SCROLLEN = Zoom"))
        
        self.scene = QGraphicsScene()
        self.view = InteractiveView(self.scene, self)
        preview_layout.addWidget(self.view)
        
        # Vorschau als ersten Reiter hinzufügen
        self.tabs.addTab(self.tab_preview, "Setup Vorschau")

        main_layout.addLayout(right_layout, 3)
        
        # ==========================================
        # STATUSBAR (Unten rechts ausgerichtet)
        # ==========================================
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Bereit")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) 
        self.progress_bar.setFixedSize(150, 15)
        self.progress_bar.hide()
        
        # Beide Elemente als "PermanentWidget" hinzufügen, damit sie ganz rechts nebeneinander landen
        self.status_bar.addPermanentWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def add_component_from_mouse(self, x, y, w, h, r):
        cat = self.combo_type.currentIndex()
        shape = self.combo_shape.currentText()
        mat = self.combo_mat.currentText()
        
        try:
            kwargs = self._build_kwargs(cat, mat, float(self.input_power.text()), float(self.input_temp.text()))
            obj = self._create_shape_instance(shape, x, y, w, h, r, kwargs)
            
            self._add_to_backend_list(cat, obj)
            self._create_list_item(cat, shape, x, y, mat, kwargs, obj)
            self._update_preview()

        except ValueError as e:
            QMessageBox.warning(self, "Fehler", f"Fehler bei der Objektzuweisung: {str(e)}")

    def edit_selected_item(self):
        # selectedItems verwenden anstelle von currentItem
        selected_items = self.list_items.selectedItems()
        if not selected_items:
            return
            
        current_item = selected_items[0]
        obj = current_item.data(Qt.ItemDataRole.UserRole)
        cat = current_item.data(Qt.ItemDataRole.UserRole + 1)
        shape = "Square" if isinstance(obj, Square) else "Rectangle" if isinstance(obj, Rectangle) else "Circle"
        
        dialog = EditComponentDialog(obj, shape, cat, self)
        if dialog.exec():
            try:
                x, y, w, h, r, mat, pwr, tmp = dialog.get_values()
                kwargs = self._build_kwargs(cat, mat, pwr, tmp)
                new_obj = self._create_shape_instance(shape, x, y, w, h, r, kwargs)
                
                if cat == 0:
                    idx = self.components.index(obj)
                    self.components[idx] = new_obj
                elif cat == 1:
                    idx = self.heat_sources.index(obj)
                    self.heat_sources[idx] = new_obj
                elif cat == 2:
                    idx = self.initial_heat_spots.index(obj)
                    self.initial_heat_spots[idx] = new_obj

                current_item.setData(Qt.ItemDataRole.UserRole, new_obj)
                list_text = self._generate_list_text(cat, shape, x, y, mat, kwargs)
                current_item.setText(list_text)

                self._update_preview()
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Ungültige Eingabe: {str(e)}")

    def _build_kwargs(self, cat, mat, pwr, tmp):
        if cat == 0: return {"material": mat}
        elif cat == 1: return {"material": mat, "power": pwr}
        else: return {"temp": tmp}

    def _create_shape_instance(self, shape, x, y, w, h, r, kwargs):
        M = int(self.input_m.text())
        N = int(self.input_n.text())
        if shape == "Square": return Square(x, y, w, **kwargs)
        elif shape == "Rectangle": return Rectangle(x, y, w, h, **kwargs)
        elif shape == "Circle": return Circle(N, M, x, y, r, **kwargs)

    def _add_to_backend_list(self, cat, obj):
        if cat == 0: self.components.append(obj)
        elif cat == 1: self.heat_sources.append(obj)
        else: self.initial_heat_spots.append(obj)

    def _generate_list_text(self, cat, shape, x, y, mat, kwargs):
        if cat == 0: return f"Bauteil: {shape} an ({x},{y}) - {mat}"
        elif cat == 1: return f"Heizung: {shape} an ({x},{y}) - {kwargs.get('power')} W/m²"
        else: return f"Start-Temp: {shape} an ({x},{y}) - {kwargs.get('temp')} °C"

    def _create_list_item(self, cat, shape, x, y, mat, kwargs, obj):
        list_text = self._generate_list_text(cat, shape, x, y, mat, kwargs)
        item = QListWidgetItem(list_text)
        item.setData(Qt.ItemDataRole.UserRole, obj)
        item.setData(Qt.ItemDataRole.UserRole + 1, cat)
        self.list_items.addItem(item)
        
        # Sicherstellen, dass das neue Item ausgewählt ist
        self.list_items.clearSelection()
        item.setSelected(True)

    def select_item_by_obj(self, obj):
        for i in range(self.list_items.count()):
            item = self.list_items.item(i)
            if item.data(Qt.ItemDataRole.UserRole) is obj:
                self.list_items.clearSelection()
                item.setSelected(True)
                break

    def delete_selected_item(self):
        selected_items = self.list_items.selectedItems()
        if not selected_items:
            return
            
        current_item = selected_items[0]
        obj = current_item.data(Qt.ItemDataRole.UserRole)
        cat = current_item.data(Qt.ItemDataRole.UserRole + 1)
        
        if cat == 0 and obj in self.components: self.components.remove(obj)
        elif cat == 1 and obj in self.heat_sources: self.heat_sources.remove(obj)
        elif cat == 2 and obj in self.initial_heat_spots: self.initial_heat_spots.remove(obj)
            
        row = self.list_items.row(current_item)
        self.list_items.takeItem(row)
        self._update_preview()

    def _update_preview(self):
        self.scene.clear()
        try:
            m = int(self.input_m.text())
            n = int(self.input_n.text())
        except ValueError:
            return

        board_rect = QRectF(0, 0, m, n)
        bg_item = self.scene.addRect(board_rect, QPen(Qt.GlobalColor.black), QBrush(QColor(220, 220, 220)))
        bg_item.setZValue(-1)

        selected_obj = None
        selected_items = self.list_items.selectedItems()
        if selected_items:
            selected_obj = selected_items[0].data(Qt.ItemDataRole.UserRole)

        def draw_objects(obj_list, color):
            for obj in obj_list:
                is_selected = (obj is selected_obj)
                pen = QPen(Qt.GlobalColor.yellow, 3) if is_selected else QPen(Qt.GlobalColor.black, 1)
                
                rect_item = None
                if isinstance(obj, Square):
                    r = QRectF(obj.bottom_left[0], obj.bottom_left[1], obj.side_length, obj.side_length)
                    rect_item = self.scene.addRect(r, pen, QBrush(color))
                elif isinstance(obj, Rectangle):
                    r = QRectF(obj.bottom_left[0], obj.bottom_left[1], obj.x_length, obj.y_length)
                    rect_item = self.scene.addRect(r, pen, QBrush(color))
                elif isinstance(obj, Circle):
                    r = QRectF(obj.x_center - obj.radius, obj.y_center - obj.radius, obj.radius * 2, obj.radius * 2)
                    rect_item = self.scene.addEllipse(r, pen, QBrush(color))

                if rect_item:
                    rect_item.setData(0, obj)
                    if is_selected:
                        rect_item.setZValue(1)

        draw_objects(self.components, QColor(100, 150, 255, 200))
        draw_objects(self.heat_sources, QColor(255, 100, 100, 200))
        draw_objects(self.initial_heat_spots, QColor(255, 165, 0, 200))

        if len(self.scene.items()) <= 1: 
            self.view.setSceneRect(-10, -10, m + 20, n + 20)
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
            
    def add_plot_tab(self, fig, title):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Konvertiert die Matplotlib-Figure in ein Qt-Widget
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, tab)
        
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        self.tabs.addTab(tab, title)
        

    def run_simulation(self):
        try:
            M = int(self.input_m.text())
            N = int(self.input_n.text())
            t_span = (float(self.input_tstart.text()), float(self.input_tend.text()))
            T_amb = float(self.input_tamb.text())
            substrate = self.combo_substrate.currentText()
            cool_surface = self.check_cool.isChecked()

            self.status_label.setText("Erstelle Matrizen...")
            alpha, temp_rate_mat, u0 = initialise_matrices(N, M, substrate, self.components, self.heat_sources, self.initial_heat_spots)

            self.current_alpha = alpha
            self.temp_rate_mat = temp_rate_mat
            self.u0 = u0

            # --- ALTE ERGEBNISSE LÖSCHEN (alles außer der 3D/Zeichnen-Vorschau auf Index 0) ---
            while self.tabs.count() > 1:
                self.tabs.removeTab(1)

            # --- SETUP DASHBOARD SOFORT ZEIGEN ---
            fig_setup = plot_setup_dashboard(alpha, temp_rate_mat, u0)
            self.add_plot_tab(fig_setup, "Setup Übersicht")
            self.tabs.setCurrentIndex(1)  # Wechselt direkt zum neuen Dashboard-Tab

            self.status_label.setText("Integration läuft (Dies kann dauern)...  ")
            self.progress_bar.show()
            self.btn_run.setEnabled(False)

            self.worker = SimulationWorker(alpha, temp_rate_mat, u0, t_span, N, M, self.dx, self.dy, T_amb, cool_surface)
            self.worker.finished.connect(self.on_simulation_finished)
            self.worker.error.connect(self.on_simulation_error)
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Setup Fehler", f"Fehler vor der Simulation:\n{str(e)}")

    def on_simulation_finished(self, sol_tensor):
        self.status_label.setText("Bereit")
        self.progress_bar.hide()
        self.btn_run.setEnabled(True)

        temp_min, temp_max = sol_tensor.min(), sol_tensor.max()

        # 1. Restliche Figures über das Backend generieren
        fig_initial = initial_state(sol_tensor, temp_min, temp_max, alpha=self.current_alpha) 
        fig_final = final_state(sol_tensor, temp_min, temp_max, alpha=self.current_alpha) 
        
        # WICHTIG: Referenzen an self binden, damit der Garbage Collector Slider/Animation nicht vorzeitig freigibt.
        fig_interactive, self.heat_slider = interactive_heat_map(sol_tensor, temp_min, temp_max, alpha=self.current_alpha) 
        fig_ani, self.heat_ani = animate_heat(sol_tensor, temp_min, temp_max, alpha=self.current_alpha) 

        # 2. Ergebnisse als neue Tabs anfügen
        self.add_plot_tab(fig_initial, "Startzustand")
        self.add_plot_tab(fig_final, "Endzustand")
        self.add_plot_tab(fig_interactive, "Zeitschieberegler")
        self.add_plot_tab(fig_ani, "Animation")
        
        # Fokus optional auf den Startzustand setzen (Index 2), um Abschluss zu signalisieren
        self.tabs.setCurrentIndex(2)

    def on_simulation_error(self, err_msg):
        self.status_label.setText("Fehler!")
        self.progress_bar.hide()
        self.btn_run.setEnabled(True)
        QMessageBox.critical(self, "Simulationsfehler", f"Fehler während der Integration:\n{err_msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Schriftart anpassen (wie im DataProcessor)
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    QApplication.setFont(font)
    
    # Design anwenden
    apply_native_dark_palette(app)
    app.setStyleSheet(APP_STYLE)
    
    window = HeatFlowApp()
    window.showMaximized()
    sys.exit(app.exec())