from __future__ import annotations

import math
from typing import Callable, Tuple
import pygame

from core.manager import Manager

ColorTuple = Tuple[int, int, int]


def bezier_point(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    t: float,
) -> tuple[float, float]:
    """Cubic bezier curve formula."""
    u = 1.0 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t

    x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
    y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
    return (x, y)


def get_bezier_curve_points(
    start: tuple[int, int],
    end: tuple[int, int],
    segments: int = 28,
    start_side: str = "right",
    end_side: str = "left",
) -> list[tuple[int, int]]:
    """
    Compute points along a smooth bezier curve between start and end pins.
    Accounts for pin exit direction ('left' or 'right') so wires naturally
    arc outwards from IC package pins.
    """
    x1, y1 = start
    x2, y2 = end

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    dist = math.hypot(dx, dy)
    offset = max(35.0, min(140.0, dist * 0.45))

    cp1_x = x1 - offset if start_side == "left" else x1 + offset
    cp1_y = y1

    cp2_x = x2 - offset if end_side == "left" else x2 + offset
    cp2_y = y2

    points: list[tuple[int, int]] = []
    for step in range(segments + 1):
        t = step / float(segments)
        pt = bezier_point(
            (float(x1), float(y1)),
            (float(cp1_x), float(cp1_y)),
            (float(cp2_x), float(cp2_y)),
            (float(x2), float(y2)),
            t,
        )
        points.append((int(round(pt[0])), int(round(pt[1]))))
    return points


class Wire:
    """Represents a visual wire connection between a source node and an input node."""

    def __init__(
        self,
        output_node: int,
        input_node: int,
        get_start_pos: Callable[[], tuple[int, int]],
        get_end_pos: Callable[[], tuple[int, int]],
        get_start_side: Callable[[], str] | None = None,
        get_end_side: Callable[[], str] | None = None,
    ) -> None:
        self.output_node = output_node
        self.input_node = input_node
        self.get_start_pos = get_start_pos
        self.get_end_pos = get_end_pos
        self.get_start_side = get_start_side or (lambda: "right")
        self.get_end_side = get_end_side or (lambda: "left")
        self.is_hovered: bool = False

    def get_points(self) -> list[tuple[int, int]]:
        start = self.get_start_pos()
        end = self.get_end_pos()
        start_side = self.get_start_side()
        end_side = self.get_end_side()
        return get_bezier_curve_points(start, end, start_side=start_side, end_side=end_side)

    def is_near_pos(self, pos: tuple[int, int], tolerance: float = 8.0) -> bool:
        """Check if a point is close to the wire curve."""
        points = self.get_points()
        px, py = pos
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            length_sq = dx * dx + dy * dy
            if length_sq == 0:
                dist = math.hypot(px - x1, py - y1)
            else:
                t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / length_sq))
                proj_x = x1 + t * dx
                proj_y = y1 + t * dy
                dist = math.hypot(px - proj_x, py - proj_y)

            if dist <= tolerance:
                return True
        return False

    def render(self, surface: pygame.Surface) -> None:
        points = self.get_points()
        if len(points) < 2:
            return

        # Wire signal logic level from manager
        signal = Manager.node_values.get(self.output_node, 0)

        if signal == 1:
            wire_color: ColorTuple = (34, 197, 94)  # Vibrant green (HIGH)
            glow_color: ColorTuple = (74, 222, 128)
            line_width = 3
        else:
            wire_color = (100, 116, 139)  # Slate blue-gray (LOW)
            glow_color = (148, 163, 184)
            line_width = 2

        if self.is_hovered:
            # Highlight with yellow/amber when hovered for deletion/inspection
            wire_color = (251, 191, 36)
            line_width = 4

        # Draw wire glow if HIGH or hovered
        if signal == 1 or self.is_hovered:
            glow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.lines(glow_surface, (*glow_color, 75), False, points, line_width + 4)
            surface.blit(glow_surface, (0, 0))

        pygame.draw.lines(surface, wire_color, False, points, line_width)
