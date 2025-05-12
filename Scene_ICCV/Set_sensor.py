# -*- coding: utf-8 -*-
"""
This module configures sensors and renders custom Pygame images.
Adjust the foreground PNG path near line 55.

Change-log
----------
* Re-wrote ``render`` to use a user-specified PNG, ensuring stable rendering.
* Added ``get_display`` helper.
* Critical bug fix: horizontal flip.
  All cameras with FOV = 120 ° are flipped horizontally—use that FOV with care!
"""

import glob
import os
import sys

import carla
import argparse
import random
import time
import numpy as np
import pygame


class CustomTimer:
    """Light wrapper for ``time.perf_counter`` / ``time.time`` to keep code portable."""
    def __init__(self):
        try:
            self.timer = time.perf_counter
        except AttributeError:           # fallback on older Python
            self.timer = time.time

    def time(self):
        return self.timer()


# ----------------------------------------------------------------------------- 
# Display manager
# -----------------------------------------------------------------------------
# ``grid_size`` is the logical grid—for example [2, 3] means 2 rows × 3 cols.
# ``window_size`` is the actual Pygame window size, here 1280 × 720.
class DisplayManager:
    def __init__(self, grid_size, window_size):
        pygame.init()
        pygame.font.init()

        # Create a Pygame window (the full canvas).
        self.display = pygame.display.set_mode(
            window_size, pygame.HWSURFACE | pygame.DOUBLEBUF
        )

        self.grid_size = grid_size          # logical grid (rows, cols)
        self.window_size = window_size      # full window size (px)

        # List of SensorManager objects handled by this display.
        self.sensor_list = []

        # Foreground PNG (with alpha channel).
        image_path = "asset/123.png"        # ←--- update this path if needed
        self.transparent_image = pygame.image.load(image_path).convert_alpha()

    # --------------------------------------------------------------------- #
    # Convenience helpers
    # --------------------------------------------------------------------- #
    def get_display(self):
        """Return the Pygame display surface."""
        return self.display

    def get_window_size(self):
        """Return full window size as [x, y]."""
        return [int(self.window_size[0]), int(self.window_size[1])]

    def get_display_size(self):
        """Return a single cell’s size in the logical grid as [x, y]."""
        return [
            int(self.window_size[0] / self.grid_size[1]),
            int(self.window_size[1] / self.grid_size[0]),
        ]

    def get_display_offset(self, grid_pos):
        """
        Convert a logical grid position [row, col] to the pixel offset of
        that cell’s top-left corner.
        """
        cell_size = self.get_display_size()
        x0 = int(grid_pos[1] * cell_size[0])
        y0 = int(grid_pos[0] * cell_size[1])
        return [x0, y0]

    # --------------------------------------------------------------------- #
    # Sensor bookkeeping
    # --------------------------------------------------------------------- #
    def add_sensor(self, sensor):
        self.sensor_list.append(sensor)

    def get_sensor_list(self):
        return self.sensor_list

    # --------------------------------------------------------------------- #
    # Rendering
    # --------------------------------------------------------------------- #
    def render(self):
        """Draw every sensor image plus the foreground PNG, then flip."""
        if not self.render_enabled():
            return

        for sensor in self.sensor_list:
            sensor.render()                 # let each sensor blit its surface

        # Foreground overlay (position can be tweaked).
        self.display.blit(self.transparent_image, (400, 0))

        pygame.display.flip()

    # --------------------------------------------------------------------- #
    # Cleanup
    # --------------------------------------------------------------------- #
    def destroy(self):
        for sensor in self.sensor_list:
            sensor.destroy()

    # Is rendering currently enabled?
    def render_enabled(self):
        return self.display is not None


