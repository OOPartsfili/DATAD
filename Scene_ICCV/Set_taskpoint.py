import carla


def draw_arrow_example(world, start_location, end_location, life_time=180):
    """
    Draw a red arrow in the CARLA world from start_location to end_location.
    Parameters
    ----------
    world : carla.World
        CARLA simulation world.
    start_location : carla.Location
        Arrow starting point.
    end_location : carla.Location
        Arrow ending point.
    life_time : float, optional
        How long (in seconds) the arrow should remain visible (default: 180 s).
    """
    debug = world.debug

    # Arrow appearance parameters
    thickness = 0.3
    arrow_size = 0.3
    arrow_color = carla.Color(255, 0, 0, 0)  # red
    life_time = 180.0                        # seconds
    persistent_lines = False                 # not permanent

    # Draw the arrow
    debug.draw_arrow(
        start_location,
        end_location,
        thickness,
        arrow_size,
        arrow_color,
        life_time,
        persistent_lines,
    )
