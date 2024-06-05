from __future__ import annotations

from typing import Optional

import plotly.graph_objects as go
from loguru import logger

from cloud.db.base import Database
from cloud.models import Drawing
from cloud.types import GCodeSettings


class Curve:
    def __init__(
        self, x: list[float] = None, y: list[float] = None, z: float = 0.2
    ) -> None:
        self.x = x or []
        self.y = y or []
        self.z = z

    def distribute(self, delta: float) -> Curve:
        delta = float(delta)
        x_distributed = [self.x[0]]
        y_distributed = [self.y[0]]
        for _x, _y in zip(self.x, self.y):
            x = x_distributed[-1]
            y = y_distributed[-1]
            while self.distance(x, y, _x, _y) > delta:
                dist = self.distance(x, y, _x, _y)
                x = x + delta * (_x - x) / dist
                y = y + delta * (_y - y) / dist
                x_distributed.append(x)
                y_distributed.append(y)
        self.x = x_distributed
        self.y = y_distributed
        return self

    def scale(self, factor: float) -> Curve:
        self.x = [x * factor for x in self.x]
        self.y = [y * factor for y in self.y]
        return self

    def translate(self, x_trans: float, y_trans: float) -> Curve:
        self.x = [x + x_trans for x in self.x]
        self.y = [y + y_trans for y in self.y]
        return self

    def mirror_over_x(self) -> Curve:
        self.y = [-y for y in self.y]
        return self

    @staticmethod
    def distance(x_a: float, y_a: float, x_b: float, y_b: float) -> float:
        return ((x_a - x_b) ** 2 + (y_a - y_b) ** 2) ** 0.5


class CurvesGenerator:
    def __init__(
        self, drawing: Drawing, settings: Optional[GCodeSettings] = None
    ) -> None:
        self.settings = settings or GCodeSettings()
        self.drawing = drawing
        self.curves: list[Curve] = []

    def __call__(self) -> list[Curve]:
        self.create_curves()
        self.mirror_over_x()
        self.fit_into_table()
        self.distribute()
        return self.curves

    def create_curves(self) -> None:
        curve = Curve()
        for i, (x, y) in enumerate(zip(self.drawing.x, self.drawing.y)):
            curve.x.append(x)
            curve.y.append(y)
            if i in self.drawing.stops:
                if len(curve.x) > 1:
                    self.curves.append(curve)
                curve = Curve()
        if len(curve.x) > 1:
            self.curves.append(curve)

    @property
    def x_max(self) -> float:
        return max(max(c.x) for c in self.curves)

    @property
    def y_max(self) -> float:
        return max(max(c.y) for c in self.curves)

    @property
    def x_min(self) -> float:
        return min(min(c.x) for c in self.curves)

    @property
    def y_min(self) -> float:
        return min(min(c.y) for c in self.curves)

    def distribute(self) -> None:
        self.curves = [c.distribute(self.settings.delta) for c in self.curves]

    def scale(self, scale_factor: float) -> None:
        self.curves = [c.scale(scale_factor) for c in self.curves]

    def mirror_over_x(self) -> None:
        self.curves = [c.mirror_over_x() for c in self.curves]

    def translate(self, x_trans: float, y_trans: float) -> None:
        self.curves = [c.translate(x_trans, y_trans) for c in self.curves]

    def fit_into(
        self,
        w_min: float,
        w_max: float,
        h_min: Optional[float] = None,
        h_max: Optional[float] = None,
    ) -> None:
        h_min = h_min or w_min
        h_max = h_max or w_max
        x_span = self.x_max - self.x_min
        y_span = self.y_max - self.y_min
        scale_factor = min((w_max - w_min) / x_span, (h_max - h_min) / y_span)
        self.scale(scale_factor)
        self.translate(
            (w_max + w_min - self.x_max - self.x_min) / 2,
            (h_max + h_min - self.y_max - self.y_min) / 2,
        )

    def fit_into_table(self) -> None:
        self.fit_into(
            self.settings.table_size_mm / 2 - self.settings.print_size_mm / 2,
            self.settings.table_size_mm / 2 + self.settings.print_size_mm / 2,
        )