# ----------------------------------------------------------------------------- 
# Sensor manager
# -----------------------------------------------------------------------------
class SensorManager:
    """
    Wrapper around a CARLA sensor that
      • spawns the sensor,
      • converts raw data to a Pygame ``Surface``,
      • knows where to draw itself on the main display.
    """

    def __init__(
        self,
        world,
        display_man,
        sensor_type,
        transform,
        attached,
        sensor_options,
        display_pos,
        sp_flag,
    ):
        # ``sp_flag`` can be [] (no special position) or
        # [[x, y], [w, h]] (custom offset and size).
        self.sp_flag = sp_flag

        self.surface = None
        self.world = world
        self.display_man = display_man
        self.display_pos = display_pos
        self.sensor_options = sensor_options

        self.sensor = self.init_sensor(sensor_type, transform, attached)
        self.timer = CustomTimer()

        # Register with the display manager so it will be rendered.
        self.display_man.add_sensor(self)

    # --------------------------------------------------------------------- #
    # Sensor creation
    # --------------------------------------------------------------------- #
    def init_sensor(self, sensor_type, transform, attached):
        lib = self.world.get_blueprint_library()

        if sensor_type == "RGBCamera":
            bp = lib.find("sensor.camera.rgb")
            disp_size = (
                self.display_man.get_display_size()
                if self.sp_flag == []
                else self.sp_flag[1]
            )
            bp.set_attribute("image_size_x", str(disp_size[0]))
            bp.set_attribute("image_size_y", str(disp_size[1]))
            for k, v in self.sensor_options.items():
                bp.set_attribute(k, v)

            cam = self.world.spawn_actor(bp, transform, attach_to=attached)
            cam.listen(self.save_rgb_image)
            return cam

        if sensor_type == "SS":  # semantic segmentation camera
            bp = lib.find("sensor.camera.semantic_segmentation")
            disp_size = (
                self.display_man.get_display_size()
                if self.sp_flag == []
                else self.sp_flag[1]
            )
            bp.set_attribute("image_size_x", str(disp_size[0]))
            bp.set_attribute("image_size_y", str(disp_size[1]))
            for k, v in self.sensor_options.items():
                bp.set_attribute(k, v)

            cam = self.world.spawn_actor(bp, transform, attach_to=attached)
            cam.listen(self.save_ss_image)
            return cam

        if sensor_type == "IS":  # instance segmentation
            bp = lib.find("sensor.camera.instance_segmentation")
            disp_size = (
                self.display_man.get_display_size()
                if self.sp_flag == []
                else self.sp_flag[1]
            )
            bp.set_attribute("image_size_x", str(disp_size[0]))
            bp.set_attribute("image_size_y", str(disp_size[1]))
            for k, v in self.sensor_options.items():
                bp.set_attribute(k, v)

            cam = self.world.spawn_actor(bp, transform, attach_to=attached)
            cam.listen(self.save_is_image)
            return cam

        return None  # unsupported type

    def get_sensor(self):
        return self.sensor

    # --------------------------------------------------------------------- #
    # Callbacks to convert raw CARLA images into Pygame surfaces
    # --------------------------------------------------------------------- #
    def save_rgb_image(self, image):
        image.convert(carla.ColorConverter.Raw)
        arr = np.frombuffer(image.raw_data, dtype=np.uint8)
        arr = arr.reshape((image.height, image.width, 4))[:, :, :3][:, :, ::-1]

        # Flip horizontally if FOV = 120°
        if self.sensor_options.get("fov") == "120":
            arr = np.fliplr(arr)

        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(arr.swapaxes(0, 1))

    def save_ss_image(self, image):
        image.convert(carla.ColorConverter.CityScapesPalette)
        arr = np.frombuffer(image.raw_data, dtype=np.uint8)
        arr = arr.reshape((image.height, image.width, 4))[:, :, :3][:, :, ::-1]

        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(arr.swapaxes(0, 1))

    def save_is_image(self, image):
        image.convert(carla.ColorConverter.Raw)
        arr = np.frombuffer(image.raw_data, dtype=np.uint8)
        arr = arr.reshape((image.height, image.width, 4))[:, :, :3][:, :, ::-1]

        if self.display_man.render_enabled():
            self.surface = pygame.surfarray.make_surface(arr.swapaxes(0, 1))

    # --------------------------------------------------------------------- #
    # Draw onto the main Pygame surface
    # --------------------------------------------------------------------- #
    def render(self):
        if self.surface is None:
            return

        offset = (
            self.display_man.get_display_offset(self.display_pos)
            if self.sp_flag == []
            else self.sp_flag[0]
        )
        self.display_man.display.blit(self.surface, offset)

    def destroy(self):
        self.sensor.destroy()


