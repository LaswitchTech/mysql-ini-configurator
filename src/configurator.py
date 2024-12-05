#!/usr/bin/env python3
import sys
import os
import psutil
import chardet
import json
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QScrollArea, QLineEdit, QSizePolicy, QFrame,
    QCheckBox, QFormLayout, QPushButton, QComboBox,
    QFileDialog, QHBoxLayout, QMessageBox, QLabel,
    QSlider, QSpinBox, QListWidget, QListWidgetItem
)
from configparser import ConfigParser

# Declare Constants
APP_NAME = "MySQL INI Configurator"
INI_FILE = "my.ini"
LOG_FILE = "log.log"
ENCODING = "mbcs" if sys.platform == "win32" else "utf-8"
DEBUG = True

class CaseSensitiveConfigParser(ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_lines = []  # Store raw lines from the file
        self.detected_encoding = ENCODING  # Default encoding

    def read(self, filenames, encoding=None):
        """Read the configuration file and preserve raw lines."""
        with open(filenames, 'rb') as binary_file:
            raw_data = binary_file.read()
            detected = chardet.detect(raw_data)
            self.detected_encoding = detected['encoding'] or ENCODING

        # Use detected encoding or specified encoding
        final_encoding = encoding or self.detected_encoding
        with open(filenames, 'r', encoding=final_encoding) as f:
            self.raw_lines = f.readlines()  # Store raw lines
        super().read_string(''.join(self.raw_lines), source=filenames)

    def get_raw_lines(self):
        """Return raw lines from the file."""
        return self.raw_lines

    def get_encoding(self):
        """Return detected encoding."""
        return self.detected_encoding

class Configurator(QMainWindow):

    ############################################################################
    #
    # Constructor
    #
    ############################################################################

    def __init__(self, ini_path):
        super().__init__()

        # Initialize the fields
        self.init_app(ini_path)

        # Initialize the fields
        self.init_fields()

        # Initialize the configurations
        self.init_config()

        # Initialize the UI
        self.init_ui()

        # Initialize the form
        self.init_form()

    ############################################################################
    #
    # Initialization Methods
    #
    ############################################################################

    def init_app(self, ini_path):

        # Dynamically determine the path to my.ini in the same directory as this script
        if getattr(sys, 'frozen', False):
            # If the application is frozen (e.g., running as .app or .exe)
            if sys.platform == "darwin":
                # For macOS, locate the directory containing the .app bundle
                self.script_directory = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', '..', '..'))
                self.resource_directory = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "..", "Resources"))
            elif sys.platform == "win32":
                # For Windows, locate the directory containing the .exe file
                self.script_directory = os.path.abspath(os.path.dirname(sys.executable))
                self.resource_directory = os.path.abspath(sys._MEIPASS)
            else:
                # For other platforms, use the executable's directory
                self.script_directory = os.path.dirname(sys.executable)
                self.resource_directory = self.script_directory
        else:
            # If running as a regular script
            self.script_directory = os.path.dirname(os.path.abspath(__file__))
            self.resource_directory = os.path.join(self.script_directory)

        # Debugging
        self.log("Script Directory:", self.script_directory)
        self.log("Resource Directory:", self.resource_directory)

        # Application settings
        self.ini_path = os.path.join(self.script_directory, ini_path)
        self.window_title = APP_NAME
        self.encoding = ENCODING

        # Debugging
        self.log("INI Path:", self.ini_path)
        self.log("Application Name:", self.window_title)
        self.log("Default Encoding:", self.encoding)
        self.log("Application initialized.")

    def init_fields(self):

        # Debugging
        self.log("Initializing Fields...")

        # Fields dictionary
        self.fields = {}

        # Set filename
        filename = os.path.join(self.resource_directory, "lib/fields.json")

        # Load the field listing from src/fields.json if it exists
        if os.path.exists(filename):

            with open(filename, 'rb') as binary_file:
                raw_data = binary_file.read()
                detected = chardet.detect(raw_data)['encoding']

            # Load fields from JSON file
            with open(filename, "r", encoding=detected) as f:

                # Loop through each section and field
                for section, fields in json.load(f).items():
                    for key, parameters in fields.items():

                        # Debugging
                        self.log(f"Field: {section} -> {key}")

                        # Add the field to the dictionary
                        self.add_fields(
                            section,
                            key,
                            parameters["label"],
                            parameters["tooltip"],
                            parameters["type"],
                            parameters["default"],
                            parameters["required"],
                            parameters.get("options", [])
                        )

        # Debugging
        self.log("Fields initialized.")

    def init_config(self):

        # Debugging
        self.log("Initializing Configurations...")

        # Initialize the configuration dictionary
        self.config = {}

        # Load default configuration from fields
        for section, fields in self.fields.items():

            # Create the section if it doesn't exist
            if section not in self.config:
                self.config[section] = {}

            # Add the field to the section
            for key, parameters in fields.items():

                # Debugging
                self.log(f"Configuring: {section} -> {key}")

                self.config[section][key] = parameters["default"]

        # Initialize the Parser
        Parser = CaseSensitiveConfigParser(allow_no_value=True)

        # Load configuration from the INI file
        if os.path.exists(self.ini_path):

            # Read the configuration file
            Parser.read(self.ini_path, encoding=self.encoding)

            # Use the encoding detected when reading the file
            if isinstance(Parser, CaseSensitiveConfigParser):
                self.encoding = Parser.get_encoding()

            # Debugging
            self.log("Encoding:", self.encoding)

            # Get raw lines to check for raw values
            raw_lines = Parser.get_raw_lines()

            # Debugging
            self.log("Reading configuration from INI file...")
            self.log("Raw Lines:", raw_lines)

            # Create a dictionary to map sections to their lines
            section_lines = {}
            current_section = None

            for line in raw_lines:
                stripped_line = line.strip()
                if stripped_line.startswith("[") and stripped_line.endswith("]"):
                    # This is a section header
                    current_section = stripped_line[1:-1].strip()  # Extract section name
                    section_lines[current_section] = []
                elif current_section is not None:
                    # Add line to the current section
                    section_lines[current_section].append(line)

            # Debugging
            self.log("Section Lines:", section_lines)

            # Overwrite default values with existing configuration
            for section, fields in self.fields.items():
                for key, parameters in fields.items():
                    if parameters["type"] == "raw":
                        self.config[section][key] = "False"
                        raw_string = parameters["default"]
                        # Debugging
                        self.log(f"Raw String: {raw_string}")
                        if raw_string[-1] != "\n":
                            raw_string += "\n"
                        if section in section_lines and raw_string in section_lines[section]:
                            self.config[section][key] = "True"
                    elif section in Parser and key in Parser[section]:
                        self.config[section][key] = Parser[section][key]

        # Debugging
        if DEBUG:
            self.log("Sections found:", Parser.sections())
            for section, fields in self.config.items():
                self.log(f"Section: {section}")
                for key, value in fields.items():
                    self.log(f"  {key} = {value}")
        self.log("Configurations initialized.")

    def init_ui(self):

        # Debugging
        self.log("Initializing UI...")

        # Main window settings
        self.setWindowTitle(self.window_title)
        self.setWindowIcon(QIcon(os.path.join(self.resource_directory, "icons/icon.png")))
        self.resize(800, 600)
        self.setObjectName("mainWindow")

        # Determine the paths based on whether the app is frozen
        stylesheet_path = os.path.join(self.resource_directory, "styles/style.css")

        # Load and set the stylesheet
        if os.path.exists(stylesheet_path):
            stylesheet = self.load_stylesheet(stylesheet_path, self.resource_directory)
            self.setStyleSheet(stylesheet)

        # Main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setObjectName("mainLayout")
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_widget)

        # Add a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setObjectName("scrollLayout")
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # Save button
        self.save_button = QPushButton("Save Configuration")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_config)
        self.main_layout.addWidget(self.save_button)

        # Debugging
        self.log("UI initialized.")

    def init_form(self):

        # Debugging
        self.log("Initializing Form...")

        # Initialize the objs dictionary
        self.objs = {}

        # Add sections and fields to the form
        for section, fields in self.fields.items():

            # Add the section to the objs dictionary
            self.objs[section] = {}

            # Add the section to the form
            layout = self.add_section(section)

            # Add the fields to the layout
            for key, parameters in fields.items():
                self.add_input(layout, section, key, parameters)

        # Debugging
        self.log("Form initialized.")

    ############################################################################
    #
    # Helper Methods
    #
    ############################################################################

    def load_stylesheet(self, stylesheet_path, resource_directory):
        with open(stylesheet_path, "r") as f:
            stylesheet = f.read()

        # Replace relative image paths with absolute paths
        stylesheet = stylesheet.replace("src/", f"{resource_directory}/")
        return stylesheet

    def toggle_section(self, section_container, chevron):
        is_visible = section_container.isVisible()
        section_container.setVisible(not is_visible)
        chevron.setText("▼" if is_visible else "▲")

    def parse_variables(self, value):

        # Debugging
        self.log(f"Parsing variables in [{value}]...")

        # Check the variable type
        if isinstance(value, bool):
            value = "1" if value else "0"
        elif not isinstance(value, str):
            value = str(value)

        # Replace %AppDir% with the directory of the INI file
        if "%AppDir%" in value:
            value = value.replace("%AppDir%", self.script_directory)

        # Replace %TotalRAM% with the total RAM in bytes
        if "%TotalRAM%" in value:
            value = str(value).replace("%TotalRAM%", str(psutil.virtual_memory().total))

        # Remove Quotes and Double Quotes
        value = value.replace('"', "").replace("'", "")

        # Remove leading and trailing whitespace
        value = value.strip()

        # Debugging
        self.log(f"Value parsed: [{value}]")

        return value

    def convert_encoding(self, text):
        # Detect the encoding of the text
        encoding = chardet.detect(text)["encoding"]
        # Convert the text to self.encoding
        return text.decode(encoding, errors='ignore').encode(self.encoding)

    def convert_to_string(self, array):

        # loop through the array and convert each item to a string
        for i in range(len(array)):
            array[i] = str(array[i])

        return array

    def convert_to_bytes(self, size):

        # Debugging
        self.log(f"Parsing size [{size}]...")

        # Check if the size is a string
        if isinstance(size, str):

            # Check if the size ends with a unit
            if size[-1].isalpha():

                # Get the unit and value
                unit = size[-1].lower()
                value = int(size[:-1])

                # Convert the value to bytes
                if unit == "t":
                    return value * 1024**4
                elif unit == "g":
                    return value * 1024**3
                elif unit == "m":
                    return value * 1024**2
                elif unit == "k":
                    return value * 1024
                elif unit == "b":
                    return value

        return int(size)

    def convert_to_human_readable(self, size):

        # Debugging
        self.log(f"Parsing size [{size}]...")

        # Convert the size to a human-readable format
        if size >= 1024**4:
            return f"{size / 1024**4:.2f} TB"
        elif size >= 1024**3:
            return f"{size / 1024**3:.2f} GB"
        elif size >= 1024**2:
            return f"{size / 1024**2:.2f} MB"
        elif size >= 1024:
            return f"{size / 1024:.2f} KB"

        return f"{size} B"

    def convert_to_ini(self, size):

        # Debugging
        self.log(f"Parsing size [{size}]...")

        # Convert the size to a human-readable format and remove decimals
        if size >= 1024**4:
            return f"{size // 1024**4}T"
        elif size >= 1024**3:
            return f"{size // 1024**3}G"
        elif size >= 1024**2:
            return f"{size // 1024**2}M"
        elif size >= 1024:
            return f"{size // 1024}B"

        return f"{size}B"

    def get_array_key(self, array, key):
        if isinstance(array, list):
            for item in array:
                if isinstance(item, dict) and key in item:
                    return item[key]
        return None

    def browse_path(self, line_edit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory", self.script_directory)
        if path:
            line_edit.setText(path)

    ############################################################################
    #
    # Data Methods
    #
    ############################################################################

    def add_fields(self, section, key, label, tooltip, type, default=None, required=True, options=[]):

        # Create the section if it doesn't exist
        if section not in self.fields:
            self.fields[section] = {}

        # Add the field to the section
        self.fields[section][key] = {
            "label": label,
            "tooltip": tooltip,
            "type": type,
            "default": default,
            "required": required,
            "options": options,
        }

        # Debugging
        self.log(f"Field added: {section} -> {key}")

    ############################################################################
    #
    # Form Methods
    #
    ############################################################################

    def add_section(self, section):

        # Debugging
        self.log("Initializing Section[{section}]...")

        # Section title with chevron
        section_title = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)
        title_label = QLabel(f"<b>{section}</b>")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setObjectName("sectionTitle")

        chevron = QLabel("▼")
        chevron.setAlignment(Qt.AlignRight)
        chevron.setFixedWidth(30)
        chevron.setObjectName("sectionChevron")

        title_layout.addWidget(title_label, stretch=1)
        title_layout.addWidget(chevron, stretch=0)
        section_title.setLayout(title_layout)
        section_title.setObjectName("sectionHeader")
        section_title.setCursor(Qt.PointingHandCursor)

        # Section container
        section_container = QFrame()
        section_container.setContentsMargins(0, 0, 0, 0)
        section_layout = QVBoxLayout()
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(0)
        section_layout.setObjectName("sectionLayout")
        section_container.setLayout(section_layout)
        section_container.setObjectName("sectionContainerLayout")

        # Add to scroll layout
        self.scroll_layout.addWidget(section_title)
        self.scroll_layout.addWidget(section_container)

        # Collapse/expand functionality
        section_container.setVisible(False)
        section_title.mousePressEvent = lambda event: self.toggle_section(section_container, chevron)

        # Debugging
        self.log(f"Section[{section}] initialized.")

        # Return the section layout
        return section_layout

    def add_input(self, layout, section, key, parameters):

        # Debugging
        self.log(f"Initializing Input[{section} -> {key}]...")

        # Get the value from the configuration
        value = self.parse_variables(self.config[section].get(key, parameters["default"]))

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)
        row_layout.setObjectName("rowLayout")

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)
        container.setToolTip(parameters["tooltip"])
        container.setObjectName("rowContainerLayout")

        # Add a label
        label_layout = QHBoxLayout()
        label = QLabel(parameters["label"])
        label.setObjectName("fieldLabel")
        label.setFixedWidth(200)

        # Add the input field
        if parameters["type"] == "static":
            label = QLabel(value)
            label.setObjectName("fieldLabel")
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            label.setWordWrap(True)
        elif parameters["type"] == "text":
            input = QLineEdit()
            input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            input.setText(value)
        elif parameters["type"] == "password":
            input = QLineEdit()
            input.setEchoMode(QLineEdit.Password)
            input.setText(value)
        elif parameters["type"] == "number":
            input = QSpinBox()
            options = parameters.get("options", {})
            if isinstance(options, dict):
                min_value = options.get("min", 0)
                max_value = options.get("max", 100000)
            else:
                min_value = 0
                max_value = 100000
            input.setMinimum(int(self.parse_variables(min_value)))
            input.setMaximum(int(self.parse_variables(max_value)))
            input.setValue(int(value))
        elif parameters["type"] == "checkbox":
            input = QCheckBox()
            if value.lower() in ["1", "true", "yes", "on", ""]:
                input.setChecked(1)
        elif parameters["type"] == "raw":
            input = QCheckBox()
            if value.lower() in ["1", "true", "yes", "on", ""]:
                input.setChecked(1)
        elif parameters["type"] == "select":
            input = QComboBox()
            input.addItems(self.convert_to_string(parameters["options"]))
            input.setCurrentText(value)
        elif parameters["type"] == "multi-select":
            input = QListWidget()
            input.setSelectionMode(QListWidget.MultiSelection)
            if isinstance(value, str):
                value = value.split(",")
            for option in parameters["options"]:
                item = QListWidgetItem(option)
                input.addItem(item)
                if option in value:
                    item.setSelected(True)
        elif parameters["type"] == "range":
            # Handle range inputs
            options = parameters.get("options", {})
            if isinstance(options, dict):
                min_value = options.get("min", 0)
                max_value = options.get("max", 100)
            else:
                min_value = 0
                max_value = 100
            min_value = int(self.parse_variables(min_value))
            max_value = int(self.parse_variables(max_value))
            value = int(value)

            # Debugging
            self.log(f"Min: {min_value}, Max: {max_value}, Value: {value}")

            # Create a slider for the range
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(min_value)
            slider.setMaximum(max_value)
            slider.setValue(value)
            slider.setContentsMargins(0, 0, 0, 0)
            slider.setTickInterval((max_value - min_value) // 10 or 1)
            slider.setTickPosition(QSlider.TicksBelow)

            # Create a label to show the current value
            value_label = QLabel(str(value))
            value_label.setContentsMargins(0, 0, 0, 0)
            slider.valueChanged.connect(
                lambda v: value_label.setText(str(v))
            )

            # Layout for the slider and label
            input = QWidget()
            input_layout = QHBoxLayout(input)
            input_layout.addWidget(slider)
            input_layout.addWidget(value_label)
            input_layout.setContentsMargins(0, 0, 0, 0)
        elif parameters["type"] == "filesize":
            # Handle filesize inputs
            options = parameters.get("options", {})
            scale = 1024  # KB as the base scale
            if isinstance(options, dict):
                min_value = options.get("min", scale)
                max_value = options.get("max", 1024**3)
            else:
                min_value = scale
                max_value = 1024**3
            min_value = int(self.parse_variables(min_value))
            max_value = int(self.parse_variables(max_value))
            value = self.convert_to_bytes(value)

            # Debugging
            self.log(f"Min: {min_value}, Max: {max_value}, Value: {value}")

            # Scale the values for the slider
            min_scaled = min_value // scale
            max_scaled = max_value // scale
            default_scaled = value // scale

            # Create a slider for the filesize
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(min_scaled)
            slider.setMaximum(max_scaled)
            slider.setValue(default_scaled)
            slider.setTickInterval((max_scaled - min_scaled) // 10 or 1)
            slider.setTickPosition(QSlider.TicksBelow)

            # Create a label to show the human-readable value
            value_label = QLabel(self.convert_to_human_readable(value))
            slider.valueChanged.connect(
                lambda v: value_label.setText(self.convert_to_human_readable(v * scale))
            )

            # Layout for the slider and label
            input = QWidget()
            input_layout = QHBoxLayout(input)
            input_layout.addWidget(slider)
            input_layout.addWidget(value_label)
            input_layout.setContentsMargins(0, 0, 0, 0)
        elif parameters["type"] == "path":
            # Handle path inputs
            default_path = os.path.abspath(self.parse_variables(parameters["default"])) if parameters["default"] else ""
            value = os.path.abspath(self.parse_variables(value) or default_path)

            # Create the layout and widgets for the path field
            path_layout = QHBoxLayout()
            path_layout.setContentsMargins(0, 0, 0, 0)
            line_edit = QLineEdit()
            line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            line_edit.setText(value)
            browse_button = QPushButton("...")
            default_button = QPushButton("Set Default")

            # Connect buttons
            browse_button.clicked.connect(lambda: self.browse_path(line_edit))
            default_button.clicked.connect(lambda: line_edit.setText(default_path))

            # Add widgets to the path layout
            path_layout.addWidget(line_edit)
            path_layout.addWidget(browse_button)
            path_layout.addWidget(default_button)

            # Wrap the path layout in a QWidget
            input = QWidget()
            input.setLayout(path_layout)
        else :
            input = QLineEdit()
            input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            input.setText(value)

        # Add the label and input to the row layout
        label_layout.addWidget(label)
        label_widget = QWidget()
        label_widget.setLayout(label_layout)
        row_layout.addWidget(label_widget)
        layout.addWidget(container)

        # Check if the input is a static text
        if not parameters["type"] == "static":

            # Set an object name for the input
            input.setObjectName("fieldInput")
            if parameters["type"] in ["range","filesize"]:
                input.setObjectName("fieldRange")
            elif parameters["type"] == "path":
                input.setObjectName("fieldPath")
            elif parameters["type"] == "multi-select":
                input.setObjectName("fieldMultiSelect")
            elif parameters["type"] in ["checkbox","raw"]:
                input.setObjectName("fieldCheckbox")

            # Debugging
            self.log(f"Object Name: {input.objectName()}")

            # Add the input field to the layout
            label_layout.addWidget(input)

            # Store the field in the objs dictionary
            self.objs[section][key] = input
            if parameters["type"] in ["filesize","range"]:
                self.objs[section][key] = slider
            elif parameters["type"] == "path":
                self.objs[section][key] = line_edit

        # Debugging
        self.log(f"Input[{section} -> {key}] initialized.")

    ############################################################################
    #
    # Core Methods
    #
    ############################################################################

    def log(self, *message):
        if DEBUG:
            print(*message)
            with open(os.path.abspath(os.path.join(self.script_directory, LOG_FILE)), "a") as f:
                print(*message, file=f)

    def save_config(self):

        try:

            # Retrieve the configuration from the form
            for section, fields in self.fields.items():
                for key, parameters in fields.items():

                    # Skip if the field is not in the objs dictionary
                    if key not in self.objs[section]:
                        if key in self.config[section]:
                            self.config[section].pop(key)
                        continue

                    # Get the object
                    obj = self.objs[section][key]

                    # Process value based on field type
                    if parameters["type"] == "filesize":
                        value = self.convert_to_ini(obj.value() * 1024)
                    elif parameters["type"] == "range":
                        value = str(obj.value())
                    elif parameters["type"] == "multi-select":
                        selected_items = obj.selectedItems()
                        selected_values = [item.text() for item in selected_items]
                        value = ",".join(selected_values)
                    elif parameters["type"] == "select":
                        value = obj.currentText()
                    elif parameters["type"] == "text":
                        value = obj.text()
                    elif parameters["type"] == "static":
                        value = None
                    elif parameters["type"] == "number":
                        value = str(obj.value())
                    elif parameters["type"] == "checkbox":
                        value = "True" if obj.isChecked() else "False"
                    elif parameters["type"] == "raw":
                        if obj.isChecked():
                            value = str(parameters["default"])
                        else:
                            value = None
                    else:
                        value = obj.text()

                    # Debugging
                    self.log(f"Attempting: {section} -> {key} = {value}")

                    # Add quotes to the value if it contains spaces
                    if value is not None and " " in value:
                        value = f'"{value}"'

                    # Convert default to string
                    if not isinstance(parameters["default"], str):
                        parameters["default"] = str(parameters["default"])

                    # Save the value to the config
                    self.config[section][key] = value

                    # Unset the confguration value if it is the same as default and no required
                    if value is None or (parameters["type"] != "raw" and value.lower() == parameters["default"].lower() and not parameters["required"]):
                        self.config[section].pop(key)
                    else:
                        # Debugging
                        self.log(f"Saving: {section} -> {key} = {value}")

            # Write the updated configuration back to the file
            with open(self.ini_path, "w", encoding=self.encoding) as configfile:
                for section, fields in self.fields.items():
                    configfile.write(f"[{section}]\n")
                    for key, parameters in fields.items():
                        value = self.config[section].get(key)
                        if parameters["type"] == "raw":
                            if value:
                                configfile.write(f"{value}\n")
                        elif value:
                            configfile.write(f"{key} = {value}\n")
                    configfile.write("\n")

            QMessageBox.information(self, "Saved", "Configurations saved successfully.")
        except Exception as e:
            self.log("Error saving configuration:", str(e))
            QMessageBox.critical(self, "Error", f"Failed to save configurations:\n{e}")

############################################################################
#
# Entry Point
#
############################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Configurator(INI_FILE)
    window.show()
    sys.exit(app.exec_())
