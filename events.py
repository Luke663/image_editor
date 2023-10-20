from tkinter import filedialog, messagebox, colorchooser, Canvas, Event, Text, simpledialog
from PIL import Image, ImageOps, ImageFilter, ImageGrab, ExifTags, ImageTk


def set_image(app, image: Image) -> None:
    """
    Adds the desired image to the canvas, resizing the canvas to the size of the image
    and centering the canvas in the window.
    :param app: (Window) main window class providing access to application variables.
    :param image: (PIL.Image) The image to be added to the canvas.
    """
    app.opened_image = image

    # x, y of top left corner of canvas to allow it to be centered
    x = (app.root.winfo_width() // 2) - (image.width // 2)
    y = (app.root.winfo_height() // 2) - (image.height // 2)

    app.canvas.place_configure(x=x, y=y, width=image.width, height=image.height)

    image_p = ImageTk.PhotoImage(image)
    app.canvas.image = image_p
    app.canvas.create_image(0, 0, image=image_p, anchor='nw')


def _calculate_scale(app, image: Image) -> (int, int):
    """
    Calculates the required width, height for the currently being loaded image to fit in
    the canvas at its current size. Incrementally reducing the current height and width
    by 1% to maintain aspect ratio.
    :param app: (Window) main window class providing access to application variables.
    :param image: (PIL.Image) Image to be loaded onto the canvas requiring scaling.
    :return: Tuple(int, int) the calculated width and height for the scaled image.
    """
    width, height = image.width, image.height
    width_max, height_max = app.root.winfo_width(), app.root.winfo_height()

    # Calculates 1% of the width and height
    increment_width, increment_height = width / 100, height / 100

    # Inefficient but sufficient for this application as no other processes run simultaneously.
    while width > width_max or height > height_max:
        width -= increment_width
        height -= increment_height

    return int(width), int(height)


def _get_image_coordinates(app) -> (int, int, int, int):
    """
    Gets the x,y of the top left and bottom right corners of the canvas for
    cropping and saving.
    :param app: (Window) main window class providing access to application variables.
    :return: Tuple(int, int, int, int) x top-left, y top-left, x bottom-right, y bottom-right
    """
    x = app.canvas.winfo_rootx()
    y = app.canvas.winfo_rooty()
    x2 = x + app.opened_image.width
    y2 = y + app.opened_image.height

    return x, y, x2, y2


def open_picture(app) -> None:
    """
    Opens the desired image, displaying it on the canvas.
    :param app: (Window) main window class providing access to application variables.
    """
    filepath = filedialog.askopenfilename()

    if not filepath:
        return

    app.opened_file_path = filepath
    image = Image.open(filepath)

    width, height = _calculate_scale(app, image)
    set_image(app, image.resize((width, height)))


def save_picture(app) -> None:
    """
    Re-writes the opened image (file path) with the current image on the canvas
    (If confirmation is given).
    :param app: (Window) main window class providing access to application variables.
    """
    if not messagebox.askokcancel(
            title='Confirm',
            message='Are you sure you wish to overwrite the file?'):
        return

    x, y, x2, y2 = _get_image_coordinates(app)

    saved_image = ImageGrab.grab().crop((x, y, x2, y2))
    saved_image.save(app.opened_file_path)
    set_image(app, saved_image)


def save_picture_as(app) -> None:
    """
    Allows the user to save the current canvas as an image with a user specified filename.
    :param app: (Window) main window class providing access to application variables.
    """
    new_path = filedialog.asksaveasfile(defaultextension='.png',
                                        filetypes=[('Image', '.png'), ('All files', '.*')])
    if not new_path:
        return

    x, y, x2, y2 = _get_image_coordinates(app)

    saved_image = ImageGrab.grab().crop((x, y, x2, y2))
    saved_image.save(new_path.name)
    set_image(app, saved_image)


def window_resize(event: Event, app) -> None:
    """
    Positions the canvas at the center of the window upon resizing/maximising. (Removes drawing
    or inserted items that haven't been saved).
    :param event: (Tkinter.Event) accessor to triggered event variables.
    :param app: (Window) main window class providing access to application variables.
    """
    if app.opened_image is None or\
            (app.root.winfo_width() == app.current_width and app.root.winfo_height() == app.current_height):
        return

    app.current_width = app.root.winfo_width()
    app.current_height = app.root.winfo_height()
    set_image(app, app.opened_image)


def filter_black_white(app) -> None:
    """
    Applies the grayscale PIL filter to the currently opened image.
    :param app: (Window) main window class providing access to application variables.
    """
    image = ImageOps.grayscale(app.opened_image)
    set_image(app, image)


def filter_blur(app) -> None:
    """
    Applies the blur PIL filter to the currently opened image.
    :param app: (Window) main window class providing access to application variables.
    """
    image = app.opened_image.filter(ImageFilter.BLUR)
    set_image(app, image)


def filter_emboss(app) -> None:
    """
    Applies the emboss PIL filter to the currently opened image.
    :param app: (Window) main window class providing access to application variables.
    """
    image = app.opened_image.filter(ImageFilter.EMBOSS)
    set_image(app, image)


def filter_sharpen(app) -> None:
    """
    Applies the sharpen PIL filter to the currently opened image.
    :param app: (Window) main window class providing access to application variables.
    """
    image = app.opened_image.filter(ImageFilter.SHARPEN)
    set_image(app, image)


def crop(app, x, y, x2, y2) -> None:
    """
    Crops the desired part of the currently opened image then applies this to the canvas.
    :param app: (Window) main window class providing access to application variables.
    :param x: (int) x coordinate of the top left corner of the canvas.
    :param y: (int) y coordinate of the top left corner of the canvas.
    :param x2: (int) x coordinate of the bottom right corner of the canvas.
    :param y2: (int) y coordinate of the bottom right corner of the canvas.
    """
    # Prevents errors by switching x and y coordinates to maintain the needed
    # top-left THEN bottom-right order of the coordinates.
    if x2 < x:
        x, x2 = x2, x

    if y2 < y:
        y, y2 = y2, y

    image = app.opened_image.crop((x, y, x2, y2))
    set_image(app, image)


def resize_image(app) -> None:
    """
    Allows the user to enter a width and height (via prompts) and resize the
    canvas image at will.
    :param app: (Window) main window class providing access to application variables.
    """
    width, height = app.opened_image.width, app.opened_image.height

    width = simpledialog.askinteger(
        title='Enter new width',
        prompt=f'Enter the new image width\n(the current width is {width}).')

    height = simpledialog.askinteger(
        title='Enter new width',
        prompt=f'Enter the new image height\n(the current height is {height}).')

    set_image(app, app.opened_image.resize((width, height)))


def rotate(app) -> None:
    """
    Rotates the currently opened image 90 degrees.
    :param app: (Window) main window class providing access to application variables.
    """
    image = app.opened_image.transpose(Image.ROTATE_90)
    width, height = _calculate_scale(app, image)
    set_image(app, image.resize((width, height)))


def flip_lr(app) -> None:
    """
    Flips the currently opened image around the vertical axis.
    :param app: (Window) main window class providing access to application variables.
    """
    image = app.opened_image.transpose(Image.FLIP_LEFT_RIGHT)
    width, height = _calculate_scale(app, image)
    set_image(app, image.resize((width, height)))


def flip_tb(app) -> None:
    """
    Flips the currently opened image around the horizontal axis.
    :param app: (Window) main window class providing access to application variables.
    """
    image = app.opened_image.transpose(Image.FLIP_TOP_BOTTOM)
    width, height = _calculate_scale(app, image)
    set_image(app, image.resize((width, height)))


def see_exif_data(app) -> None:
    """
    Displays a pop-up with any EXIF data retrieved from the current image.
    :param app: (Window) main window class providing access to application variables.
    """
    data = app.opened_image.getexif()
    data_list = ""

    if not data:
        data_list = "No data."
    else:
        for key, item in data.items():
            if key in ExifTags.TAGS:
                data_list += f"{ExifTags.TAGS[key]}:\t{item}\n"
            else:
                data_list += f"Ukn. -> {key}: {item}\n"

    messagebox.showinfo(title='EXIF Data', message=data_list)


def remove_exif_data(app) -> None:
    """
    Applies a duplicate image, the same as the current one, to the canvas with no EXIF data.
    :param app: (Window) main window class providing access to application variables.
    """
    image = app.opened_image

    img_pixel_data = list(image.getdata())
    new_image = Image.new(image.mode, image.size)
    new_image.putdata(img_pixel_data)
    set_image(app, new_image)

    messagebox.showinfo(title='EXIF Data', message='Data removed.')


def no_image_error() -> None:
    """
    Error message provided when operations are called that require an image
    but one has not been opened.
    """
    messagebox.showerror(title='Error', message='No image has been opened!')


def set_colour(app, is_line: bool) -> None:
    """
    Sets the chosen colour for either drawing or inserting shapes.
    :param app: (Window) main window class providing access to application variables.
    :param is_line: (Bool) Identifies if the request is to alter line colour or drawing colour.
    """
    if is_line:  # Set line colour
        app.line_colour = colorchooser.askcolor(title='Select line colour')[1]
        app.insert_menu.entryconfig(6, foreground=app.line_colour)
    else:  # Set drawing colour
        app.drawing_colour = colorchooser.askcolor(title='Select pen colour')[1]
        app.draw_menu.entryconfig(1, foreground=app.drawing_colour)


def initiate_draw(app) -> None:
    """
    If not currently drawing, sets the state and cursor to drawing mode and the binding to
    allow drawing. If already drawing it undoes that. (Called by clicking the 'Draw' option
    in the menu).
    :param app: (Window) main window class providing access to application variables.
    """
    if not app.drawing_state:
        app.root.config(cursor='pencil')
        app.drawing_state = True
        app.root.bind('<B1-Motion>', lambda event: draw(event, app))
        app.menu_bar.entryconfig(app.STATE_MENU_ITEM_INDEX, label='State: Drawing')
    else:
        app.root.config(cursor='arrow')
        app.drawing_state = False
        app.root.unbind('<B1-Motion>')
        app.menu_bar.entryconfig(app.STATE_MENU_ITEM_INDEX, label='State: None')


def draw(event: Event, app) -> None:
    """
    Called repetitively via the '<B1-Motion>' binding to add a small circle (size set by
    pen width in the drawing menu) to the canvas when mouse left-click is held and dragged
    to simulate drawing.
    :param event: (Tkinter.Event) accessor to triggered event variables.
    :param app: (Window) main window class providing access to application variables.
    """
    x = event.x - app.pen_width.get()
    y = event.y - app.pen_width.get()
    x2 = event.x + app.pen_width.get()
    y2 = event.y + app.pen_width.get()

    app.canvas.create_oval(x, y, x2, y2, fill=app.drawing_colour, outline='')


def start_image_insert(app) -> None:
    """
    Provides visual feedback and sets binding to allow the user to place an additional
    image on the canvas.
    :param app: (Window) main window class providing access to application variables.
    """
    app.root.bind('<Button-1>', lambda event: insert_image(event, app))
    app.root.config(cursor='icon')
    app.menu_bar.entryconfig(app.STATE_MENU_ITEM_INDEX, label='State: Inserting image')


def insert_image(event: Event, app) -> None:
    """
    Inserts an additional image, adding it on top of the canvas.
    :param event: (Tkinter.Event) accessor to triggered event variables.
    :param app: (Window) main window class providing access to application variables.
    """
    # Reset the visual state of the window
    app.root.unbind('<Button-1>')
    app.root.config(cursor='arrow')
    app.menu_bar.entryconfig(app.STATE_MENU_ITEM_INDEX, label='State: None')

    path = filedialog.askopenfilename(title='Select new image')

    if path is None:
        return

    # Prompt user for desired image size (currently square only)
    width = height = simpledialog.askinteger(
        title='Enter image dimensions',
        prompt='Enter the width/height for the square image.')

    if width is None:
        return

    # Limits size of inserted image (currently arbitrary values)
    if width < 30 or width > 500:
        messagebox.showerror(title='Error', message='Input must be between 30 and 500.')
        return

    im = ImageTk.PhotoImage(Image.open(path).resize((width, height)))

    window_canvas = Canvas(app.canvas, width=width, height=height, highlightthickness=0)
    window_canvas.image = im
    window_canvas.create_image(0, 0, image=im, anchor='nw')

    app.canvas.create_window((event.x, event.y), window=window_canvas, width=width, height=height)


def insert_footer(app) -> None:
    """
    Adds a 60 pixel high footer to the bottom of the current image to allow a
    description or notes to be added (fixed font of 'Arial 10').
    :param app: (Window) main window class providing access to application variables.
    """
    x, y = 0, app.opened_image.height - 60

    footer = Text(app.canvas, font='Arial 10', padx=10, pady=5, border=2, takefocus=0)
    app.canvas.create_window((x, y), window=footer, width=app.canvas.winfo_width(), height=60, anchor='nw')

    # Binding to allow the removal of focus on the footer.
    footer.bind('<FocusIn>', lambda event: _prepare_footer_focus_removal(event, app))
    footer.focus_force()


def _prepare_footer_focus_removal(event: Event, app) -> None:
    """
    Adds binding to the mouse left button to allow removal of footer focus by
    clicking on the canvas (otherwise the footer remains in focus).
    :param event: (Tkinter.Event) accessor to triggered event variables.
    :param app: (Window) main window class providing access to application variables.
    """
    app.root.bind('<Button-1>', lambda _event: _remove_footer_focus(_event, app))


def _remove_footer_focus(event: Event, app) -> None:
    """
    Forces focus back to the canvas, removing the caret from the text widget and
    undoing the mouse left-click binding.
    :param event: (Tkinter.Event) accessor to triggered event variables.
    :param app: (Window) main window class providing access to application variables.
    """
    app.root.unbind('<Button-1>')
    app.canvas.focus_force()
