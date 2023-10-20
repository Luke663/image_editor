import threading


# Template class for animated (rubber-banded) operations such as cropping or adding shapes
class Animation(object):

    # Updates the state indicator on the menu bar and the cursor then sets up the binding
    # to allow the animation/rubber-banding to start upon a left mouse click.
    def __init__(self, app, state_label: str):
        self.app = app
        app.root.config(cursor='tcross')
        app.menu_bar.entryconfig(self.app.STATE_MENU_ITEM_INDEX, label=state_label)

        app.root.bind('<Button-1>', self.start_animation)

    # Each child class has their own implementation of the draw function
    # as each displays to the user different visual feedback.
    def draw_animation(self, init_x: int, init_y: int, event) -> None:
        pass

    # Resets the state (cursor, bindings and state indicator) saving the coordinates
    # of the second left mouse click. Each child class then has a different method call
    # (crop, create_rectangle...)
    def stop_animation(self, event) -> None:
        self.app.animation_state.set()  # flag allows the new animation thread to know when to stop

        self.app.root.unbind('<Motion>')
        self.app.root.unbind('<Button-1>')

        self.app.root.config(cursor='arrow')
        self.app.menu_bar.entryconfig(self.app.STATE_MENU_ITEM_INDEX, label='State: None')

        self.app.saved_point["x2"] = event.x
        self.app.saved_point["y2"] = event.y

    # Upon a left mouse click the coordinates of the cursor are stored then the animation
    # is started providing visual feedback to the user for the operation being performed.
    def start_animation(self, event):
        self.app.saved_point["x"] = event.x
        self.app.saved_point["y"] = event.y

        self.app.root.bind('<Button-1>', self.stop_animation)
        self.app.root.bind('<Motion>', self.app.update_mouse)

        self.app.animation_state = threading.Event()  # Used by the new thread to know when to stop
        anim = threading.Thread(
            target=self.draw_animation,
            args=(event.x, event.y, self.app.animation_state),
            daemon=True)
        anim.start()
