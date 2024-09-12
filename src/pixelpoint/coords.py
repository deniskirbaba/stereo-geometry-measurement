import math
from typing import NamedTuple


class Coord(NamedTuple):
    x: float
    y: float


def distances_to_ccs(
    left_camera_to_obj_distance: float,
    right_camera_to_obj_distance: float,
    baseline: float,
) -> tuple[Coord, Coord, Coord]:
    """
    Calculate the coordinates of the cameras and the object in a 2D Cartesian coordinate system.

    Parameters
    ----------
    left_camera_to_obj_distance : float
        Distance from the left camera to the object.
    right_camera_to_obj_distance : float
        Distance from the right camera to the object.
    baseline : float
        The horizontal distance between the two cameras (i.e., the distance between the left and right cameras).

    Returns
    -------
    object_coord : Coord
        The coordinates of the object relative to the camera system.
    left_camera_coord : Coord
        The coordinates of the left camera.
    right_camera_coord : Coord
        The coordinates of the right camera.

    """

    # Coordinates of the cameras
    left_camera_coord = Coord(0, 0)
    right_camera_coord = Coord(baseline, 0)

    # Using the law of cosines to compute the x-coordinate of the object
    cos_angle = (left_camera_to_obj_distance**2 + baseline**2 - right_camera_to_obj_distance**2) / (
        2 * left_camera_to_obj_distance * baseline
    )
    angle = math.acos(cos_angle)

    # Now we can calculate the object's x and y coordinates
    object_x = left_camera_to_obj_distance * math.cos(angle)
    object_y = left_camera_to_obj_distance * math.sin(angle)

    object_coord = Coord(object_x, object_y)

    return object_coord, left_camera_coord, right_camera_coord
