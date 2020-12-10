import datetime
import sqlite3
import sys
from pathlib import Path

import tomlkit

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLCDNumber, QMenuBar, QAction, QFileDialog, QLabel, QComboBox
from PyQt5.QtCore import QTimer

class DbLabel(QLabel):
    """Displays absolute version of db_path if it exists, else warning"""
    def setText(self, db_path):
        if (abs_db_path := Path(db_path).resolve()).is_file():
            super().setText(str(abs_db_path))
        else:
            super().setText("Database not found")



class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        self.configure_settings()

        self.setWindowTitle("Timer")

        self.start_btn = QPushButton("Start")
        self.start_btn.pressed.connect(self.start)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.pressed.connect(self.pause)
        self.pause_btn.setEnabled(False)
        self.pause_time = datetime.timedelta(0)


        self.end_btn = QPushButton("End")
        self.end_btn.pressed.connect(self.end)
        self.end_btn.setEnabled(False)

        btn_layout = QHBoxLayout()

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.end_btn)

        self.proj_list = QComboBox()
        self.proj_list.addItems(self.def_proj_names)
        self.proj_list.setEditable(True)
        self.proj_list.setDuplicatesEnabled(False)
        self.project_name = self.proj_list.currentText()
        self.proj_list.currentIndexChanged.connect(self.set_project_name)

        proj_layout = QHBoxLayout()
        proj_layout.addWidget(self.proj_list)

        self.db_btn = QPushButton("Choose Database...")
        self.db_btn.pressed.connect(self.browse_db)

        self.db_label = DbLabel()
        self.db_label.setText(Path(self.db))

        db_layout = QHBoxLayout()
        db_layout.addWidget(self.db_label)
        db_layout.addWidget(self.db_btn)

        self.timer_display = QLabel()
        self.elapsed_time = datetime.timedelta(0)
        self.timer_display.setText(str(self.elapsed_time))
        self.timing = False


        layout = QVBoxLayout()
        layout.addLayout(btn_layout)
        layout.addLayout(proj_layout)
        layout.addLayout(db_layout)
        layout.addWidget(self.timer_display)


        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        choose_db = QAction("Choose Database...", self)
        choose_db.triggered.connect(self.browse_db)

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu("File")
        file_menu.addAction(choose_db)

        self.tick_timer = QTimer()

    def start(self):
        print("Start pressed")
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.end_btn.setEnabled(True)
        self.start_time = datetime.datetime.now()
        self.start_timer()


    def pause(self):
        print("Pause pressed")
        self.pause_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        self.pause_timer()


    def end(self):
        print("End pressed")
        self.end_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        self.timing = False
        self.log_time()
        self.elapsed_time = datetime.timedelta(0)
        self.pause_time = datetime.timedelta(0)

    def set_project_name(self, c_box_index):
        self.project_name = self.proj_list.itemText(c_box_index)
        if self.project_name not in self.def_proj_names:
            self.def_proj_names.insert(c_box_index, self.project_name)
        self.save_settings()


    def log_time(self, comments = ""):
        print(self.db)
        if self.db:
            conn = sqlite3.connect(self.db)
        else:
            self.browse_db()
            conn = sqlite3.connect(self.db)
        with conn:
            cur = conn.cursor()
            find_sql = "SELECT id FROM projects WHERE project_name = :p_name;"
            find_value = {"p_name": self.project_name}
            cur.execute(find_sql, find_value)
            p_id = cur.fetchone()
            if p_id:
                p_id = p_id[0]
            else:
                proj_sql = ("INSERT INTO projects(project_name) "
                            +"VALUES (:project_name);")
                proj_values = {"project_name":self.project_name}
                cur.execute(proj_sql, proj_values)
                p_id = cur.lastrowid
            record_sql = ("INSERT INTO records(p_id, date, time_worked, comments) "
                          +"VALUES (:p_id, :date, :time_worked, :comments);")
            record_values = {"p_id" : p_id,
                            "date" : datetime.date.isoformat(self.start_time),
                            "time_worked" : str(self.elapsed_time),
                            "comments" : comments}
            cur.execute(record_sql, record_values)
        conn.close()

    def start_timer(self):
        self.timing = True
        self.tick_timer.singleShot(1, self.update_timer)

    def pause_timer(self):
        self.pause_time = self.elapsed_time
        self.timing = False

    def update_timer(self):
        if self.timing:
            self.elapsed_time = (datetime.datetime.now()
                                 - self.start_time
                                 + self.pause_time)
            self.timer_display.setText(str(self.elapsed_time))
            self.tick_timer.singleShot(10, self.update_timer)


    def browse_db(self):
        self.db, _ = QFileDialog.getOpenFileName(self,"Choose a Database...", "","Sqlite Database Files (*.db)")
        self.db_label.setText(self.db)
        self.save_settings()

    def configure_settings(self):
        config_path = Path("config.toml")
        config_text = config_path.read_text()
        self.config = tomlkit.loads(config_text)
        self.def_proj_names = list(self.config.get("proj_names", []))
        self.db = Path(self.config.get("database", None))

    def save_settings(self):
        self.config["database"] = str(self.db)
        self.config["proj_names"] = self.def_proj_names
        print("saving ", tomlkit.dumps(self.config))
        with open("config.toml", "w") as f:
            f.write(tomlkit.dumps(self.config))





if __name__ == '__main__':
    app = QApplication([])       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(750, 200)
    window.show()
    exit_code = app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)