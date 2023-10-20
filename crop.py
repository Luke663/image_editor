import threading
from time import sleep

import events
from animate import Animation


class Crop(Animation):
    def __init__(self, app):
        super().__init__(app, 'State: Cropping')

    # Draws a red square to the canvas allowing the user to see what will be cropped.
    def draw_animation(self, init_x: int, init_y: int, event: threading.Event) -> None:
        self.app.mouse["x"], self.app.mouse["y"] = init_x + 1, init_y + 1

        while not event.is_set():
            shape = self.app.canvas.create_rectangle(
                init_x, init_y,
                self.app.mouse["x"], self.app.mouse["y"],
                width=2,
                outline='red')
            sleep(0.1)
            self.app.canvas.delete(shape)

    def stop_animation(self, event) -> None:
        super().stop_animation(event)

        # Crops the desired section of the image
        events.crop(self.app,
                    self.app.saved_point["x"], self.app.saved_point["y"],
                    self.app.saved_point["x2"], self.app.saved_point["y2"])

    def start_animation(self, event):
        super().start_animation(event)
