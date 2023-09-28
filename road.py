from dataclasses import dataclass


@dataclass
class Road:
    horizental: bool
    top: int
    left_lanes: int
    right_lanes: int