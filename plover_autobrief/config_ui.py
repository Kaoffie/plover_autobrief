"""
This UI originally had just a few configurable options, so
it didn't look so long and full of redundant code. I might
organize this some other day.
"""

from PyQt5.QtWidgets import (
    QDialog, QWidget, QLabel, QSpinBox, QCheckBox,
    QComboBox, QDialogButtonBox, QGridLayout, QLineEdit,
    QFileDialog, QPushButton
)

from plover.engine import StenoEngine

from plover_autobrief.autobrief_config import AutobriefConfig

class ConfigUI(QDialog):

    def __init__(self, temp_config: AutobriefConfig, engine: StenoEngine, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.temp_config = temp_config
        self.engine = engine
        self.setup_window()

    def select_brief_file(self) -> str:
        file_path = QFileDialog.getOpenFileName(
            self,
            "Open Brief Generation Script",
            "",
            "Python scripts (*.py)"
        )[0]

        if file_path:
            self.brief_gen_box.setText(file_path)

    def setup_window(self) -> None:
        self.resize(350, 200)

        self.autoadd_label = QLabel(self)
        self.autoadd_label.setText("Automatically add briefs")
        self.autoadd_box = QCheckBox(self)
        self.autoadd_box.setChecked(self.temp_config.autoadd)

        self.brief_unknown_words_label = QLabel(self)
        self.brief_unknown_words_label.setText("Automatically add briefs")
        self.brief_unknown_words_box = QCheckBox(self)
        self.brief_unknown_words_box.setChecked(self.temp_config.brief_unknown_words)

        self.brief_case_sensitive_label = QLabel(self)
        self.brief_case_sensitive_label.setText("Perform case-sensitive dictionary checks")
        self.brief_case_sensitive_box = QCheckBox(self)
        self.brief_case_sensitive_box.setChecked(self.temp_config.brief_case_sensitive)

        self.brief_cap_phrases_label = QLabel(self)
        self.brief_cap_phrases_label.setText("Brief capitalized phrases")
        self.brief_cap_phrases_box = QCheckBox(self)
        self.brief_cap_phrases_box.setChecked(self.temp_config.brief_cap_phrases)

        self.override_label = QLabel(self)
        self.override_label.setText("Briefs can override existing outlines")
        self.override_box = QCheckBox(self)
        self.override_box.setChecked(self.temp_config.override)

        self.exclude_chars_label = QLabel(self)
        self.exclude_chars_label.setText("Exclude words/phrases with these characters")
        self.exclude_chars_box = QLineEdit(self)
        self.exclude_chars_box.setText(self.temp_config.exclude_chars)

        self.to_dict_label = QLabel(self)
        self.to_dict_label.setText("Save briefs to")
        self.to_dict_box = QComboBox(self)
        self.to_dict_box.addItems([
            dic.path
            for dic in self.engine.dictionaries.dicts
            if not dic.readonly
        ])
        if self.temp_config.to_dict:
            self.to_dict_box.setCurrentText(self.temp_config.to_dict)
        
        self.brief_gen_label = QLabel(self)
        self.brief_gen_label.setText("Python script for generating briefs")
        self.brief_gen_box = QLineEdit(self)
        self.brief_gen_box.setText(self.temp_config.brief_gen)
        self.brief_gen_browse = QPushButton("Browse", self)
        self.brief_gen_browse.clicked.connect(self.select_brief_file)

        self.min_length_label = QLabel(self)
        self.min_length_label.setText("Minimum word/phrase length to brief")
        self.min_length_box = QSpinBox(self)
        self.min_length_box.setValue(self.temp_config.min_length)
        self.min_length_box.setRange(1, 20)

        self.min_strokes_label = QLabel(self)
        self.min_strokes_label.setText("Brief if existing outline longer than")
        self.min_strokes_box = QSpinBox(self)
        self.min_strokes_box.setValue(self.temp_config.min_strokes)
        self.min_strokes_box.setRange(1, 20)

        self.search_depth_label = QLabel(self)
        self.search_depth_label.setText("Maximum buffer search depth")
        self.search_depth_box = QSpinBox(self)
        self.search_depth_box.setValue(self.temp_config.search_depth)
        self.search_depth_box.setRange(2, 10)

        self.row_height_label = QLabel(self)
        self.row_height_label.setText("Row Height")
        self.row_height_box = QSpinBox(self)
        self.row_height_box.setValue(self.temp_config.row_height)
        self.row_height_box.setRange(10, 100)

        self.page_len_label = QLabel(self)
        self.page_len_label.setText("Number of briefs to display")
        self.page_len_box = QSpinBox(self)
        self.page_len_box.setValue(self.temp_config.page_len)
        self.page_len_box.setRange(1, 30)

        self.button_box = QDialogButtonBox(
            (
                QDialogButtonBox.Cancel | 
                QDialogButtonBox.Ok
            ),
            parent=self
        )
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.save_settings)

        self.layout = QGridLayout()
        self.layout.addWidget(self.autoadd_label, 0, 0)
        self.layout.addWidget(self.autoadd_box, 0, 1)
        self.layout.addWidget(self.brief_unknown_words_label, 1, 0)
        self.layout.addWidget(self.brief_unknown_words_box, 1, 1)
        self.layout.addWidget(self.brief_case_sensitive_label, 2, 0)
        self.layout.addWidget(self.brief_case_sensitive_box, 2, 1)
        self.layout.addWidget(self.brief_cap_phrases_label, 3, 0)
        self.layout.addWidget(self.brief_cap_phrases_box, 3, 1)
        self.layout.addWidget(self.override_label, 4, 0)
        self.layout.addWidget(self.override_box, 4, 1)
        self.layout.addWidget(self.exclude_chars_label, 5, 0)
        self.layout.addWidget(self.exclude_chars_box, 5, 1)
        self.layout.addWidget(self.to_dict_label, 6, 0)
        self.layout.addWidget(self.to_dict_box, 6, 1)
        self.layout.addWidget(self.brief_gen_label, 7, 0)
        self.layout.addWidget(self.brief_gen_box, 7, 1)
        self.layout.addWidget(self.brief_gen_browse, 8, 1)
        self.layout.addWidget(self.min_length_label, 9, 0)
        self.layout.addWidget(self.min_length_box, 9, 1)
        self.layout.addWidget(self.min_strokes_label, 10, 0)
        self.layout.addWidget(self.min_strokes_box, 10, 1)
        self.layout.addWidget(self.search_depth_label, 11, 0)
        self.layout.addWidget(self.search_depth_box, 11, 1)
        self.layout.addWidget(self.row_height_label, 12, 0)
        self.layout.addWidget(self.row_height_box, 12, 1)
        self.layout.addWidget(self.page_len_label, 13, 0)
        self.layout.addWidget(self.page_len_box, 13, 1)
        self.layout.addWidget(self.button_box, 14, 1)
        self.setLayout(self.layout)

    def save_settings(self) -> None:
        self.temp_config.autoadd = self.autoadd_box.isChecked()
        self.temp_config.brief_unknown_words = self.brief_cap_phrases_box.isChecked()
        self.temp_config.brief_case_sensitive = self.brief_case_sensitive_box.isChecked()
        self.temp_config.brief_cap_phrases = self.brief_cap_phrases_box.isChecked()
        self.temp_config.override = self.override_box.isChecked()
        self.temp_config.exclude_chars = self.exclude_chars_box.text()
        self.temp_config.to_dict = self.to_dict_box.currentText()
        self.temp_config.brief_gen = self.brief_gen_box.text()
        self.temp_config.min_length = self.min_length_box.value()
        self.temp_config.min_strokes = self.min_strokes_box.value()
        self.temp_config.search_depth = self.search_depth_box.value()
        self.temp_config.row_height = self.row_height_box.value()
        self.temp_config.page_len = self.page_len_box.value()
        
        self.accept()
