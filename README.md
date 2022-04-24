# Autobrief for Plover
[![PyPI](https://img.shields.io/pypi/v/plover-autobrief)](https://pypi.org/project/plover-autobrief/)
![GitHub](https://img.shields.io/github/license/Kaoffie/plover_autobrief)

Autobrief for Plover is a plugin that automatically detects words that aren't in your dictionaries, and provides you the opportunity to assign briefs to them on the fly, either automatically or manually.

This plugin is still under development and has many missing features. Please stay tuned for more updates in the future!

# Plugin Setup

You will need to set up the plugin before using it! These can be done in the settings menu. You will need to set up:

- A dictionary to save all the temporary briefs to
- An automatic briefing python script (this plugin does not come with one yet!)

The automatic briefing python script should contain a single function, `get_brief`, which takens in a string, and outputs a list of possible briefs. Each brief is represented as a tuple of strokes, and each stroke is represented as a string:

```py
from typing import List, Tuple

def get_briefs(text: str) -> List[Tuple[str, ...]]:
    return ...
```

Without a briefing script, autobrief will add every single word it thinks can be briefed, but will not automatically provide briefs. 

Briefing scripts will come in the future when I get the time to make them.

# Macros

These macros will be useful to you while using the plugin:

- `=ab_prev_page` Previous page
- `=ab_next_page` Next page
- `=ab_commit:n` Add the nth suggested brief to your dictionary (if `autoadd` is not turned on)
- `=ab_define:n` Manually define the nth word on the autobrief list
