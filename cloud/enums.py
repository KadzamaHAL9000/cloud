from enum import Enum, IntEnum


class FontEnum(str, Enum):
    liberation_sans_bold = "Liberation Sans:style=Bold"
    liberation_sans_bold_italic = "Liberation Sans:style=Bold Italic"
    liberation_serif_bold = "Liberation Serif:style=Bold"
    liberation_serif_bold_italic = "Liberation Serif:style=Bold Italic"
    pacifico = "Pacifico"


class ToolEnum(IntEnum):
    first = 0
    second = 1