# ----------------------------------------------------------------------------- 
# Simulation loop
# -----------------------------------------------------------------------------
def run_simulation(args, client):
    """
    Run one driving episode and render all configured sensors.
    """
    display_manager = None
    vehicle_list = []
    timer = CustomTimer()

    try:
        world = client.get_world()
        original_settings = world.get_settings()

        # ------------------------- World settings ------------------------- #
        if args.sync:
            traffic_manager = client.get_trafficmanager(8000)
            tm_settings = world.get_settings()
            traffic_manager.set_synchronous_mode(True)
            tm_settings.synchronous_mode = True
            tm_settings.fixed_delta_seconds = 0.05
            world.apply_settings(tm_settings)

        # --------------------------- Spawn ego ---------------------------- #
        bp_vehicle = world.get_blueprint_library().filter("model3")[0]
        ego = world.spawn_actor(bp_vehicle, random.choice(world.get_map().get_spawn_points()))
        ego.set_autopilot(True)
        vehicle_list.append(ego)

        # -------------------- Display / sensor setup --------------------- #
        display_manager = DisplayManager(
            grid_size=[1, 3], window_size=[args.width, args.height]
        )
        clock = pygame.time.Clock()

        # Front camera (takes entire width)
        SensorManager(
            world,
            display_manager,
            "RGBCamera",
            carla.Transform(carla.Location(x=2, y=-0.18, z=1.3), carla.Rotation(yaw=0)),
            ego,
            {"fov": "135"},
            display_pos=[0, 1],
            sp_flag=[[0, 0], [5740, 1010]],
        )
        # Left mirror
        SensorManager(
            world,
            display_manager,
            "RGBCamera",
            carla.Transform(carla.Location(x=1.5, y=-1, z=1.1), carla.Rotation(yaw=-140)),
            ego,
            {},
            display_pos=[0, 0],
            sp_flag=[[700, 570], [670, 430]],
        )
        # Right mirror
        SensorManager(
            world,
            display_manager,
            "RGBCamera",
            carla.Transform(carla.Location(x=1.5, y=1, z=1.1), carla.Rotation(yaw=140)),
            ego,
            {},
            display_pos=[0, 2],
            sp_flag=[[4719, 560], [670, 430]],
        )
        # Rearview mirror
        SensorManager(
            world,
            display_manager,
            "RGBCamera",
            carla.Transform(carla.Location(x=-2.2, y=0, z=1.35), carla.Rotation(yaw=180)),
            ego,
            {"fov": "120"},
            display_pos=[1, 1],
            sp_flag=[[2890, 210], [650, 190]],
        )

        # --------------------------- Main loop --------------------------- #
        quit_requested = False
        sim_start = timer.time()

        while True:
            if args.sync:
                world.tick()
            else:
                world.wait_for_tick()

            display_manager.render()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_requested = True
            if quit_requested:
                break

    finally:
        if display_manager:
            display_manager.destroy()

        # Destroy all actors
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicle_list])
        world.apply_settings(original_settings)


# ----------------------------------------------------------------------------- 
# Entry point
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="CARLA sensor rendering demo")
    parser.add_argument("--host", default="127.0.0.1", help="CARLA host (default 127.0.0.1)")
    parser.add_argument("-p", "--port", default=2000, type=int, help="CARLA port (default 2000)")
    parser.add_argument("--sync", action="store_true", help="Run in synchronous mode")
    parser.add_argument(
        "--async", dest="sync", action="store_false", help="Run in asynchronous mode"
    )
    parser.set_defaults(sync=True)
    parser.add_argument(
        "--res", default="5740x1010", metavar="WIDTHxHEIGHT", help="Window resolution"
    )
    args = parser.parse_args()
    args.width, args.height = [int(v) for v in args.res.split("x")]

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(5.0)
        run_simulation(args, client)
    except KeyboardInterrupt:
        print("\nCancelled by user. Bye!")


if __name__ == "__main__":
    main()
