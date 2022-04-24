from PyQt5.QtWidgets import (
    QTableWidget, QGridLayout, QHeaderView, 
    QLabel, QAction, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QKeySequence

from plover.engine import StenoEngine
from plover.gui_qt.tool import Tool
from plover.gui_qt.utils import ToolBar

from plover_autobrief.resources_rc import *
from plover_autobrief.autobrief_config import AutobriefConfig, CONFIG_ITEMS
from plover_autobrief.config_ui import ConfigUI

class AutobriefUI(Tool):
    TITLE = "Autobrief"
    ICON = ":/autobrief/survey.svg"
    ROLE = "autobrief"

    def __init__(self, engine: StenoEngine) -> None:
        super().__init__(engine)
        self.engine: StenoEngine = engine
        self.config = AutobriefConfig()
        self.restore_state()
        self.show_window()
        self.finished.connect(self.save_state)

    def _restore_state(self, settings: QSettings) -> None:
        for attr, (_, attr_type) in CONFIG_ITEMS.items():
            if settings.contains(attr):
                setattr(self.config, attr, settings.value(attr, type=attr_type))

        if hasattr(self.config, "brief_gen") and self.config.brief_gen:
                self.config.load_brief_gen()

        self.prev_pin = False
        if settings.contains("pinned") and settings.value("pinned", type=bool):
            self.prev_pin = True
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        if not settings.contains("geometry"):
            self.resize(260, 400)
        
    def _save_state(self, settings: QSettings) -> None:
        for key in CONFIG_ITEMS.keys():
            settings.setValue(key, getattr(self.config, key))

        settings.setValue("pinned", self.pin_action.isChecked())

    def show_window(self) -> None:
        self.suggestions_label = QLabel(self)
        self.suggestions_label.setText("Brief Suggestions")

        self.suggestions_table = QTableWidget(self)
        self.suggestions_table.setRowCount(self.config.page_len)
        self.suggestions_table.setColumnCount(4)
        self.suggestions_table.verticalHeader().setDefaultSectionSize(self.config.row_height)
        self.suggestions_table.setMinimumHeight(self.config.row_height * self.config.page_len + self.config.row_height)
        self.suggestions_table.setAlternatingRowColors(True)
        self.suggestions_table.horizontalHeader().hide()
        self.suggestions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.suggestions_table.verticalHeader().hide()
        self.suggestions_table.setShowGrid(False)
        self.suggestions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.pin_action = QAction(self)
        self.pin_action.setCheckable(True)
        self.pin_action.setChecked(self.prev_pin)
        self.pin_action.setText("Pin window")
        self.pin_action.setToolTip("Keep Autobrief on top.")
        self.pin_action.setIcon(QIcon(":/autobrief/pin.svg"))
        self.pin_action.triggered.connect(self.on_toggle_pin)
        self.pin_action.setShortcut(QKeySequence("Ctrl+P"))

        self.settings_action = QAction(self)
        self.settings_action.setText("Autobrief settings")
        self.settings_action.setText("Configure Autobrief.")
        self.settings_action.setIcon(QIcon(":/autobrief/settings.svg"))
        self.settings_action.triggered.connect(self.on_settings)
        self.settings_action.setShortcut(QKeySequence("Ctrl+S"))

        self.page_label = QLabel(self)
        self.page_label.setText("Page 0 of 0")
        self.page_label.setAlignment(Qt.AlignHCenter)

        self.layout = QGridLayout()
        self.layout.addWidget(self.suggestions_label, 2, 0, 1, 2)
        self.layout.addWidget(self.suggestions_table, 3, 0, 1, 2)
        self.layout.addWidget(ToolBar(
            self.pin_action,
            self.settings_action
        ), 4, 0)
        self.layout.addWidget(self.page_label, 4, 1)
        self.setLayout(self.layout)

        self.show()
    
    def on_toggle_pin(self, _: bool = False) -> None:
        flags = self.windowFlags()

        if self.pin_action.isChecked():
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.show()

    def on_settings(self, *args) -> None:
        config_dialog = ConfigUI(self.config.copy(), self.engine, self)
        if config_dialog.exec():
            self.config = config_dialog.temp_config
            if self.config.brief_gen:
                self.config.load_brief_gen()

            self.suggestions_table.setRowCount(self.config.page_len)
            self.suggestions_table.verticalHeader().setDefaultSectionSize(self.config.row_height)
            self.suggestions_table.setMinimumHeight(self.config.row_height * self.config.page_len + self.config.row_height)

    def get_autobrief_config(self) -> AutobriefConfig:
        return self.config
