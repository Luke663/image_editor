from tkinter import Menu, Canvas, Event, Tk, IntVar
import events
from crop import Crop
from draw_line import Line
from draw_oval import Oval
from draw_square import Square


class Window(object):

    def __init__(self) -> None:
        # Store for the current image and its file path
        self.opened_file_path = None
        self.opened_image = None

        # Used to track mouse positions when needed
        self.mouse = {"x": 0, "y": 0}
        # Used to store points for cropping or inserting shapes/lines
        self.saved_point = {"x": 0, "y": 0, "x2": 0, "y2": 0}

        # State variables
        self.drawing_state = False
        self.animation_state = None
        self.drawing_colour = "red"
        self.line_colour = "black"

        # Index of the 'State' item on the menu bar
        self.STATE_MENU_ITEM_INDEX = 7

        # Allows tracking or resizing events
        self.current_width = 1300
        self.current_height = 721

        # Window initialisation
        self.root = Tk()
        self.root.geometry('1300x721')
        self.root.title('Image Editor')

        # Pen and line width variables
        self.pen_width = IntVar(value=2)
        self.line_width = IntVar(value=2)
        self.available_pen_widths = ["1", "2", "3", "5", "10", "15"]

        # Menu Toolbar
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # ----------------------------------- Menu bar Items --------------------------------------
        # Menu variables for file options
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Open', command=lambda: events.open_picture(self))
        self.file_menu.add_command(label='Save', command=lambda: events.save_picture(self)
                                   if self.opened_image else events.no_image_error())
        self.file_menu.add_command(label='Save as...', command=lambda: events.save_picture_as(self)
                                   if self.opened_image else events.no_image_error())
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=exit)

        # Menu variables for operations
        self.operation_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Operation', menu=self.operation_menu)
        self.operation_menu.add_command(label='Rotate 90°', command=lambda: events.rotate(self)
                                        if self.opened_image else events.no_image_error())
        self.operation_menu.add_command(label='Flip left-right', command=lambda: events.flip_lr(self)
                                        if self.opened_image else events.no_image_error())
        self.operation_menu.add_command(label='Flip top-bottom', command=lambda: events.flip_tb(self)
                                        if self.opened_image else events.no_image_error())
        self.operation_menu.add_separator()
        self.operation_menu.add_command(label='Crop', command=lambda: Crop(self))
        self.operation_menu.add_command(label='Resize', command=lambda: events.resize_image(self))

        # Menu variables for filters
        self.filter_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Filter', menu=self.filter_menu)
        self.filter_menu.add_command(label='Sharpen', command=lambda: events.filter_sharpen(self)
                                     if self.opened_image else events.no_image_error())
        self.filter_menu.add_command(label='Blur', command=lambda: events.filter_blur(self)
                                     if self.opened_image else events.no_image_error())
        self.filter_menu.add_command(label='Black & white', command=lambda: events.filter_black_white(self)
                                     if self.opened_image else events.no_image_error())
        self.filter_menu.add_command(label='Emboss', command=lambda: events.filter_emboss(self)
                                     if self.opened_image else events.no_image_error())

        # Menu variables for inserting
        self.insert_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Insert', menu=self.insert_menu)
        self.insert_menu.add_command(label='Line', command=lambda: Line(self))
        self.insert_menu.add_command(label='Square', command=lambda: Square(self))
        self.insert_menu.add_command(label='Oval', command=lambda: Oval(self))
        self.insert_menu.add_command(label='Image', command=lambda: events.start_image_insert(self))
        self.insert_menu.add_command(label='Footer', command=lambda: events.insert_footer(self))
        self.insert_menu.add_separator()
        self.insert_menu.add_command(label='Line colour:  ▉', command=lambda: events.set_colour(self, True),
                                     foreground=self.line_colour)
        self.line_width_menu = Menu(self.insert_menu, tearoff=0)
        self.insert_menu.add_cascade(label='Select line width', menu=self.line_width_menu)

        for index in range(len(self.available_pen_widths)):
            self.line_width_menu.add_radiobutton(label=self.available_pen_widths[index],
                                                 variable=self.line_width,
                                                 value=int(self.available_pen_widths[index]))

        # Menu variables for exif data
        self.exif_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='EXIF data', menu=self.exif_menu)
        self.exif_menu.add_command(label='View', command=lambda: events.see_exif_data(self)
                                   if self.opened_image else events.no_image_error())
        self.exif_menu.add_command(label='Remove', command=lambda: events.remove_exif_data(self)
                                   if self.opened_image else events.no_image_error())

        # Menu variables for drawing
        self.draw_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Draw options', menu=self.draw_menu)
        self.draw_menu.add_checkbutton(label='Draw', command=lambda: events.initiate_draw(self))
        self.draw_menu.add_command(label='Select colour:  ▉', command=lambda: events.set_colour(self, False),
                                   foreground=self.drawing_colour)

        self.pen_width_menu = Menu(self.draw_menu, tearoff=0)
        self.draw_menu.add_cascade(label='Select pen width', menu=self.pen_width_menu)

        for index in range(len(self.available_pen_widths)):
            self.pen_width_menu.add_radiobutton(label=self.available_pen_widths[index],
                                                variable=self.pen_width,
                                                value=int(self.available_pen_widths[index]))

        # Unhandled bug - removing drawing causes error if image not set, left to allow drawing on nothing
        self.draw_menu.add_command(label='Remove drawing', command=lambda: events.set_image(self, self.opened_image))

        # Display of current action/state (None, Drawing, Cropping)
        self.menu_bar.add_command(label='State: None', state='disabled')

        # ---------------------------------- Canvas -------------------------------------------------
        self.canvas = Canvas(self.root, width=1300, height=721, highlightthickness=0)
        self.canvas.pack(pady=10)

        # Re-size event binding allows centering of the canvas/image as window changes
        self.root.bind('<Configure>', lambda event: events.window_resize(event, self))

    # stores the current mouse position
    def update_mouse(self, event: Event) -> None:
        self.mouse["x"] = event.x
        self.mouse["y"] = event.y
