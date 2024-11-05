# This program is licensed under the GNU Affero General Public License (AGPL) v3.0.
# Copyright (C) 2024 Ahmed Akyol
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# Author: Ahmed Akyol
# Contact: ahmedakyll@gmail.com

from tkinter import *
from tkinter import ttk
import os
from tkinter import filedialog
import random
import shutil
from tkinter import messagebox
import sys

IMAGE = None
DATA = None
train_rat = None
val_rat = None
test_rat = None
img_count = None

class RatioSlider(Frame):
    def __init__(self, master=None, width=400, height=100, callback=None):
        # Initialize the parent Frame class with specified width and height
        super().__init__(master, width=width, height=height)
        self.master = master  # Store the reference to the parent widget
        self.width = width  # Set the width of the slider
        self.height = height  # Set the height of the slider
        self.callback = callback  # Store a callback function if provided

        # Create a canvas to draw the slider bars
        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.canvas.pack()

        # Initial values for train and validation ratios
        self.train_pos = 0.6  # Train ratio starts at 60%
        self.valid_pos = 0.8  # Validation ratio starts at 80% (60% train + 20% validation)
        self.step_size = 0.05  # Set the step size for adjustments to 5%

        # Update the visual representation of the bars and display the values
        self.update_bars()
        self.update_display()

        # Bind mouse events to handle interactions
        self.canvas.bind("<Button-1>", self.on_click)  # Left mouse button click
        self.canvas.bind("<B1-Motion>", self.on_drag)   # Mouse drag with button held down

    def update_bars(self):
        # Clear the canvas before drawing new rectangles
        self.canvas.delete("all")
        # Draw the train ratio bar
        self.canvas.create_rectangle(5, 20, self.train_pos * self.width, 60, fill='#FF6F61')
        # Draw the validation ratio bar
        self.canvas.create_rectangle(self.train_pos * self.width, 20, self.valid_pos * self.width, 60, fill='#6FAF8C')
        # Draw the test ratio bar (remaining part)
        self.canvas.create_rectangle(self.valid_pos * self.width, 20, self.width, 60, fill='#FFCC00')

    def on_click(self, event):
        # Determine which bar was clicked based on the mouse x-coordinate
        if event.x <= self.train_pos * self.width:
            self.selected_bar = 'train'  # Train bar selected
        elif self.train_pos * self.width < event.x <= self.valid_pos * self.width:
            self.selected_bar = 'valid'  # Validation bar selected
        else:
            self.selected_bar = None  # No bar selected

    def on_drag(self, event):
        # Adjust the position of the selected bar based on mouse drag
        if self.selected_bar == 'train':
            new_train_pos = round(event.x / self.width / self.step_size) * self.step_size
            new_train_pos = max(0, min(1, new_train_pos))  # Ensure value stays between 0 and 1
            if new_train_pos < self.valid_pos:
                self.train_pos = new_train_pos  # Update train position

        elif self.selected_bar == 'valid':
            new_valid_pos = round(event.x / self.width / self.step_size) * self.step_size
            new_valid_pos = max(0, min(1, new_valid_pos))  # Ensure value stays between 0 and 1
            if new_valid_pos > self.train_pos:
                self.valid_pos = new_valid_pos  # Update validation position

        # Update the visual representation of the bars and display the values
        self.update_bars()
        self.update_display()

    def update_display(self):
        total = 100  # Define the total percentage
        # Calculate the train, validation, and test ratios based on the current positions
        self.train_ratio = round(self.train_pos * total)  # Train ratio as a percentage
        self.valid_ratio = round(self.valid_pos * total) - self.train_ratio  # Validation ratio as a percentage
        self.test_ratio = total - self.train_ratio - self.valid_ratio  # Test ratio as a percentage

        # Update the display with the current train ratio
        self.canvas.create_text(50, 70, text=f"Train: {self.train_ratio}%", anchor='nw',
                                fill='#FF6F61', font=("Helvetica", 12, "bold"))
        # Update the display with the current validation ratio
        self.canvas.create_text(150, 70, text=f"Validation: {self.valid_ratio}%", anchor='nw',
                                fill='#6FAF8C', font=("Helvetica", 12, "bold"))
        # Update the display with the current test ratio
        self.canvas.create_text(280, 70, text=f"Test: {self.test_ratio}%", anchor='nw',
                                fill='#FFCC00', font=("Helvetica", 12, "bold"))

        # Call the callback function if it is defined, passing the updated ratios
        if self.callback:
            self.callback(self.train_ratio, self.valid_ratio, self.test_ratio)


