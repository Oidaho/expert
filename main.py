# main.py
import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QMessageBox,
    QFormLayout,
)

# Импорты ваших модулей
from expert_system import GPUPredictor as ExpertPredictor
from predict import predict_top_cards as NeuralPredictor

# Пути к файлам
GPU_DATA_PATH = "gpus.json"
MODEL_PATH = "gpu_model.joblib"


class GPUKnowledgeBase:
    """Работа с базой данных видеокарт"""

    def __init__(self):
        self.data = []
        self.load_data()

    def load_data(self):
        if os.path.exists(GPU_DATA_PATH):
            with open(GPU_DATA_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        return self.data

    def save_data(self):
        with open(GPU_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_card(self, card_data):
        self.data.append(card_data)
        self.save_data()

    def update_card(self, index, card_data):
        self.data[index] = card_data
        self.save_data()

    def delete_card(self, index):
        self.data.pop(index)
        self.save_data()


class KnowledgeBaseWindow(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("База знаний")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Таблица с данными
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Название", "Производитель", "TDP", "Мощность", "Архитектура", "Производительность"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")

        self.add_btn.clicked.connect(self.add_card)
        self.edit_btn.clicked.connect(self.edit_card)
        self.delete_btn.clicked.connect(self.delete_card)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(len(self.db.data))
        for row, card in enumerate(self.db.data):
            self.table.setItem(row, 0, QTableWidgetItem(card.get("card", "")))
            self.table.setItem(row, 1, QTableWidgetItem(card.get("manufacturer", "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(card.get("tdp", ""))))
            self.table.setItem(row, 3, QTableWidgetItem(str(card.get("power", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(card.get("architecture", "")))
            self.table.setItem(row, 5, QTableWidgetItem(card.get("performance", "")))

    def add_card(self):
        dialog = CardEditDialog()
        if dialog.exec_() == QDialog.Accepted:
            card_data = dialog.get_data()
            self.db.add_card(card_data)
            self.load_data()

    def edit_card(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            card_data = {
                "card": self.table.item(current_row, 0).text(),
                "manufacturer": self.table.item(current_row, 1).text(),
                "tdp": self.table.item(current_row, 2).text(),
                "power": self.table.item(current_row, 3).text(),
                "architecture": self.table.item(current_row, 4).text(),
                "performance": self.table.item(current_row, 5).text(),
            }
            dialog = CardEditDialog(card_data)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_data()
                self.db.update_card(current_row, updated_data)
                self.load_data()

    def delete_card(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self,
                "Удаление",
                "Вы действительно хотите удалить эту запись?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.db.delete_card(current_row)
                self.load_data()


class CardEditDialog(QDialog):
    def __init__(self, card_data=None):
        super().__init__()
        self.card_data = card_data or {}
        self.setWindowTitle("Редактирование видеокарты")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.fields = {
            "card": QLineEdit(self.card_data.get("card", "")),
            "manufacturer": QLineEdit(self.card_data.get("manufacturer", "")),
            "tdp": QLineEdit(self.card_data.get("tdp", "")),
            "power": QLineEdit(self.card_data.get("power", "")),
            "architecture": QLineEdit(self.card_data.get("architecture", "")),
            "performance": QLineEdit(self.card_data.get("performance", "")),
        }

        for label, field in self.fields.items():
            layout.addRow(label.capitalize(), field)

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.accept)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def get_data(self):
        return {key: field.text() for key, field in self.fields.items()}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPU Predictor")
        self.setGeometry(100, 100, 1000, 600)

        self.db = GPUKnowledgeBase()
        self.expert = ExpertPredictor()
        self.neural = NeuralPredictor

        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout()

        # Левая панель ввода
        input_widget = QWidget()
        input_layout = QFormLayout()

        self.input_fields = {
            "manufacturer": QLineEdit(),
            "tdp": QLineEdit(),
            "power": QLineEdit(),
            "architecture": QLineEdit(),
            "performance": QLineEdit(),
        }

        for label, field in self.input_fields.items():
            input_layout.addRow(label.capitalize(), field)

        input_widget.setLayout(input_layout)

        # Правая панель результатов
        results_widget = QWidget()
        results_layout = QVBoxLayout()

        self.results_list = QListWidget()
        results_layout.addWidget(self.results_list)

        btn_layout = QHBoxLayout()
        self.expert_btn = QPushButton("Экспертная оценка")
        self.neural_btn = QPushButton("Нейронная оценка")

        self.expert_btn.clicked.connect(lambda: self.predict("expert"))
        self.neural_btn.clicked.connect(lambda: self.predict("neural"))

        btn_layout.addWidget(self.expert_btn)
        btn_layout.addWidget(self.neural_btn)

        results_layout.addLayout(btn_layout)
        results_widget.setLayout(results_layout)

        # Меню
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Файл")

        view_db_action = file_menu.addAction("Просмотр базы знаний")
        view_db_action.triggered.connect(self.show_knowledge_base)

        # Основная компоновка
        layout.addWidget(input_widget, 40)
        layout.addWidget(results_widget, 60)
        main_widget.setLayout(layout)

    def get_input_data(self):
        data = {}
        for key, field in self.input_fields.items():
            value = field.text().strip()
            if value:
                data[key] = (
                    value if key in ["manufacturer", "architecture", "performance"] else int(value)
                )
            else:
                data[key] = None
        return data

    def predict(self, method):
        input_data = self.get_input_data()
        if method == "expert":
            results = self.expert.predict(input_data)
        else:
            results = self.neural(input_data)

        self.results_list.clear()
        for name, score in results:
            self.results_list.addItem(f"{name} - {score:.2f}")

    def show_knowledge_base(self):
        kb_window = KnowledgeBaseWindow(self.db)
        kb_window.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
