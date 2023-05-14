import argparse
import json
import os
from configparser import ConfigParser

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QLineEdit, QApplication

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = ConfigParser()
        self.config.optionxform = str

        if not os.path.exists(config_path):
            self.create_config()
        else:
            self.config.read(config_path)

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"File not found: {self.config_path}")
        self.config.read(self.config_path)

    def create_config(self):
        self.config['General'] = {"MyStrKey": "MyStrVar", "MyBoolKey": True, "MyTimeKey": "12:45",
                                  "MyPasswordKey": "BolosInTheWild", "MyFloatKey": "42,42", "MyIntKey": "666"}
        self.config['Documentation'] = {"Doc": "Add your documentation here"}
        self.save_config()

    def save_config(self):
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)


class PyQTConfigCraft(QtWidgets.QWidget):
    def __init__(self, config_manager):
        super().__init__()

        self.tab_widget = None
        self.config_manager = config_manager

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Config craft')
        self.resize(800, 600)

        layout = QtWidgets.QVBoxLayout()

        self.tab_widget = QtWidgets.QTabWidget()

        for section in self.config_manager.config.sections():
            if section == 'Documentation':
                doc_widget = QtWidgets.QTextBrowser()
                doc_widget.setOpenExternalLinks(True)  # Enable opening of external links
                # concatenate all lines in 'Documentation' section
                doc_html = ''.join([self.config_manager.config.get('Documentation', option) for option in
                                    self.config_manager.config.options('Documentation')])

                doc_widget.setHtml(doc_html)
                self.tab_widget.addTab(doc_widget, section)

            else:
                section_layout = QtWidgets.QFormLayout()
                section_widget = QtWidgets.QWidget()
                section_widget.setLayout(section_layout)

                for key in self.config_manager.config[section]:
                    self.add_entry(section_layout, key, self.config_manager.config.get(section, key))

                self.tab_widget.addTab(section_widget, section)

        layout.addWidget(self.tab_widget)

        save_button = QtWidgets.QPushButton('Save')
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def add_entry(self, layout, key, value):
        try:
            typed_value = json.loads(value)
        except json.JSONDecodeError:
            typed_value = value

        if isinstance(typed_value, bool):
            widget = QtWidgets.QCheckBox()
            widget.setChecked(typed_value)
        elif str(typed_value).lower() == "true" or str(typed_value).lower() == "false":
            widget = QtWidgets.QCheckBox()
            widget.setChecked(typed_value.lower() == "true")
        elif isinstance(typed_value, int):
            widget = QtWidgets.QSpinBox()
            widget.setValue(typed_value)
        elif isinstance(typed_value, float):
            widget = QtWidgets.QDoubleSpinBox()
            widget.setValue(typed_value)
        elif isinstance(typed_value, str):
            time = QTime.fromString(typed_value, "HH:mm")
            if time.isValid():
                widget = QtWidgets.QTimeEdit()
                widget.setTime(time)
            elif "password" in key.lower():
                widget = self.create_password_edit()
                widget.setText(typed_value)
            else:
                widget = QtWidgets.QLineEdit()
                widget.setText(typed_value)
        else:
            widget = QtWidgets.QLabel('Unsupported type')

        layout.addRow(key, widget)

    def create_password_edit(self):
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        toggle_password_visibility_action = QAction(QIcon('img/eye-not-looking-symbolic.svg'), 'Show Password',
                                                    password_edit)
        toggle_password_visibility_action.triggered.connect(
            lambda: self.toggle_password_visibility(toggle_password_visibility_action, password_edit))
        toggle_password_visibility_action.setCheckable(True)
        password_edit.addAction(toggle_password_visibility_action, QLineEdit.TrailingPosition)
        return password_edit

    @staticmethod
    def toggle_password_visibility(action, password_edit):
        if action.isChecked():
            password_edit.setEchoMode(QLineEdit.Normal)
            action.setIcon(QIcon('img/eye-open-negative-filled-symbolic.svg'))  # Change the icon as needed
        else:
            password_edit.setEchoMode(QLineEdit.Password)
            action.setIcon(QIcon('img/eye-not-looking-symbolic.svg'))

    def save_config(self):
        for i in range(self.tab_widget.count()):
            section = self.tab_widget.tabText(i)
            if section == 'Documentation':
                doc_widget = self.tab_widget.widget(i)
                self.config_manager.config.set('Documentation', 'Doc', doc_widget.toPlainText())
            else:
                layout = self.tab_widget.widget(i).layout()
                for j in range(0, layout.count(), 2):
                    key = layout.itemAt(j).widget().text()
                    value_widget = layout.itemAt(j + 1).widget()
                    if isinstance(value_widget, QtWidgets.QCheckBox):
                        value = value_widget.isChecked()
                    elif isinstance(value_widget, QtWidgets.QSpinBox):
                        value = value_widget.value()
                    elif isinstance(value_widget, QtWidgets.QDoubleSpinBox):
                        value = value_widget.value()
                    elif isinstance(value_widget, QtWidgets.QTimeEdit):
                        value = value_widget.text()
                    elif isinstance(value_widget, QtWidgets.QLineEdit):
                        value = value_widget.text()
                    else:
                        continue
                    self.config_manager.config.set(section, key, json.dumps(value))
        self.config_manager.save_config()


def main():
    parser = argparse.ArgumentParser(
        description='Configuration file manager. Python and PyQt5-based configuration file manager, allowing '
                    'user-friendly editing and saving of key-value pair files with diverse data types and embedded '
                    'documentation support for INI files.')
    parser.add_argument('-f', '--config-file', help='Path to the INI configuration file.')
    parser.add_argument('-i', '--icon', help='Path to the icon file.')  # TODO

    args = parser.parse_args()

    config_path = args.config_file if args.config_file else "default.ini"
    config_manager = ConfigManager(config_path)

    app = QApplication([])
    gui = PyQTConfigCraft(config_manager)
    gui.show()

    app.exec_()


if __name__ == "__main__":
    main()

