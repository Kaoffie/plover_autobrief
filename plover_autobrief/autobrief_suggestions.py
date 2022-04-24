from PyQt5.QtWidgets import QTableWidgetItem

from typing import Tuple, List

from plover.engine import StenoEngine
from plover.formatting import RetroFormatter
from plover.gui_qt.add_translation_dialog import AddTranslationDialog
from plover.steno import Stroke as SystemStroke
from plover.translation import Translation

from plover_autobrief.autobrief_ui import AutobriefUI


StenoOutline = Tuple[str, ...]


def common_prefix(str_x: str, str_y: str) -> str:
    x_len = len(str_x)
    y_len = len(str_y)
    short_len = min(x_len, y_len)
    for index in range(short_len):
        if str_x[index] != str_y[index]:
            return str_x[:index]

    return str_x[:short_len]


class AutobriefSuggestions(AutobriefUI):
    def __init__(self, engine: StenoEngine) -> None:
        super().__init__(engine)

        self._suggestions: List[Tuple[str, StenoOutline, bool]] = []
        self._suggestion_keys = set()
        self._suggestion_briefs = set()
        self._page = 0

        engine.signal_connect("stroked", self.on_stroke)

    def update_table(self) -> None:
        top_index = self._page * self.config.page_len

        page_count = (len(self._suggestions) - 1) // self.config.page_len + 1
        displayed = self._suggestions[top_index:top_index + self.config.page_len]
        display_len = len(displayed)

        for index, (translation, brief, added) in enumerate(displayed):
            self.suggestions_table.setItem(index, 0, QTableWidgetItem(str(index + 1)))
            self.suggestions_table.setItem(index, 1, QTableWidgetItem(translation))
            self.suggestions_table.setItem(index, 2, QTableWidgetItem("/".join(brief)))
            self.suggestions_table.setItem(index, 3, QTableWidgetItem("Added" * added))

        if display_len < self.config.page_len:
            for index in range(display_len, self.config.page_len):
                for col in range(0, 4):
                    self.suggestions_table.setItem(index, col, QTableWidgetItem(""))
        
        self.page_label.setText(f"Page {self._page + 1} of {page_count}")

    def is_valid_stroke(self, stroke: str) -> bool:
        try:
            _ = SystemStroke(stroke)
        except ValueError:
            return False
        
        return True

    def is_valid_outline(self, outline: StenoOutline) -> bool:
        return all(self.is_valid_stroke(s) for s in outline.split("/"))

    def is_briefable(self, text: str) -> bool:
        if (
            text in self._suggestion_keys
            or len(text) < self.config.min_length
            or any(c in self.config.exclude_chars for c in text)
            or self.is_valid_outline(text)
        ):
            return False

        splitted = text.split()
        if len(splitted) > 1:
            if self.config.brief_cap_phrases:
                if not splitted[0][0].isupper():
                    return False
                if not splitted[-1][0].isupper():
                    return False

                cap_count = len([
                    w for w in splitted
                    if len(w) < 5 or w[0].isupper()
                ])

                if cap_count < len(splitted):
                    return False
                
            else:
                return False

        # Don't suggest briefs for words that were from a non-explicit dict entry
        for tl_obj in self.engine.translator_state.prev(2):
            if (
                text in tl_obj.english 
                and len(tl_obj.rtfcre) < self.config.min_strokes
            ):
                return False

        # Don't suggest briefs for all capitalized words
        if len(splitted) == 1:
            lookup_text = text.lower()
        else:
            lookup_text = text
        
        outlines = self.engine.reverse_lookup(lookup_text)
        if not outlines:
            return True

        if min(len(outline) for outline in outlines) >= self.config.min_strokes:
            return True

        return False

    def is_valid_brief(self, brief: StenoOutline) -> bool:
        if any(not self.is_valid_stroke(s) for s in brief):
            return False
        
        if brief in self._suggestion_briefs:
            return False
        
        if not self.config.override:
            return (self.engine.lookup(brief) is None)

        return True
    
    def add_translation_dialog(self, arg_int: int) -> None:
        translation, _, added = self._suggestions[arg_int]

        if not added:
            dialog = AddTranslationDialog(self.engine, self.config.to_dict)
            dialog.add_translation.translation.setText(translation)
            dialog.add_translation.on_translation_edited()
            dialog.setWindowIcon(self.windowIcon())
            dialog.add_translation._focus_strokes()

            def on_finished():
                dialog.deleteLater()

                outlines = self.engine.dictionaries.get(
                    self.config.to_dict
                ).reverse_lookup(translation)

                if outlines:
                    brief = iter(outlines).next()
                    self._suggestions[arg_int] = (
                        translation, 
                        brief, 
                        True
                    )
                    self.update_table()
            
            dialog.finished.connect(on_finished)
            dialog.showNormal()
            dialog.activateWindow()
            dialog.raise_()
    
    def handle_arg_macros(self, autobrief_state: str) -> None:
        autobrief_arg = self.engine._translator.autobrief_arg
        if autobrief_arg and autobrief_arg.isnumeric():
            arg_int = self._page * self.config.page_len + int(autobrief_arg) - 1
            if arg_int >= len(self._suggestions):
                pass

            elif autobrief_state == "commit_brief":
                translation, brief, added = self._suggestions[arg_int]
                if not added and brief:
                    self.engine.add_translation(brief, translation, self.config.to_dict)
                    self._suggestions[arg_int] = (translation, brief, True)

            elif autobrief_state == "define_brief":
                self.add_translation_dialog(arg_int)

    def on_stroke(self, _: tuple) -> None:
        update_suggestions = False
        
        if hasattr(self.engine._translator, "autobrief_state"):
            autobrief_state = self.engine._translator.autobrief_state
            update_suggestions = bool(autobrief_state)
            max_pages = (len(self._suggestions) - 1) // self.config.page_len + 1

            if autobrief_state == "prev_page":
                self._page = (self._page - 1) % max_pages
            
            elif autobrief_state == "next_page":
                self._page = (self._page + 1) % max_pages
            
            elif hasattr(self.engine._translator, "autobrief_arg"):
                self.handle_arg_macros(autobrief_state)
                
            del self.engine._translator.autobrief_state
            del self.engine._translator.autobrief_arg

        else:
            prev_translations: List[Translation] = self.engine.translator_state.prev()
            if not prev_translations:
                return

            retro_formatter: RetroFormatter = RetroFormatter(prev_translations)
            last_words: List[str] = retro_formatter.last_words(self.config.search_depth)[:-1]

            if not last_words:
                return

            lw_length = len(last_words)
            brief_buffer = []

            # Last word
            last_word = last_words[-1].strip()
            if self.is_briefable(last_word):
                briefs = self.config.get_briefs(last_word)
                valid_briefs = [brief for brief in briefs if self.is_valid_brief(brief)]

                if valid_briefs:
                    brief_buffer.append((last_word, valid_briefs[0]))
                elif self.config.no_briefer:
                    brief_buffer.append((last_word, ""))

            # Longest valid phrase that ends with last word
            for index in range(0, lw_length - 2):
                text_to_brief = "".join(last_words[index:lw_length]).strip()
                if self.is_briefable(text_to_brief):
                    briefs = self.config.get_briefs(text_to_brief)
                    valid_briefs = [brief for brief in briefs if self.is_valid_brief(brief)]

                    if valid_briefs:
                        brief_buffer.append((text_to_brief, valid_briefs[0]))
                        break
                    elif self.config.no_briefer:
                        brief_buffer.append((text_to_brief, ""))
                        break

            # Actually add the briefs
            if brief_buffer:
                update_suggestions = True
                for translation, brief in brief_buffer:
                    if self.config.autoadd:
                        self.engine.add_translation(brief, translation, self.config.to_dict)

                    self._suggestions.insert(0, (translation, brief, self.config.autoadd))
                    self._suggestion_keys.add(translation)
                    self._suggestion_briefs.add(brief)
                    
        if update_suggestions:
            self.update_table()
