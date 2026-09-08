"""Centrally clocked controlled replacement for incompatible scene compositions."""

from dataclasses import dataclass


@dataclass
class Transition:
    position: float = 0
    duration: float = 0.28
    paused: bool = False

    @property
    def active(self):
        return self.position < self.duration

    @property
    def opacity(self):
        return max(0.0, 1 - self.position / self.duration)

    def tick(self, delta):
        if delta > 0.5:
            self.paused = True
        if not self.paused:
            self.position = min(self.duration, self.position + max(0, delta))

    def finish(self):
        self.position = self.duration