def build_plot(curves: list[Curve]) -> str:
    fig = go.Figure()
    for c in curves:
        fig.add_trace(go.Scatter(x=c.x, y=c.y, mode="lines+markers", name="markers"))
    return fig.to_json()


class UserDrawingService:
    def __init__(self, user_uid: str, settings: GCodeSettings, db: Database) -> None:
        self.user_uuid = user_uid
        self.settings = settings
        self.db = db

    def __call__(self) -> str:
        try:
            drawing = Drawing.get_by_user(user_uuid=self.user_uuid, db=self.db)
        except FileNotFoundError:
            logger.warning(f"User has no drawing. User: {self.user_uuid}.")
            raise

        if drawing.plot and drawing.settings == self.settings.dict():
            logger.info(
                f"Drawing with the settings found in db. User: {self.user_uuid}."
            )
            return drawing.plot

        logger.info(f"Generating Plot and GCODE for user {self.user_uuid}")

        curves_generator = CurvesGenerator(drawing, self.settings)
        curves = curves_generator()
        gcode_generator = GCodeGenerator(curves, self.settings)

        drawing.gcode = gcode_generator()
        drawing.plot = build_plot(curves)
        drawing.settings = self.settings.dict()
        drawing.save_for_user(
            user_uid=self.user_uuid, update_fields=["plot", "settings"], db=self.db
        )

        return drawing.plot


class GCodeGenerator:
    def __init__(self, curves: list[Curve], settings: GCodeSettings) -> None:
        self.commands: list[str] = []
        self.curves = curves
        self.settings = settings
        self.preparation = [
            "; Preparation commands",
            "G90",
            "M82",
            "M106 S0",
            "M104 S42 T0",
            "M104 S39 T1",
            "M109 S42 T0",
            "M109 S39 T1",
            "G28",
            "G29",
            f"T{settings.tool}",
            "G92 E0.0000",
            "G1 E-0.2000 F2700",
        ]
        self.finalization = [
            "; Finalisation commands",
            "G92 E0.0000",
            "G1 E-0.2000 F2700",
            "G1 Z30",
            "G28 X0 Y0",
            "M84",
        ]

    def __call__(self) -> str:
        for c in self.curves:
            self.move_to(c.x[0], c.y[0])
            self.print(c.x, c.y)
        return "\n".join(self.preparation + self.commands + self.finalization)

    def comment(self, message: str) -> None:
        self.commands.append(f"; {message}")

    def print(self, x_list: list[float], y_list: list[float]) -> None:
        e_step = self.settings.delta * self.settings.e_per_mm
        e = 0.0
        self.comment(f"Printing with e_step={e_step}")
        self.commands.append(self.G92(e=0))
        for x, y in zip(x_list, y_list):
            e += e_step
            self.commands.append(self.G1(x=x, y=y, e=e, f=self.settings.f))
        self.commands.append(self.G92(e=0))

    def move_to(self, x: float, y: float) -> None:
        z = self.settings.z
        self.comment(f"Moving to {x:.2f}, {y:.2f}, {z:.2f}")
        self.commands.append(self.G1(z=z * 5, f=1000))
        self.commands.append(self.G1(x=x, y=y, f=4800))
        self.commands.append(self.G1(z=z, f=2700))

    def G(
        self,
        cmd: str,
        *,
        x: float = None,
        y: float = None,
        z: float = None,
        f: float = None,
        e: float = None,
    ) -> str:
        X = f"X{x + self.settings.offset_x:.3f}" if x is not None else ""
        Y = f"Y{y + self.settings.offset_y:.3f}" if y is not None else ""
        Z = f"Z{z:.3f}" if z is not None else ""
        F = f"F{f:.0f}" if f is not None else ""
        E = f"E{e:.4f}" if e is not None else ""
        return f"G{cmd} {X} {Y} {Z} {E} {F}"

    def G1(
        self,
        *,
        x: float = None,
        y: float = None,
        z: float = None,
        f: float = None,
        e: float = None,
    ) -> str:
        return self.G("1", x=x, y=y, z=z, f=f, e=e)

    def G92(
        self,
        *,
        x: float = None,
        y: float = None,
        z: float = None,
        f: float = None,
        e: float = None,
    ) -> str:
        return self.G("92", x=x, y=y, z=z, f=f, e=e)
