"""Deterministic geometry and continuous, topology-preserving routes."""

from dataclasses import dataclass
from math import hypot
from functools import cached_property


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def mix(self, other, t):
        return Point(self.x + (other.x - self.x) * t, self.y + (other.y - self.y) * t)


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    def port(self, side, fraction=0.5):
        return {
            "left": Point(self.x, self.y + self.h * fraction),
            "right": Point(self.x + self.w, self.y + self.h * fraction),
            "top": Point(self.x + self.w * fraction, self.y),
            "bottom": Point(self.x + self.w * fraction, self.y + self.h),
        }[side]

    def contains(self, p, margin=0):
        return (
            self.x - margin < p.x < self.x + self.w + margin
            and self.y - margin < p.y < self.y + self.h + margin
        )


def smooth(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


@dataclass(frozen=True)
class Route:
    id: str
    points: tuple[Point, ...]

    @cached_property
    def samples(self):
        """Rounded authored corners; one shared path for drawing and token travel.

        Short legs limit the radius. Endpoints and their outward directions stay fixed.
        """
        result = [self.points[0]]
        for a, corner, b in zip(self.points, self.points[1:], self.points[2:]):
            incoming = hypot(corner.x - a.x, corner.y - a.y)
            outgoing = hypot(b.x - corner.x, b.y - corner.y)
            if not incoming or not outgoing:
                result.append(corner)
                continue
            radius = min(16, incoming / 3, outgoing / 3)
            start, end = corner.mix(a, radius / incoming), corner.mix(b, radius / outgoing)
            result.append(start)
            for step in range(1, 13):
                t = step / 12
                result.append(start.mix(corner, t).mix(corner.mix(end, t), t))
        result.append(self.points[-1])
        return tuple(result)

    @cached_property
    def length(self):
        return sum(hypot(b.x - a.x, b.y - a.y) for a, b in zip(self.samples, self.samples[1:]))

    def at(self, u):
        remaining = max(0, min(1, u)) * self.length
        for a, b in zip(self.samples, self.samples[1:]):
            length = hypot(b.x - a.x, b.y - a.y)
            if length and remaining <= length:
                return a.mix(b, remaining / length)
            remaining -= length
        return self.points[-1]

    def validate(self, obstacles=()):
        if len(self.points) < 2 or self.length == 0:
            raise ValueError("Empty route")
        for a, b in zip(self.points, self.points[1:]):
            if a.x != b.x and a.y != b.y:
                raise ValueError("Orthogonal route expected")
            for box in obstacles:
                # Exact open-interior segment/box intersection for orthogonal routes.
                if a.x == b.x:
                    hit = box.x < a.x < box.x + box.w and max(min(a.y, b.y), box.y) < min(
                        max(a.y, b.y), box.y + box.h
                    )
                else:
                    hit = box.y < a.y < box.y + box.h and max(min(a.x, b.x), box.x) < min(
                        max(a.x, b.x), box.x + box.w
                    )
                if hit:
                    raise ValueError(f"Route {self.id} crosses obstacle")


def transfer_layout(position):
    """Authored code→register→memory composition; register moves AND resizes in flight."""
    t = smooth(position / 2)
    code = Box(64, 270, 580, 230)
    register = Box(760 + 40 * t, 320 - 35 * t, 220 + 45 * t, 124)
    memory = Box(1100, 260, 436, 340)
    return code, register, memory


def data_route(source, destination, id="address-flow"):
    # Authored top corridor; unchanged topology and continuously moving endpoint legs.
    lane = min(source.y, destination.y) - 42
    return Route(
        id,
        (
            source,
            Point(source.x + 22, source.y),
            Point(source.x + 22, lane),
            Point(destination.x - 22, lane),
            Point(destination.x - 22, destination.y),
            destination,
        ),
    )
