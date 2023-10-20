import threading
from time import sleep

from animate import Animation


class Line(Animation):
    def __init__(self, app):
        super().__init__(app, 'State: Inserting line')

    # Draws a line to the canvas, with the current insertion line settings (width, colour),
    # allowing the user to see what will be drawn before finalisation.
    def draw_animation(self, init_x: int, init_y: int, event: threading.Event) -> None:
        self.app.mouse["x"], self.app.mouse["y"] = init_x + 1, init_y + 1

        while not event.is_set():
            shape = self.app.canvas.create_line(init_x, init_y, self.app.mouse["x"], self.app.mouse["y"],
                                                width=self.app.line_width.get(), fill=self.app.line_colour)
            sleep(0.1)
            self.app.canvas.delete(shape)

    def stop_animation(self, event) -> None:
        super().stop_animation(event)

        # Draws the desired line to the canvas
        self.app.canvas.create_line(self.app.saved_point["x"], self.app.saved_point["y"],
                                    self.app.saved_point["x2"], self.app.saved_point["y2"],
                                    width=self.app.line_width.get(), fill=self.app.line_colour)

    def start_animation(self, event):
        super().start_animation(event)