def resource_path(relative_path):
    try:
        # PyInstaller'da çalışırken geçici klasörü kullan
        base_path = sys._MEIPASS
    except AttributeError:
        # Normal çalışırken proje klasörünü kullan
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def browse_files():
    """
    Prompts the user to select a directory, filters image and data files within that directory, and shuffles them.

    The function opens a directory selection window. It filters for image files with `.png`, `.jpg`, or `.jpeg`
    extensions, and data files with `.txt` or `.xml` extensions in the selected directory. It pairs the image and data
    files, shuffles the paired lists, and stores the results in global variables `IMAGE` and `DATA`.

    Global Variables:
    IMAGE (list): A list containing the full paths of the matched image files.
    DATA (list): A list containing the full paths of the matched data files.

    If no folder is selected or if no files of the expected format are found, an error message is displayed.

    Usage:
    The elements in the IMAGE and DATA lists are related by their indices.
    """
    global IMAGE, DATA
    # Unsplit Data folder choose
    folder_name = filedialog.askdirectory(initialdir="/", title="Select a Folder")
    if folder_name:
        try:
            # Filtering Photos
            image_files = [f for f in os.listdir(folder_name) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            data_files = [f for f in os.listdir(folder_name) if f.lower().endswith(('.txt', '.xml'))]
            image_files = [os.path.join(folder_name, f) for f in image_files]
            data_files = [os.path.join(folder_name, f) for f in data_files]

            # Data Shuffle
            combined = list(zip(image_files, data_files))
            random.shuffle(combined)
            image_files, data_files = zip(*combined)

            IMAGE = image_files
            DATA = data_files
        except ValueError:
            pass
    else:
        return None


def create_folders():
    """
    Creates a main folder and three subfolders ('train', 'valid', 'test').

    The function prompts the user to enter a name for the main folder. It then creates this main folder if it does not
    already exist. Afterward, it creates three subfolders named 'train', 'valid', and 'test' within the main folder.

    Returns:
    tuple: A tuple containing the absolute paths of the created subfolders in the following order:
        (train folder path, valid folder path, test folder path).

    If the main folder already exists, a message indicating this is displayed.

    Usage:
    Call the function to create the folder structure needed for organizing data.
    """
    try:
        popup = Toplevel(window)
        popup.title("Folder Name")
        popup.geometry("300x200")

        # Label and Input
        Label(popup, text="Enter the name of the main folder : ", font=("Helvetica", 10), fg="black", bg="#dbdbdb").pack(pady=5)
        entry = Entry(popup, width=25)
        entry.pack(pady=5)

        # Get the value and close the popup
        def on_confirm():
            global user_input
            user_input = entry.get()
            popup.destroy()

        # Okay Button
        ttk.Button(popup, text="Okay", command=on_confirm).pack(pady=10)

        # Wait until the popup appears in the centre of the screen
        popup.transient(window)
        popup.grab_set()
        window.wait_window(popup)

        main_folder = user_input
        sub_folder_train = 'train'
        sub_folder_valid = 'valid'
        sub_folder_test = 'test'

        # Create main folder
        if os.path.exists(main_folder):
            main_folder += '1'
            os.makedirs(main_folder)
            current_file_path = os.path.dirname(__file__)

        # Create sub folders and absolute path
        sub_folder_train_path = os.path.join(main_folder, sub_folder_train)
        os.makedirs(sub_folder_train_path)
        sub_folder_valid_path = os.path.join(main_folder, sub_folder_valid)
        os.makedirs(sub_folder_valid_path)
        sub_folder_test_path = os.path.join(main_folder, sub_folder_test)
        os.makedirs(sub_folder_test_path)

        return sub_folder_train_path, sub_folder_valid_path, sub_folder_test_path
    except (FileExistsError, UnboundLocalError, NameError):
        pass


def update_ratios(train, valid, test):
    # Declare the variables as global to modify them outside of this function
    global train_rat, val_rat, test_rat

    # Convert the input percentages to decimal ratios
    train_rat = train / 100  # Convert the training ratio to a decimal
    val_rat = valid / 100  # Convert the validation ratio to a decimal
    test_rat = test / 100  # Convert the test ratio to a decimal


def split_datas(train_ratio=train_rat, val_ratio=val_rat, test_ratio=test_rat):
    """
    Splits the IMAGE dataset into training, validation, and test sets based on specified ratios.

    The function takes three optional parameters that define the proportions of the dataset to be allocated for
    training, validation, and testing. It uses the global `IMAGE` variable to determine the size of the dataset. If the
    `IMAGE` variable is `None`, it will pass without action.

    Parameters:
    train_ratio (float): The proportion of the dataset to be used for training (default is 0.6).
    val_ratio (float): The proportion of the dataset to be used for validation (default is 0.2).
    test_ratio (float): The proportion of the dataset to be used for testing (default is 0.2).

    Returns:
    tuple: A tuple containing three lists:
        - train (list): The training dataset.
        - validation (list): The validation dataset.
        - test (list): The test dataset.

    Note:
    The ratios of training, validation, and testing must sum to 1. If not, the behavior of the function is undefined.
    Make sure to validate that the `IMAGE` variable is properly populated before calling this function.
    """

    try:
        img_count = len(IMAGE)
        # Splitting train images
        train_data_calc_img = int(img_count * train_ratio)
        train_img = IMAGE[:train_data_calc_img]
        train = [img for img in train_img]
        # Splitting train datas and add the train list
        train_data_calc = int(len(DATA) * train_ratio)
        train_datas = DATA[:train_data_calc]
        for data in train_datas:
            train.append(data)

        # Splitting validation images
        val_data_calc_img = int(img_count * val_ratio) + train_data_calc_img
        validation_img = IMAGE[train_data_calc_img:val_data_calc_img]
        validation = [img for img in validation_img]
        # Splitting validation datas and add the validation list
        val_data_calc = int(len(DATA) * val_ratio) + train_data_calc
        validation_datas = DATA[train_data_calc:val_data_calc]
        for data in validation_datas:
            validation.append(data)

        # Splitting test images
        test_data_calc_img = int(img_count * test_ratio) + val_data_calc_img
        test_img = IMAGE[val_data_calc_img:test_data_calc_img]
        test = [img for img in test_img]
        # Splitting test datas and add the test list
        test_data_calc = int(len(DATA) * test_ratio) + val_data_calc
        test_datas = DATA[val_data_calc:test_data_calc]
        for data in test_datas:
            test.append(data)

        return train, validation, test, img_count
    except TypeError:
        messagebox.showwarning('Warning', 'Select the folder with the data!')


def copy_images():
    """
    Copies images from the IMAGE dataset into designated training, validation, and test subfolders.

    The function first creates the necessary folder structure by calling `create_folders()`,
    and then splits the IMAGE dataset into training, validation, and test sets using `split_datas()`.
    Afterwards, it copies the corresponding images into their respective subfolders.

    Usage:
    This function assumes that the `IMAGE` global variable contains a list of image file paths
    that are to be copied. The folders must be created before copying takes place.

    Returns:
    None

    Note:
    Ensure that the `IMAGE` variable is populated with valid image paths before calling this function.
    If there are any issues with copying files (e.g., if a file does not exist),
    an error will be raised by `shutil.copy`.
    """
    global IMAGE, DATA, train_rat, val_rat, test_rat
    try:
        train, validation, test, img_count = split_datas(train_ratio=train_rat, val_ratio=val_rat, test_ratio=test_rat)
        train_path, valid_path, test_path = create_folders()

        # Copying images to subfolders
        for train_data in train:
            img = rf'{train_data}'
            shutil.copy(img, train_path)

        for valid_data in validation:
            img = rf'{valid_data}'
            shutil.copy(img, valid_path)

        for test_data in test:
            img = rf'{test_data}'
            shutil.copy(img, test_path)
        messagebox.showinfo('Info', f'Your {img_count} images are separated!\n'
                                    f'Train {int(img_count * train_rat)} images\n'
                                    f'Validation {int(img_count * val_rat)} images\n'
                                    f'Test {int(img_count * test_rat)} images ')
    except TypeError:
        pass

    finally:     
        # Clean Memory
        IMAGE = None
        DATA = None
        train_rat = None
        val_rat = None
        test_rat = None
        img_count = None


# Create a new Tkinter window
window = Tk()
icon = resource_path("logo.ico")  # Icon path
window.iconbitmap(icon)  # Add icon to window
window.title('Splitter Alpha')  # Set the window title
window.geometry("640x480")  # Set the window size
window.config(background="#f0f0f0")  # Set a light background color

# Title area
title_frame = Frame(window, bg="#4a90e2", pady=20)  # Create a frame for the title with padding
title_frame.pack(fill="x")  # Fill the width of the window

title_label = Label(title_frame, text="Splitter Alpha", font=("Helvetica", 20, "bold"), fg="white", bg="#4a90e2")  # Title label
title_label.pack()  # Add the title label to the title frame

# Main content area
content_frame = Frame(window, bg="#f0f0f0", pady=20)  # Create a frame for the content area with padding
content_frame.pack(fill="both", expand=True)  # Allow it to expand and fill the window

# Add the RatioSlider to the content frame
ratio_slider = RatioSlider(window, callback=update_ratios)  # Create a RatioSlider with a callback function
ratio_slider.pack(pady=20)  # Add the slider to the content frame with padding

# File browsing button
button_explore = ttk.Button(content_frame, text="Browse Files", command=browse_files)  # Button to browse files
button_explore.pack(pady=10)  # Add the button to the content frame with padding

# Start operation button
button_start = ttk.Button(content_frame, text="Split Datas", command=copy_images)  # Button to start the separation process
button_start.pack(pady=10)  # Add the button to the content frame with padding

# Exit button
button_exit = ttk.Button(content_frame, text="Exit", command=window.quit)  # Button to close the application
button_exit.pack(pady=10)  # Add the button to the content frame with padding

# Button styles and window configuration
style = ttk.Style()  # Create a style object for button styling
style.configure("TButton", font=("Helvetica", 12), padding=10)  # Configure the button style

# Start the Tkinter event loop to display the GUI
window.mainloop()

