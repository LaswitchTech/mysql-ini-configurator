#!/usr/bin/env python3
import sys
import os
import psutil
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QScrollArea, QLineEdit, QSizePolicy, QFrame,
    QCheckBox, QFormLayout, QPushButton, QComboBox,
    QFileDialog, QHBoxLayout, QMessageBox, QLabel,
    QSlider, QSpinBox
)
from configparser import ConfigParser


class CaseSensitiveConfigParser(ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_lines = []  # Store raw lines from the file

    def read(self, filenames, encoding=None):
        """Read the configuration file and preserve raw lines."""
        with open(filenames, 'r', encoding=encoding or 'utf-8') as f:
            self.raw_lines = f.readlines()  # Store raw lines
        super().read(filenames, encoding=encoding)

    def get_raw_lines(self):
        """Return raw lines from the file."""
        return self.raw_lines

class MySQLConfigurator(QMainWindow):
    def __init__(self, ini_path):
        super().__init__()

        # Debug mode
        # self.debug = True
        self.debug = False

        # Main window settings
        self.setWindowTitle("MySQL INI Configurator")
        self.setWindowIcon(QIcon("src/icons/icon.png"))
        self.resize(800, 600)

        # Configuration file path
        self.ini_path = ini_path
        self.default_directory = os.path.dirname(self.ini_path)
        self.config = CaseSensitiveConfigParser(allow_no_value=True)

        # Load the configuration or initialize defaults
        if os.path.exists(self.ini_path):
            self.config.read(self.ini_path)
        if not self.config.sections():  # Check if the config is empty
            self.initialize_default_config()  # Initialize with defaults

        if self.debug:
            print("Sections found:", self.config.sections())
            for section in self.config.sections():
                print(f"Section: {section}")
                for key, value in self.config.items(section):
                    print(f"  {key} = {value}")

        # Labels for user-friendly names
        self.labels = {
            "port": "Port",
            "basedir": "Base Directory",
            "datadir": "Data Directory",
            "sql-mode": "SQL Mode",
            "log-output": "Log Output",
            "general-log": "General Log",
            "max_connections": "Max Connections",
            "table_open_cache": "Table Open Cache",
            "innodb_buffer_pool_size": "InnoDB Buffer Pool Size",
            "tmp_table_size": "Temporary Table Size",
            "pipe": "Named Pipe",
            "socket": "Socket",
            "no-beep": "Disable Beep",
            "default-character-set": "Default Character Set",
            "skip-networking": "Skip Networking",
            "enable-named-pipe": "Enable Named Pipe",
            "shared-memory": "Enable Shared Memory",
            "shared-memory-base-name": "Shared Memory Base Name",
            "named-pipe-full-access-group": "Named Pipe Full Access Group",
            "character-set-server": "Character Set Server",
            "authentication_policy": "Authentication Policy",
            "default-storage-engine": "Default Storage Engine",
            "general_log_file": "General Log File",
            "slow-query-log": "Enable Slow Query Log",
            "slow_query_log_file": "Slow Query Log File",
            "long_query_time": "Long Query Time (s)",
            "log-error": "Error Log File",
            "log-bin": "Binary Log File",
            "server-id": "Server ID",
            "lower_case_table_names": "Lower Case Table Names",
            "secure-file-priv": "Secure File Privilege Directory",
            "temptable_max_ram": "TempTable Max RAM",
            "internal_tmp_mem_storage_engine": "Temporary Memory Storage Engine",
            "myisam_max_sort_file_size": "MyISAM Max Sort File Size",
            "myisam_sort_buffer_size": "MyISAM Sort Buffer Size",
            "key_buffer_size": "MyISAM Key Buffer Size",
            "read_buffer_size": "MyISAM Read Buffer Size",
            "read_rnd_buffer_size": "MyISAM Random Read Buffer Size",
            "innodb_flush_log_at_trx_commit": "InnoDB Flush Log at Commit",
            "innodb_redo_log_capacity": "InnoDB Redo Log Capacity",
            "innodb_thread_concurrency": "InnoDB Thread Concurrency",
            "innodb_autoextend_increment": "InnoDB Autoextend Increment",
            "innodb_buffer_pool_instances": "InnoDB Buffer Pool Instances",
            "innodb_concurrency_tickets": "InnoDB Concurrency Tickets",
            "innodb_old_blocks_time": "InnoDB Old Blocks Time",
            "innodb_stats_on_metadata": "InnoDB Stats on Metadata",
            "innodb_file_per_table": "InnoDB File Per Table",
            "innodb_checksum_algorithm": "InnoDB Checksum Algorithm",
            "flush_time": "Flush Time (s)",
            "join_buffer_size": "Join Buffer Size",
            "max_allowed_packet": "Max Allowed Packet Size",
            "max_connect_errors": "Max Connection Errors",
            "open_files_limit": "Open Files Limit",
            "sort_buffer_size": "Sort Buffer Size",
            "binlog_row_event_max_size": "Binlog Row Event Max Size",
            "sync_source_info": "Sync Source Info",
            "sync_relay_log": "Sync Relay Log",
            "plugin_load": "Plugins to Load",
            "mysqlx_port": "MySQL X Protocol Port",
        }

        # Tooltips for additional information
        self.tooltips = {
            "port": "TCP/IP Port for MySQL connections.",
            "basedir": "Path to the MySQL installation directory.",
            "datadir": "Path to the database root directory.",
            "sql-mode": "SQL modes for MySQL operations. Affects data validation.",
            "log-output": "Format of the general query and slow query logs.",
            "general-log": "Enable or disable the general query log.",
            "max_connections": "Maximum number of concurrent connections allowed.",
            "table_open_cache": "Number of open tables for all threads.",
            "innodb_buffer_pool_size": "Size of the InnoDB buffer pool for caching data and indexes. adjust 50%-70% of total RAM",
            "tmp_table_size": "Maximum size for in-memory temporary tables.",
            "pipe": "Named pipe to use for connections.",
            "socket": "Path to the MySQL socket file.",
            "no-beep": "Disables the beep on error for the MySQL client.",
            "default-character-set": "Default character set for the MySQL client.",
            "skip-networking": "Disables networking to allow only local socket connections.",
            "enable-named-pipe": "Allows named pipe connections on Windows.",
            "shared-memory": "Enables shared memory for MySQL connections.",
            "shared-memory-base-name": "Base name for shared memory.",
            "named-pipe-full-access-group": "Group with full access to named pipe connections.",
            "character-set-server": "Default character set for new databases and tables.",
            "authentication_policy": "Multi-factor authentication policy for MySQL.",
            "default-storage-engine": "Default storage engine for new tables.",
            "general_log_file": "Path to the general query log file.",
            "slow-query-log": "Enables or disables the slow query log.",
            "slow_query_log_file": "Path to the slow query log file.",
            "long_query_time": "Time in seconds to consider a query as slow.",
            "log-error": "Path to the error log file.",
            "log-bin": "Base name for binary log files.",
            "server-id": "Unique identifier for the server in replication setups.",
            "lower_case_table_names": "Configures case sensitivity for table and database names. 0=Case-sensitive, 1=Lowercase, 2=Uppercase.",
            "secure-file-priv": "Restricts file import/export operations to the specified directory.",
            "temptable_max_ram": "Maximum memory for temporary tables.",
            "internal_tmp_mem_storage_engine": "Storage engine for internal temporary tables.",
            "myisam_max_sort_file_size": "Maximum size for temporary files during MyISAM index creation.",
            "myisam_sort_buffer_size": "Buffer size for sorting MyISAM indexes.",
            "key_buffer_size": "Size of the buffer for MyISAM index blocks.",
            "read_buffer_size": "Buffer size for sequential scans on MyISAM tables.",
            "read_rnd_buffer_size": "Buffer size for random reads from MyISAM tables.",
            "innodb_flush_log_at_trx_commit": "Controls InnoDB log flushing at transaction commit. 0=No, 1=Yes, 2=Every second.",
            "innodb_redo_log_capacity": "Size of the redo log files for InnoDB.",
            "innodb_thread_concurrency": "Limits the number of threads executing in InnoDB.",
            "innodb_autoextend_increment": "Increment size for extending auto-extend tablespaces.",
            "innodb_buffer_pool_instances": "Number of buffer pool instances for InnoDB.",
            "innodb_concurrency_tickets": "Concurrency tickets for InnoDB threads.",
            "innodb_old_blocks_time": "Time before moving a block to the new sublist in InnoDB.",
            "innodb_stats_on_metadata": "Enables or disables updating InnoDB stats on metadata queries.",
            "innodb_file_per_table": "Enables individual tablespace files for InnoDB tables.",
            "innodb_checksum_algorithm": "Checksum algorithm for InnoDB tables. 0=none, 1=crc32, 2=strict_crc32, 3=innodb, 4=strict_innodb, 5=none.",
            "flush_time": "Interval for flushing tables to disk.",
            "join_buffer_size": "Buffer size for joins and index scans.",
            "max_allowed_packet": "Maximum packet size for communication buffers.",
            "max_connect_errors": "Maximum allowed failed connection attempts before blocking.",
            "open_files_limit": "Number of open file descriptors allowed for MySQL.",
            "sort_buffer_size": "Buffer size for ORDER BY and GROUP BY operations.",
            "binlog_row_event_max_size": "Maximum size for a row-based binary log event.",
            "sync_source_info": "Sync interval for source info in replication.",
            "sync_relay_log": "Sync interval for relay log in replication.",
            "plugin_load": "Comma-separated list of plugins to load at startup.",
            "mysqlx_port": "Port for MySQL X Protocol connections.",
        }

        # Main widget and layout
        self.main_widget = QWidget()
        # self.main_widget.setStyleSheet("background-color: #323232;")
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_widget)

        # Add a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # Fields dictionary
        self.fields = {}

        # Comment State dictionary
        self.comment_states = {}

        # Build the form
        self.build_form()

        # Save button
        self.save_button = QPushButton("Save Configuration")
        self.save_button.setStyleSheet("background-color: #41d7a7; padding: 15px; color: white; font-size: 14px; border: 1px solid #41d7a7;")
        self.save_button.clicked.connect(self.save_config)
        self.main_layout.addWidget(self.save_button)

    def initialize_default_config(self):
        """Ensure all sections and keys are loaded, adding defaults for missing sections."""
        if self.debug:
            print("Initializing configuration...")

        # Read raw lines to identify existing content
        raw_lines = self.config.get_raw_lines() if hasattr(self.config, 'get_raw_lines') else []
        section = None

        # Parse the raw lines
        for line in raw_lines:
            stripped_line = line.strip()
            if not stripped_line:  # Skip blank lines
                continue

            if stripped_line.startswith("[") and stripped_line.endswith("]"):
                section = stripped_line.strip("[]").lower()
                if not self.config.has_section(section):
                    self.config.add_section(section)
                continue

            if section and "=" in stripped_line:
                key, value = stripped_line.lstrip("#").lstrip(";").split("=", 1)
                key = key.strip()
                value = value.strip()
                is_commented = stripped_line.startswith("#") or stripped_line.startswith(";")
                if is_commented:
                    self.config[section][f"#{key}"] = value
                else:
                    self.config[section][key] = value

        # Check for each required section and add defaults for missing sections
        required_sections = ["client", "mysql", "mysqld"]
        for section in required_sections:
            if not self.config.has_section(section):
                if self.debug:
                    print(f"Section [{section}] missing. Adding with default keys.")
                self.add_default_section(section)

    def add_default_section(self, section):
        """Add a specific default section and its keys."""
        if section == "client":
            self.config.add_section("client")
            self.config["client"]["pipe"] = ""
            self.config["client"]["socket"] = "MYSQL"
            self.config["client"]["port"] = "3306"

        elif section == "mysql":
            self.config.add_section("mysql")
            self.config["mysql"]["no-beep"] = "true"
            self.config["mysql"]["#default-character-set"] = ""

        elif section == "mysqld":
            self.config.add_section("mysqld")
            self.config["mysqld"]["port"] = "3306"
            self.config["mysqld"]["basedir"] = "\"G:/mysql\""
            self.config["mysqld"]["datadir"] = "G:/mysql/data"
            self.config["mysqld"]["authentication_policy"] = "*,,"
            self.config["mysqld"]["default-storage-engine"] = "INNODB"
            self.config["mysqld"]["sql-mode"] = "\"STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION\""
            self.config["mysqld"]["log-output"] = "FILE"
            self.config["mysqld"]["general-log"] = "0"
            self.config["mysqld"]["general_log_file"] = "\"AZ-MA-AS01.log\""
            self.config["mysqld"]["slow-query-log"] = "1"
            self.config["mysqld"]["slow_query_log_file"] = "\"AZ-MA-AS01-slow.log\""
            self.config["mysqld"]["long_query_time"] = "10"
            self.config["mysqld"]["log-error"] = "\"AZ-MA-AS01.err\""
            self.config["mysqld"]["log-bin"] = "\"AZ-MA-AS01-bin\""
            self.config["mysqld"]["server-id"] = "1"
            self.config["mysqld"]["lower_case_table_names"] = "1"
            self.config["mysqld"]["secure-file-priv"] = "\"G:/mysql/uploads\""
            self.config["mysqld"]["max_connections"] = "151"
            self.config["mysqld"]["table_open_cache"] = "4000"
            self.config["mysqld"]["temptable_max_ram"] = "1G"
            self.config["mysqld"]["tmp_table_size"] = "618M"
            self.config["mysqld"]["internal_tmp_mem_storage_engine"] = "TempTable"
            self.config["mysqld"]["myisam_max_sort_file_size"] = "2146435072"
            self.config["mysqld"]["myisam_sort_buffer_size"] = "2G"
            self.config["mysqld"]["key_buffer_size"] = "8M"
            self.config["mysqld"]["read_buffer_size"] = "128K"
            self.config["mysqld"]["read_rnd_buffer_size"] = "256K"
            self.config["mysqld"]["innodb_flush_log_at_trx_commit"] = "1"
            self.config["mysqld"]["innodb_log_buffer_size"] = "16M"
            self.config["mysqld"]["innodb_buffer_pool_size"] = "8G"
            self.config["mysqld"]["innodb_redo_log_capacity"] = "100M"
            self.config["mysqld"]["innodb_thread_concurrency"] = "9"
            self.config["mysqld"]["innodb_autoextend_increment"] = "64"
            self.config["mysqld"]["innodb_buffer_pool_instances"] = "8"
            self.config["mysqld"]["innodb_concurrency_tickets"] = "5000"
            self.config["mysqld"]["innodb_old_blocks_time"] = "1000"
            self.config["mysqld"]["innodb_stats_on_metadata"] = "0"
            self.config["mysqld"]["innodb_file_per_table"] = "1"
            self.config["mysqld"]["innodb_checksum_algorithm"] = "0"
            self.config["mysqld"]["flush_time"] = "0"
            self.config["mysqld"]["join_buffer_size"] = "256K"
            self.config["mysqld"]["max_allowed_packet"] = "128M"
            self.config["mysqld"]["max_connect_errors"] = "100"
            self.config["mysqld"]["open_files_limit"] = "8161"
            self.config["mysqld"]["sort_buffer_size"] = "256K"
            self.config["mysqld"]["binlog_row_event_max_size"] = "8K"
            self.config["mysqld"]["sync_source_info"] = "10000"
            self.config["mysqld"]["sync_relay_log"] = "10000"
            self.config["mysqld"]["mysqlx_port"] = "33060"

    def build_form(self):
        # Define sections and fields
        if self.debug:
            print("Building form...")
        self.add_section("client", [
            ("pipe", "text", "", False),
            ("socket", "text", "MYSQL", False),
            ("port", "number", 3306, True),
        ])
        self.add_section("mysql", [
            ("no-beep", "checkbox", False),
            ("default-character-set", "select", "utf8mb4", ["utf8mb4","latin1","ascii","ucs2","utf8","binary","cp850","cp1251","cp1256","latin2","hebrew","greek","tis620","big5","gb2312","gbk","gb18030"], False),
        ])
        self.add_section("mysqld", [
            ("skip-networking", "checkbox", False, False),
            ("enable-named-pipe", "checkbox", False, False),
            ("shared-memory", "checkbox", False, False),
            ("shared-memory-base-name", "text", "MYSQL", False),
            ("socket", "text", "MYSQL", False),
            ("named-pipe-full-access-group", "text", "", False),
            ("port", "number", 3306, True),
            ("basedir", "path", "./", True),
            ("datadir", "path", "data", True),
            ("character-set-server", "select", "utf8mb4", ["utf8mb4","latin1","ascii","ucs2","utf8","binary","cp850","cp1251","cp1256","latin2","hebrew","greek","tis620","big5","gb2312","gbk","gb18030"], False),
            ("authentication_policy", "text", "*,,", True),
            ("default-storage-engine", "select", "INNODB", ["INNODB", "MyISAM", "MEMORY", "CSV", "ARCHIVE", "FEDERATED", "BLACKHOLE", "NDB"], True),
            ("sql-mode", "multi-select", ["STRICT_TRANS_TABLES","NO_ZERO_IN_DATE","NO_ZERO_DATE","ERROR_FOR_DIVISION_BY_ZERO","NO_ENGINE_SUBSTITUTION"], ["STRICT_TRANS_TABLES","NO_ZERO_IN_DATE","NO_ZERO_DATE","ERROR_FOR_DIVISION_BY_ZERO","NO_ENGINE_SUBSTITUTION","ONLY_FULL_GROUP_BY","ALLOW_INVALID_DATES","ANSI_QUOTES","HIGH_NOT_PRECEDENCE","IGNORE_SPACE","PAD_CHAR_TO_FULL_LENGTH","PIPES_AS_CONCAT"], True),
            ("log-output", "text", "FILE", True),
            ("general-log", "number", 0, True),
            ("general_log_file", "path", "AZ-MA-AS01.log", True),
            ("slow-query-log", "checkbox", True, True),
            ("slow_query_log_file", "path", "AZ-MA-AS01-slow.log", True),
            ("long_query_time", "number", 10, True),
            ("log-error", "path", "AZ-MA-AS01.err", True),
            ("log-bin", "path", "AZ-MA-AS01-bin", False),
            ("server-id", "number", 1, True),
            ("lower_case_table_names", "range", (1, 0, 2), True), # 0=Case-sensitive, 1=Lowercase, 2=Uppercase
            ("secure-file-priv", "path", "G:/mysql/uploads", True),
            ("max_connections", "filesize", (151, 1, 1000), True),  # Pass tuple for filesize type
            ("table_open_cache", "number", 4000, True),
            ("temptable_max_ram", "filesize", (1073741824, 134217728, psutil.virtual_memory().total), True),  # 1GB to Total RAM
            ("tmp_table_size", "filesize", (536870912, 67108864, 1073741824), True),  # 64MB to 1GB, default 64MB
            ("temptable_max_ram", "filesize", (1073741824, 134217728, psutil.virtual_memory().total), True),  # Default 1GB, min 128MB, max Total RAM
            ("internal_tmp_mem_storage_engine", "select", "TempTable", ["TempTable", "MEMORY"], True),
            ("myisam_max_sort_file_size", "filesize", (2146435072, 131072, 2146435072), True),  # Default and max 2GB
            ("myisam_sort_buffer_size", "filesize", (2147483648, 8388608, 2147483648), True),  # Default and max 2GB
            ("key_buffer_size", "filesize", (8388608, 8388608, psutil.virtual_memory().total // 3), True),  # Default 8MB, max 30% of total RAM
            ("read_buffer_size", "filesize", (131072, 131072, 1048576), True),  # Default and max 1MB
            ("read_rnd_buffer_size", "filesize", (262144, 262144, 2097152), True),  # Default 256KB, max 2MB
            ("innodb_flush_log_at_trx_commit", "range", (1, 0, 2), True), # 0=No, 1=Yes, 2=Every second
            ("innodb_buffer_pool_size", "filesize", (134217728, 134217728, psutil.virtual_memory().total), True),  # 128MB to Total RAM
            ("innodb_redo_log_capacity", "filesize", (104857600, 8388608, 1073741824), True),  # 100MB default, 8MB to 1GB
            ("innodb_thread_concurrency", "number", 0, True),  # 0 indicates infinite concurrency
            ("innodb_autoextend_increment", "number", 64, True),
            ("innodb_buffer_pool_instances", "number", 8, True),
            ("innodb_concurrency_tickets", "number", 5000, True),
            ("innodb_old_blocks_time", "number", 1000, True),
            ("innodb_stats_on_metadata", "checkbox", False, True),
            ("innodb_file_per_table", "checkbox", True, True),
            ("innodb_checksum_algorithm", "range", (0, 0, 5), True), # 0=none, 1=crc32, 2=strict_crc32, 3=innodb, 4=strict_innodb, 5=none
            ("flush_time", "number", 0, True),
            ("join_buffer_size", "filesize", (262144, 262144, 1048576), True),  # Default 256KB, max 1MB
            ("max_allowed_packet", "filesize", (134217728, 131072, 1073741824), True),  # Default 128MB, 128KB to 1GB
            ("max_connect_errors", "number", 100, True),
            ("open_files_limit", "number", 8161, True),
            ("sort_buffer_size", "filesize", (262144, 262144, 2097152), True),  # Default 256KB, max 2MB
            ("binlog_row_event_max_size", "filesize", (8192, 256, 65536), True),  # Default 8KB, 256B to 64KB
            ("sync_source_info", "number", 10000, True),
            ("sync_relay_log", "number", 10000, True),
            ("plugin_load", "text", "", False),
            ("mysqlx_port", "number", 33060, True),
        ])

    def add_section(self, title, fields):
        # Section title with chevron
        section_title = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setSpacing(0)

        title_label = QLabel(f"<b>{title}</b>")
        title_label.setStyleSheet("color: #e48e00; background-color: #00618a; padding: 5px; font-size: 16px; text-transform: uppercase;")
        title_label.setAlignment(Qt.AlignLeft)

        chevron = QLabel("▼")
        chevron.setStyleSheet("color: #e48e00; background-color: #00618a; padding: 5px; font-size: 16px;")
        chevron.setAlignment(Qt.AlignRight)
        chevron.setFixedWidth(30)  # Ensures alignment and consistent size

        title_layout.addWidget(title_label, stretch=1)
        title_layout.addWidget(chevron, stretch=0)
        section_title.setLayout(title_layout)
        section_title.setStyleSheet("background-color: #00618a;")  # Apply background across the entire line
        section_title.setCursor(Qt.PointingHandCursor)

        # Section container
        section_container = QFrame()
        section_container.setContentsMargins(0, 0, 0, 0)
        section_layout = QVBoxLayout()
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(0)  # Reduce padding between fields
        section_container.setLayout(section_layout)

        # Add fields to the section
        for field in fields:
            key, field_type = field[:2]

            # Initialize default and options based on field_type
            if field_type in ["text", "password", "number", "path"]:
                default = field[2] if len(field) > 2 else None
                required = field[3] if len(field) > 3 else True  # Default to required=True
                options = None
            elif field_type in ["select", "multi-select"]:
                default = field[2] if len(field) > 2 else None
                options = field[3] if len(field) > 3 else []
                required = field[4] if len(field) > 4 else True  # Default to required=True
            elif field_type in ["filesize", "range"]:
                if len(field) > 2 and isinstance(field[2], tuple) and len(field[2]) == 3:
                    default, min_value, max_value = field[2]
                    required = field[3] if len(field) > 3 else True  # Default to required=True
                    options = (default, min_value, max_value)
                else:
                    raise ValueError(f"Invalid options for filesize/range field '{key}': {field[2]}")
            elif field_type == "checkbox":
                default = field[2] if len(field) > 2 else False
                required = field[3] if len(field) > 3 else True  # Default to required=True
            else:
                raise ValueError(f"Unknown field type '{field_type}' for key '{key}'")

            # Add the appropriate field
            if field_type == "text":
                self.add_text_field(section_layout, title, key, default, required)
            elif field_type == "password":
                self.add_password_field(section_layout, title, key, default, required)
            elif field_type == "number":
                self.add_number_field(section_layout, title, key, default, required)
            elif field_type == "select":
                self.add_select_field(section_layout, title, key, options, default, required)
            elif field_type == "multi-select":
                self.add_multi_select_field(section_layout, title, key, options, default, required)
            elif field_type == "filesize":
                self.add_filesize_field(section_layout, title, key, options, required)
            elif field_type == "range":
                self.add_range_field(section_layout, title, key, options, required)
            elif field_type == "path":
                self.add_path_field(section_layout, title, key, default, required)
            elif field_type == "checkbox":
                self.add_checkbox_field(section_layout, title, key, default, required)

        # Add to scroll layout
        self.scroll_layout.addWidget(section_title)
        self.scroll_layout.addWidget(section_container)

        # Collapse/expand functionality
        section_container.setVisible(True)
        section_title.mousePressEvent = lambda event: self.toggle_section(section_container, chevron)

    def toggle_section(self, section_container, chevron):
        is_visible = section_container.isVisible()
        section_container.setVisible(not is_visible)
        chevron.setText("▼" if is_visible else "▲")

    def get_config_value(self, section, key, default=None):
        """Retrieve value, checking for commented and uncommented keys."""
        section = section.lower()
        key = key.lower()

        if f"#{key}" in self.config[section]:
            return self.config[section][f"#{key}"]
        if key in self.config[section]:
            return self.config[section][key]
        return default

    def get_config_commented(self, section, key):
        """Check if the key is commented."""
        section = section.lower()
        key = key.lower()

        return f"#{key}" in self.config[section] and key not in self.config[section]

    def update_comment_state(self, section, key, state, container):
        if self.debug:
            print(f"update_comment_state triggered for [{section}] {key} with state: {state}")

        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Debugging: Print section content
        if self.debug:
            if section in self.config:
                print(f"Before update: Config for section [{section}]: {dict(self.config[section])}")
            else:
                print(f"Section [{section}] not found in config.")

        # Ensure the section exists in the configuration
        if section not in self.config:
            if self.debug:
                print(f"Section [{section}] not found. Adding dynamically.")
            self.config.add_section(section)

        commented = (state == Qt.Checked)  # Determine if the field is now commented
        if commented:
            # Add comment to the key
            if key in self.config[section]:
                if self.debug:
                    print(f"Found key [{key}] in section [{section}]")
                value = self.config[section].pop(key)  # Remove key from config
                self.config[section][f"#{key}"] = value  # Add commented version
                if self.debug:
                    print(f"Commented: [{section}] {key}")
                self.update_field_background(container, True)  # Update to commented state
        else:
            # Remove comment from the key
            commented_key = f"#{key}"
            if commented_key in self.config[section]:
                if self.debug:
                    print(f"Found commented key [{commented_key}] in section [{section}]")
                value = self.config[section].pop(commented_key)  # Remove commented key
                self.config[section][key] = value  # Add uncommented version
                if self.debug:
                    print(f"Uncommented: [{section}] {key}")
                self.update_field_background(container, False)  # Update to uncommented state

        # Update the `self.fields` dictionary to reflect the new commented state
        field_key = f"{section}:{key}"
        if field_key in self.fields:
            # Extract existing field data
            field_data = self.fields[field_key]
            if len(field_data) == 5:  # Filesize fields have an additional parameter (scale)
                widget, required, _, fieldtype, scale = field_data
                self.fields[field_key] = (widget, required, commented, fieldtype, scale)
            else:
                widget, required, _, fieldtype = field_data
                self.fields[field_key] = (widget, required, commented, fieldtype)

        # Debugging: Print updated config
        if self.debug:
            if section in self.config:
                print(f"After update: Config for section [{section}]: {dict(self.config[section])}")

    def update_field_background(self, container, commented):
        if commented:
            container.setStyleSheet("background-color: #808080; color: #fff;")  # Greyed-out look
        else:
            container.setStyleSheet("")  # Default style

    def add_number_field(self, layout, section, key, default=None, required=True):
        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Check if key or commented key exists, otherwise add default
        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            # Add the key to the config with default value, commented if not required
            if required:
                self.config[section][key] = str(default or 0)
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = str(default or 0)
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        # Get value and commented state
        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)

        # Create the spin box
        spin_box = QSpinBox()
        spin_box.setMaximum(100000)
        spin_box.setMinimum(0)
        spin_box.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #76797C;")

        try:
            spin_box.setValue(int(value))
        except ValueError:
            spin_box.setValue(default or 0)  # Use default if conversion fails

        # Store the field
        self.fields[f"{section}:{key}"] = (spin_box, required, commented, "number")

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)

        # Set the tooltip for the entire row (container)
        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        # Add comment toggle if not required
        if not required:
            # Update background color based on commented state
            self.update_field_background(container, commented)

            # Add checkbox to toggle comment state
            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        # Add label and spin box
        row_layout.addWidget(self.create_row(self.get_label(key), spin_box))

        # Add the container to the layout
        layout.addWidget(container)

    def add_text_field(self, layout, section, key, default=None, required=True):

        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Check if key or commented key exists, otherwise add default
        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            # Add the key to the config with default value, commented if not required
            if required:
                self.config[section][key] = str(default or "")
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = str(default or "")
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        # Get value and commented state
        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)

        # Create the text field
        line_edit = QLineEdit()
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line_edit.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #76797C;")
        line_edit.setText(value)

        # Store the field
        self.fields[f"{section}:{key}"] = (line_edit, required, commented, "text")

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)

        # Set the tooltip for the entire row (container)
        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        # Add comment toggle if not required
        if not required:

            # Update background color based on commented state
            self.update_field_background(container, commented)

            # Add checkbox to toggle comment state
            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        # Add label and field
        row_layout.addWidget(self.create_row(self.get_label(key), line_edit))

        # Add the container to the layout
        layout.addWidget(container)

    def add_password_field(self, layout, section, key, default=None, required=True):
        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Check if key or commented key exists, otherwise add default
        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            # Add the key to the config with default value, commented if not required
            if required:
                self.config[section][key] = str(default or "")
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = str(default or "")
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        # Get value and commented state
        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)

        # Create the password field
        line_edit = QLineEdit()
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line_edit.setEchoMode(QLineEdit.Password)  # Hide input as asterisks or bullets
        line_edit.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #76797C;")
        line_edit.setText(value)

        # Store the field
        self.fields[f"{section}:{key}"] = (line_edit, required, commented, "password")

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)

        # Set the tooltip for the entire row (container)
        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        # Add comment toggle if not required
        if not required:

            # Update background color based on commented state
            self.update_field_background(container, commented)

            # Add checkbox to toggle comment state
            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        # Add label and field
        row_layout.addWidget(self.create_row(self.get_label(key), line_edit))

        # Add the container to the layout
        layout.addWidget(container)

    def add_select_field(self, layout, section, key, options, default=None, required=True):
        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Check if key or commented key exists, otherwise add default
        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            # Add the key to the config with default value, commented if not required
            if required:
                self.config[section][key] = str(default or "")
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = str(default or "")
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        # Get value and commented state
        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)

        # Create the combo box
        combo_box = QComboBox()
        combo_box.addItems(options)
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        combo_box.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #76797C;")

        # Set the value in the combo box
        if value in options:
            combo_box.setCurrentText(value)
        elif default:
            combo_box.setCurrentText(default)

        # Store the field
        self.fields[f"{section}:{key}"] = (combo_box, required, commented, "select")

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)

        # Set the tooltip for the entire row (container)
        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        # Add comment toggle if not required
        if not required:

            # Update background color based on commented state
            self.update_field_background(container, commented)

            # Add checkbox to toggle comment state
            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        # Add label and field
        row_layout.addWidget(self.create_row(self.get_label(key), combo_box))

        # Add the container to the layout
        layout.addWidget(container)

    def add_multi_select_field(self, layout, section, key, options, default=None, required=True):
        section = section.lower()
        key = key.lower()

        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            if required:
                self.config[section][key] = ",".join(default or [])
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = ",".join(default or [])
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)
        selected_items = value.split(",") if value else []

        # Create the ComboBox with checkable items
        combo_box = QComboBox()
        combo_box.setEditable(False)  # Disable typing
        combo_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        combo_box.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #76797C;")
        combo_box.setModel(QtGui.QStandardItemModel(combo_box))  # Use a QStandardItemModel for custom items

        # Add items with checkboxes
        for option in options:
            item = QtGui.QStandardItem(option)  # Create a standard item
            item.setCheckable(True)
            item.setCheckState(Qt.Checked if option in selected_items else Qt.Unchecked)
            combo_box.model().appendRow(item)  # Add the item to the combo box's model

        # Function to update selected items
        def update_selected_items():
            selected_items = [
                combo_box.model().item(i).text() for i in range(combo_box.count())
                if combo_box.model().item(i).checkState() == Qt.Checked
            ]
            value = ",".join(selected_items)
            self.fields[f"{section}:{key}"] = (combo_box, required, commented, "multi-select")  # Update stored field
            if self.debug:
                print(f"Updated [{section}:{key}] to: {value}")

        # Connect item state changes to update_selected_items
        for i in range(combo_box.count()):
            combo_box.model().item(i).setEditable(False)  # Ensure no inline editing
            combo_box.model().itemChanged.connect(update_selected_items)  # Monitor changes to the check state

        self.fields[f"{section}:{key}"] = (combo_box, required, commented, "multi-select")

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        container = QWidget()
        container.setLayout(row_layout)

        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        if not required:
            self.update_field_background(container, commented)

            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        row_layout.addWidget(self.create_row(self.get_label(key), combo_box))
        layout.addWidget(container)

    def add_checkbox_field(self, layout, section, key, default=None, required=True):
        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Check if key or commented key exists, otherwise add default
        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            # Add the key to the config with default value, commented if not required
            if required:
                self.config[section][key] = str(default or "")
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = str(default or "")
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        # Get value and commented state
        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)

        # Create the checkbox
        check_box = QCheckBox()
        check_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Enable checkbox if value is true/uncommented
        if value.lower() in ["1", "true", "yes", "on", ""]:
            check_box.setChecked(True)
        else:
            check_box.setChecked(False)

        # Store the field
        self.fields[f"{section}:{key}"] = (check_box, required, commented, "checkbox")

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)

        # Set the tooltip for the entire row (container)
        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        # Add comment toggle if not required
        if not required:

            # Update background color based on commented state
            self.update_field_background(container, commented)

            # Add checkbox to toggle comment state
            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        # Add label and field
        row_layout.addWidget(self.create_row(self.get_label(key), check_box))

        # Add the container to the layout
        layout.addWidget(container)

    def add_filesize_field(self, layout, section, key, filesize_values, required=True):
        default, min_value, max_value = filesize_values

        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Check if key or commented key exists, otherwise add default
        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            # Add the key to the config with default value, commented if not required
            if required:
                self.config[section][key] = str(default)
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = str(default)
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        # Get value and commented state
        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)

        # Scale values to a manageable range for the slider
        scale = 1024  # Scale by 1024 for KB increments
        min_scaled = min_value // scale
        max_scaled = max_value // scale
        default_scaled = default // scale

        try:
            value_scaled = int(value) // scale
        except ValueError:
            value_scaled = default_scaled

        # Create slider and label
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_scaled)
        slider.setMaximum(max_scaled)
        slider.setValue(value_scaled)
        slider.setTickInterval((max_scaled - min_scaled) // 10 or 1)
        slider.setTickPosition(QSlider.TicksBelow)

        # Function to determine the best unit for the value
        def human_readable_unit(val_scaled):
            val = val_scaled * scale
            if val >= 1024**4:
                return f"{val / 1024**4:.2f} TB"
            elif val >= 1024**3:
                return f"{val / 1024**3:.2f} GB"
            elif val >= 1024**2:
                return f"{val / 1024**2:.2f} MB"
            elif val >= 1024:
                return f"{val / 1024:.2f} KB"
            return f"{val} B"

        # Label to display the current value in human-readable format
        value_label = QLabel(human_readable_unit(value_scaled))
        slider.valueChanged.connect(
            lambda val_scaled: value_label.setText(human_readable_unit(val_scaled))
        )

        # Layout for slider and label
        filesize_layout = QHBoxLayout()
        filesize_layout.addWidget(slider)
        filesize_layout.addWidget(value_label)

        filesize_widget = QWidget()
        filesize_widget.setLayout(filesize_layout)

        # Store the scaled slider value and commented state in the fields dictionary
        self.fields[f"{section}:{key}"] = (slider, required, commented, "filesize", scale)

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)

        # Set the tooltip for the entire row (container)
        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        # Add comment toggle if not required
        if not required:
            # Update background color based on commented state
            self.update_field_background(container, commented)

            # Add checkbox to toggle comment state
            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        # Add label and filesize field
        row_layout.addWidget(self.create_row(self.get_label(key), filesize_widget))

        # Add the container to the layout
        layout.addWidget(container)

    def add_range_field(self, layout, section, key, range_values, required=True):
        default, min_value, max_value = range_values

        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Check if key or commented key exists, otherwise add default
        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            # Add the key to the config with default value, commented if not required
            if required:
                self.config[section][key] = str(default)
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = str(default)
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        # Get value and commented state
        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)

        try:
            value = int(value)
        except ValueError:
            value = default

        # Create slider and label
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(value)
        slider.setTickInterval((max_value - min_value) // 10 or 1)
        slider.setTickPosition(QSlider.TicksBelow)

        # Label to display the current value
        value_label = QLabel(f"{slider.value()}")
        slider.valueChanged.connect(
            lambda val: value_label.setText(f"{val}")
        )

        # Layout for slider and label
        range_layout = QHBoxLayout()
        range_layout.addWidget(slider)
        range_layout.addWidget(value_label)

        range_widget = QWidget()
        range_widget.setLayout(range_layout)

        # Store the slider value and commented state in the fields dictionary
        self.fields[f"{section}:{key}"] = (slider, required, commented, "range")

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)

        # Set the tooltip for the entire row (container)
        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        # Add comment toggle if not required
        if not required:
            # Update background color based on commented state
            self.update_field_background(container, commented)

            # Add checkbox to toggle comment state
            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        # Add label and range field
        row_layout.addWidget(self.create_row(self.get_label(key), range_widget))

        # Add the container to the layout
        layout.addWidget(container)

    def add_path_field(self, layout, section, key, default=None, required=True):
        # Normalize section and key to lowercase
        section = section.lower()
        key = key.lower()

        # Check if key or commented key exists, otherwise add default
        commented_key = f"#{key}"
        if key not in self.config[section] and commented_key not in self.config[section]:
            # Add the key to the config with default value, commented if not required
            default_path = os.path.abspath(os.path.join(self.default_directory, default)) if default else ""
            if required:
                self.config[section][key] = default_path
                if self.debug:
                    print(f"Added key [{key}] to section [{section}] with default value.")
            else:
                self.config[section][commented_key] = default_path
                if self.debug:
                    print(f"Added commented key [{commented_key}] to section [{section}] with default value.")

        # Get value and commented state
        value = self.get_config_value(section, key, default)
        commented = self.get_config_commented(section, key)

        # Create the layout and widgets for the path field
        path_layout = QHBoxLayout()
        line_edit = QLineEdit()
        line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line_edit.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #76797C;")
        line_edit.setText(value)
        browse_button = QPushButton("...")
        browse_button.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #76797C;")
        default_button = QPushButton("Set Default")
        default_button.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #76797C;")

        # Resolve the default path, including support for "../" and "./"
        default_path = os.path.abspath(os.path.join(self.default_directory, default)) if default else ""

        # Connect buttons
        browse_button.clicked.connect(lambda: self.browse_path(line_edit))
        default_button.clicked.connect(lambda: line_edit.setText(default_path))

        # Add widgets to the path layout
        path_layout.addWidget(line_edit)
        path_layout.addWidget(browse_button)
        path_layout.addWidget(default_button)

        # Wrap the path layout in a QWidget
        path_widget = QWidget()
        path_widget.setLayout(path_layout)

        # Store the field
        self.fields[f"{section}:{key}"] = (line_edit, required, commented, "path")

        # Add the row to the layout
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(15, 0, 5, 0)

        # Wrap layout in a QWidget
        container = QWidget()
        container.setLayout(row_layout)

        # Set the tooltip for the entire row (container)
        tooltip = self.get_tooltip(key)
        if tooltip:
            container.setToolTip(tooltip)

        # Add comment toggle if not required
        if not required:

            # Update background color based on commented state
            self.update_field_background(container, commented)

            # Add checkbox to toggle comment state
            toggle_checkbox = QCheckBox()
            toggle_checkbox.setChecked(commented)
            toggle_checkbox.stateChanged.connect(lambda state: self.update_comment_state(section, key, state, container))
            row_layout.addWidget(toggle_checkbox)

        # Add label and path widget
        row_layout.addWidget(self.create_row(self.get_label(key), path_widget))

        # Add the container to the layout
        layout.addWidget(container)

    def create_row(self, label_text, widget):
        row_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(200)
        row_layout.addWidget(label)
        row_layout.addWidget(widget)
        container = QWidget()
        container.setLayout(row_layout)
        return container

    def get_label(self, key):
        return self.labels.get(key, key)

    def get_tooltip(self, key):
        return self.tooltips.get(key, key)

    def browse_path(self, line_edit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory", self.default_directory)
        if path:
            line_edit.setText(path)

    def save_config(self):
        for key, field_data in self.fields.items():
            section, option = key.split(":")
            widget, required, commented, fieldtype = field_data[:4]  # Extract required and commented states
            value = None

            # Debugging: Print field data
            if self.debug:
                print(f"Processing field: {key} in section [{section}] with type: {fieldtype}")
                print(f"Required: {required}, Commented: {commented}")

            # Process value based on field type
            if fieldtype == "filesize":
                slider, scale = widget, field_data[4]
                raw_value = slider.value() * scale
                if raw_value >= 1024**4:
                    value = f"{raw_value / 1024**4:.0f}T"
                elif raw_value >= 1024**3:
                    value = f"{raw_value / 1024**3:.0f}G"
                elif raw_value >= 1024**2:
                    value = f"{raw_value / 1024**2:.0f}M"
                elif raw_value >= 1024:
                    value = f"{raw_value / 1024:.0f}K"
                else:
                    value = f"{raw_value}B"

            elif fieldtype == "multi-select":
                combo_box = widget
                value = ",".join(
                    combo_box.model().item(i).text()
                    for i in range(combo_box.count())
                    if combo_box.model().item(i).checkState() == Qt.Checked
                )

            elif fieldtype == "select":
                combo_box = widget
                value = combo_box.currentText()

            elif fieldtype == "text":
                line_edit = widget
                value = line_edit.text()

            elif fieldtype == "number":
                spin_box = widget
                value = str(spin_box.value())

            elif fieldtype == "checkbox":
                check_box = widget
                value = "1" if check_box.isChecked() else "0"

            # Save the value to the config
            if value is not None:
                if not self.config.has_section(section):
                    self.config.add_section(section)

                # If required, ensure the option is never commented
                if required:
                    self.config.set(section, option, value)
                else:
                    # Optional fields: Comment if explicitly toggled or originally commented
                    if commented:
                        self.config.remove_option(section, option)
                        self.config.set(section, f"#{option}", value)
                    else:
                        self.config.set(section, option, value)

        # Write the updated configuration back to the file
        with open(self.ini_path, "w") as configfile:
            self.config.write(configfile)

        QMessageBox.information(self, "Saved", "Configurations saved successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Dynamically determine the path to my.ini in the same directory as this script
    if getattr(sys, 'frozen', False):
        # If the application is frozen (e.g., running as .app or .exe)
        if sys.platform == "darwin":
            # For macOS, locate the directory containing the .app bundle
            script_directory = os.path.abspath(
                os.path.join(os.path.dirname(sys.executable), '..', '..', '..')
            )
        else:
            # For other platforms, use the executable's directory
            script_directory = os.path.dirname(sys.executable)
    else:
        # If running as a regular script
        script_directory = os.path.dirname(os.path.abspath(__file__))

    ini_file_path = os.path.join(script_directory, "my.ini")

    # Ensure the file exists, or create an empty one
    if not os.path.exists(ini_file_path):
        with open(ini_file_path, "w") as file:
            file.write("")

    window = MySQLConfigurator(ini_file_path)
    window.show()
    sys.exit(app.exec_())
