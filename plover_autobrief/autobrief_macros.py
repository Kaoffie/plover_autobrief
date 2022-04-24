from plover.translation import Translator
from plover.steno import Stroke


def prev_page(translator: Translator, stroke: Stroke, argument: str):
    translator.autobrief_state = "prev_page"


def next_page(translator: Translator, stroke: Stroke, argument: str):
    translator.autobrief_state = "next_page"


def commit_brief(translator: Translator, stroke: Stroke, argument: str):
    translator.autobrief_state = "commit_brief"
    translator.autobrief_arg = argument


def define_brief(translator: Translator, stroke: Stroke, argument: str):
    translator.autobrief_state = "define_brief"
    translator.autobrief_arg = argument
