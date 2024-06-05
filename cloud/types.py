from pydantic import BaseModel

from cloud.enums import FontEnum, ToolEnum


class GCodeSettings(BaseModel):
    class Config:
        use_enum_values = True

    delta: float = 2.0
    e_per_mm: float = 0.03
    z: float = 0.25
    f: float = 2400.0
    print_size_mm: float = 120.0
    table_size_mm: float = 200.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    tool: int = ToolEnum.first.value


class OpenSCADModelSettings(BaseModel):
    class Config:
        use_enum_values = True

    text: str = "Chocolate Fiesta"
    depth: int = 5
    width: int = 100
    foundation_depth: int = 2
    foundation_offset: float = 2.0
    foundation_joiner_height: float = 7.0
    text_spacing: float = 1.0
    font: str = FontEnum.pacifico.value
