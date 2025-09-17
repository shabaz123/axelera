# simple file explorer and image editor
# keypress operations:
# press q, a, o, p to pan the image because it may be too large to fit in the window
# the cursor is a box shape of 640x640 pixels
# This application allows you to browse files in a specified folder and open images for editing.
# Operations in File List window:
#   double-click: Open the selected file in the Image Editor
#   'r' : Refresh the file list
# Operations in Image window:
#   'q', 'a', 'o', 'p' :  Pan the image up/down/left/right
#   'c' :  Display crop box (hold down and move mouse button). Release and press Return to accept, ESC to abort crop
#   '1', '2' : Set bounding box corner 1 or 2 for labeling. Press Return to accept, ESC to abort labeling
#   'r', 'R' : Resize the image smaller or larger


import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw, ImageOps

# bounding box image full path and filename
bbox_filename = "c:/development/bbox640.png"

label_folder = "../labels"

# set the geometry of the window
geomX = 1420
geomY = 800
folder = '.'  # default folder to display files, can be overridden by command line argument

# Info Class that displays information about the image editor and file selector in a text widget in a separate window
class Info(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.title("Info")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        info_text = """Image Editor and File Selector
This application allows you to browse files in a specified folder and open images for editing.
Operations in File List window:
  double-click: Open the selected file in the Image Editor
  'r' : Refresh the file list
Operations in Image window:
  'q', 'a', 'o', 'p' :  Pan the image up/down/left/right
  'c' :  Display crop box (hold down and move mouse button). Release and press Return to accept, ESC to abort crop
  '1', '2' : Set bounding box corner 1 or 2 for labeling. Press Return to accept, ESC to abort labeling
  'r', 'R' : Resize the image smaller or larger
For more information, please refer to the documentation."""
        self.text_widget = tk.Text(self, wrap="word")
        self.text_widget.insert(tk.END, info_text)
        self.text_widget.pack(expand=True, fill="both")
        self.text_widget.config(state=tk.DISABLED)
        # create a button to close the info window
        self.close_button = tk.Button(self, text="Close", command=self.destroy)
        self.close_button.pack(pady=10)
        # bind 'i' key to open the info window
        self.bind("<i>", self.open_info)
    def open_info(self, event=None):
        """Open the info window."""
        self.deiconify()
        """Show the info window."""
        self.focus_set()
        self.lift()
        self.attributes("-topmost", True)


# File Selector Class
# this class is used to display a scrollable list of all the files in the ImageEditor 
# instance image_path, and allows the user to double-click on any file to open it 
# using the ImageEditor class

# class FileSelector(tk.Frame):
class FileSelector(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        # self.pack()
        self.create_widgets()
        self.editor = None  # will be set to the ImageEditor instance after creation
        # bind 'r' key to refresh the file list
        self.bind("<r>", self.refresh_file_list)

    def create_widgets(self):
        self.file_listbox = tk.Listbox(self, width=100, height=20)
        self.file_listbox.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.scrollbar.config(command=self.file_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.file_listbox.config(yscrollcommand=self.scrollbar.set)


        # populate the listbox with files from the specified folder
        for file in os.listdir(folder):
            if os.path.isfile(file):
                self.file_listbox.insert(tk.END, file)

        # bind double-click event to call open_file method
        self.file_listbox.bind("<Double-Button-1>", self.open_file)
        

    def refresh_file_list(self, event=None):
        """Refresh the file list in the listbox."""
        self.file_listbox.delete(0, tk.END)
        # clear the listbox
        for file in os.listdir(folder):
            if os.path.isfile(file):
                self.file_listbox.insert(tk.END, file)
        # re-populate the listbox with files from the specified folder
        if not self.file_listbox.size():
            messagebox.showinfo("Info", "No files found in the specified folder.")
        else:
            # file list refreshed
            pass

    def open_file(self, event):
        selected_file = self.file_listbox.get(self.file_listbox.curselection())
        if selected_file:
            try:
                if not self.editor:
                    self.editor = ImageEditor(self.master)  # create an instance of ImageEditor if not already created
                self.editor.open_image_filepath(selected_file)  # use the method to open image by file path
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")


# Image Editor Class
class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.file_path = None  # path to the currently opened image file
        self.originalImage = None
        self.image = None
        self.image_label = tk.Label(self.root)
        self.image_label.pack()
        self.overlayImage = None
        self.tool = "notool"  # default tool, can be "crop" etc

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_image)
        self.file_menu.add_command(label="Save", command=self.save_image)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        # self.edit_menu.add_command(label="Blur", command=self.blur_image)
        # self.edit_menu.add_command(label="Sharpen", command=self.sharpen_image)
        self.crop_size = (640, 640)  # default crop size
        self.crop_location = (0, 0)  # default crop location
        self.resize_factor = 1.0  # default resize factor
        self.displayPosition = (0, 0)
        self.labelPosition = (0,0,0,0) # (center_x, center_y, width, height) for the label position
        self.labelBoxCandidate = (0,0,0,0) # (x1, y1, x2, y2) for the label box candidate position
        self.root.bind("<o>", self.pan_left)
        self.root.bind("<p>", self.pan_right)
        self.root.bind("<q>", self.pan_up)
        self.root.bind("<a>", self.pan_down)
        self.root.bind("<c>", self.crop_choose)
        self.root.bind("<Escape>", self.exit_tool)
        self.root.bind("<Return>", self.action_tool)
        self.root.bind("<Key-1>", self.labelPos1_choose)
        self.root.bind("<Key-2>", self.labelPos2_choose)
        self.root.bind("<r>", self.resize_smaller)
        self.root.bind("<R>", self.resize_larger)
        
        # file selector
        self.file_selector = FileSelector(self.root)
        # store the red crop overlay box image in self.overlayImage
        self.overlayImage = Image.open(bbox_filename)
        # create the Info window
        # self.info_window = Info(self.root)

    def exit_tool(self, event=None):
        if self.tool == "notool":
            return
        if self.tool == "crop":
            # get the original image at the current pan display position
            self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                        min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                        min(self.originalImage.height, geomY + self.displayPosition[1])))
            self.display_image()
            self.tool = "notool"
            return
        if self.tool == "label":
            # reset the label position
            self.labelPosition = (0, 0, 0, 0)  # reset label position
            self.labelBoxCandidate = ((self.crop_size[0] // 2)-10, (self.crop_size[1] // 2)-10, (self.crop_size[0] // 2)+10, (self.crop_size[1] // 2)+10)
            # get the original image at the current pan display position
            self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                      min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                      min(self.originalImage.height, geomY + self.displayPosition[1])))
            self.read_labelfile()  # read the label file if it exists, and set self.labelPosition
            self.display_image()  # refresh the image display
            self.tool = "notool"  # reset the tool after exiting

    def action_tool(self, event=None):
        if self.tool == "notool":
            messagebox.showinfo("Info", "No tool selected, nothing to action.")
            return
        if self.tool == "crop":
            self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                      min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                      min(self.originalImage.height, geomY + self.displayPosition[1])))
            # crop the image
            if self.crop_location[0] < 0 or self.crop_location[1] < 0:
                messagebox.showwarning("Warning", "Crop location is out of bounds.")
                return
            if (self.crop_location[0] + self.crop_size[0] > self.image.width or
                self.crop_location[1] + self.crop_size[1] > self.image.height):
                messagebox.showwarning("Warning", "Crop size is out of bounds.")
                return
            self.image = self.image.crop((self.crop_location[0], self.crop_location[1],
                                          self.crop_location[0] + self.crop_size[0],
                                          self.crop_location[1] + self.crop_size[1]))
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                      filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png")])
            if file_path:
                try:
                    # convert to jpg
                    if file_path.lower().endswith('.png'):
                        self.image = self.image.convert("RGB")
                    elif file_path.lower().endswith('.bmp'):
                        self.image = self.image.convert("RGB")
                    elif file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                        self.image = self.image.convert("RGB")
                    self.image.save(file_path)
                    messagebox.showinfo("Success", "Image saved successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save image: {e}")
            self.tool = "notool"  # reset the tool after action
            return
        if self.tool == "label":
            # check if labelPosition is set
            if self.labelPosition == (0, 0, 0, 0):
                messagebox.showwarning("Warning", "No label position set.")
                return
            # determine desired label file name
            file_path = self.file_path
            dot_index = file_path.rfind('.')
            file_extension = file_path[dot_index + 1:].lower()
            fname_without_extension = file_path[:dot_index]  # get the file name without extension
            label_file = os.path.join(label_folder, os.path.basename(fname_without_extension) + '.txt')
            if os.path.exists(label_file):
                # ask the user if they want to overwrite the existing label file
                overwrite = messagebox.askyesno("Overwrite", "Label file already exists. Do you want to overwrite it?")
                if not overwrite:
                    return
            # save the label position to the label file
            try:
                with open(label_file, 'w') as f:
                    # write the label position in the format: idnum x y width height
                    # idnum is 0 for now, and x, y, width, height are scaled to the image size
                    idnum = 0  # default id number
                    x = self.labelPosition[0] / self.image.width  # scale to [0, 1]
                    y = self.labelPosition[1] / self.image.height
                    width = self.labelPosition[2] / self.image.width
                    height = self.labelPosition[3] / self.image.height
                    print(f"Saving label content '{idnum} {x} {y} {width} {height}' to {label_file}")
                    f.write(f"{idnum} {x} {y} {width} {height}\n")
                messagebox.showinfo("Success", "Label position saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save label position: {e}")
            self.tool = "notool"  # reset the tool after action

    def labelPos_choose(self, cornerNum = 0):
        if not self.originalImage:
            messagebox.showwarning("Warning", "No image to label.")
            return
        # check the image size is equal to the crop size
        if self.originalImage.width != self.crop_size[0] or self.originalImage.height != self.crop_size[1]:
            messagebox.showwarning("Warning", "Crop to the correct size first!")
            return
        if self.tool == "notool":
            self.tool = "label"
        if self.tool != "label":
            messagebox.showinfo("Info", f"Currently in {self.tool} mode. Press 'esc' to exit that.")
            return
        # get mouse pointer position within the window
        x, y  = self.root.winfo_pointerxy()
        x -= self.root.winfo_rootx()
        y -= self.root.winfo_rooty()
        x = x - ((geomX //2)-(self.crop_size[0] // 2))
        y = y - 22
        if cornerNum == 1:
            self.labelBoxCandidate = (x, y, self.labelBoxCandidate[2], self.labelBoxCandidate[3])  # update the first corner
        elif cornerNum == 2:
            self.labelBoxCandidate = (self.labelBoxCandidate[0], self.labelBoxCandidate[1], x, y)  # update the opposite corner
        # print(f"labelBoxCandidate: {self.labelBoxCandidate}")
        # get the original image at the current pan display position
        self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                      min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                      min(self.originalImage.height, geomY + self.displayPosition[1])))
        
        width = abs(self.labelBoxCandidate[2] - self.labelBoxCandidate[0])  # width of the label box
        height = abs(self.labelBoxCandidate[3] - self.labelBoxCandidate[1])
        center_x = (self.labelBoxCandidate[0] + self.labelBoxCandidate[2]) // 2  # center x of the label box
        center_y = (self.labelBoxCandidate[1] + self.labelBoxCandidate[3]) // 2
        self.labelPosition = (center_x, center_y, width, height)
        self.display_image()

    def labelPos1_choose(self, event=None):
        self.labelPos_choose(1)

    def labelPos2_choose(self, event=None):
        self.labelPos_choose(2)

    def crop_choose(self, event=None):
        if not self.originalImage:
            messagebox.showwarning("Warning", "No image to crop.")
            return
        if self.tool == "notool":
            self.tool = "crop"
        if self.tool != "crop":
            messagebox.showinfo("Info", f"Currently in {self.tool} mode. Press 'esc' to exit that.")
            return
        # get mouse pointer position within the window
        x, y  = self.root.winfo_pointerxy()
        x -= self.root.winfo_rootx()
        y -= self.root.winfo_rooty()
        # get the original image at the current pan display position
        self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                      min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                      min(self.originalImage.height, geomY + self.displayPosition[1])))
        # overlay image at the mouse pointer position
        x -= self.crop_size[0] // 2
        y -= self.crop_size[1] // 2
        self.crop_location = (x+4, y+4)  # save the crop location, inside the red border thickness
        self.image.paste(self.overlayImage, (x, y), self.overlayImage)
        self.display_image()
        
    def resize_smaller(self, event=None):
        self.handle_resize(-1)

    def resize_larger(self, event=None):
        self.handle_resize(1)

    def handle_resize(self, direction):
        if not self.originalImage:
            messagebox.showwarning("Warning", "No image to resize.")
            return
        if self.tool != "notool":
            messagebox.showinfo("Info", f"Currently in {self.tool} mode. Press 'esc' to exit that.")
            return
        # direction is -1 for smaller, 1 for larger
        scale = self.resize_factor
        if direction == -1:
            if scale > 0.1:
                scale = scale - 0.1
        elif direction == 1:
            if scale < 3.0:
                scale = scale + 0.1
        else:
            scale = 1.0  # reset to default scale
        
        # check that the new proposed resize scale is not too small
        if scale * self.originalImage.width < self.crop_size[0]:
            messagebox.showwarning("Warning", "Image width is too small, cannot resize smaller.")
            return
        if scale * self.originalImage.height < self.crop_size[1]:
            messagebox.showwarning("Warning", "Image height is too small, cannot resize smaller.")
            return
        
        self.originalImage = Image.open(self.file_path) # work on file image for best quality
        self.originalImage = ImageOps.exif_transpose(self.originalImage)  # handle EXIF orientation
        self.originalImage = self.originalImage.resize((int(self.originalImage.width * scale),
                                                       int(self.originalImage.height * scale)),
                                                      Image.Resampling.LANCZOS)
        self.resize_factor = scale
        self.reset_position_vars()  # reset position variables
        self.orig2croppedImage() # copy originalImage to self.image and crop it at displayPosition origin to fit window geometry
        self.set_title(self.originalImage.width, self.originalImage.height)
        self.read_labelfile()  # read the label file if it exists, and set self.labelPosition
        self.display_image()


    def pan_left(self, event=None):
        if self.originalImage:
            # move the displayPosition to the left by 100 pixels
            if self.displayPosition[0] >= 100:
                self.displayPosition = (self.displayPosition[0] - 100, self.displayPosition[1])
                self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                      min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                      min(self.originalImage.height, geomY + self.displayPosition[1])))
                self.display_image()
            else:
                # cannot pan left, already at the edge
                pass
    def pan_right(self, event=None):
        if self.originalImage:
            # move the displayPosition to the right by 100 pixels
            if self.displayPosition[0] + geomX <= self.originalImage.width - 100:
                self.displayPosition = (self.displayPosition[0] + 100, self.displayPosition[1])
                self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                      min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                      min(self.originalImage.height, geomY + self.displayPosition[1])))
                self.display_image()
            else:
                # cannot pan right, already at the edge
                pass
    def pan_up(self, event=None):
        if self.originalImage:
            # move the displayPosition up by 100 pixels
            if self.displayPosition[1] >= 100:
                self.displayPosition = (self.displayPosition[0], self.displayPosition[1] - 100)
                self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                      min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                      min(self.originalImage.height, geomY + self.displayPosition[1])))
                self.display_image()
            else:
                # cannot pan up, already at the edge
                pass
    def pan_down(self, event=None):
        if self.originalImage:
            # move the displayPosition down by 100 pixels
            if self.displayPosition[1] + geomY <= self.originalImage.height - 100:
                self.displayPosition = (self.displayPosition[0], self.displayPosition[1] + 100)
                self.image = self.originalImage.crop((self.displayPosition[0], self.displayPosition[1],
                                                      min(self.originalImage.width, geomX + self.displayPosition[0]),
                                                      min(self.originalImage.height, geomY + self.displayPosition[1])))
                self.display_image()
            else:
                # cannot pan down, already at the edge
                pass

    def read_labelfile(self):
        file_path = self.file_path
        # search for '.' in file_path, but search from the end of the string
        dot_index = file_path.rfind('.')
        if dot_index == -1:
            messagebox.showerror("Error", "File does not have a valid image extension.")
            return
        else:
            # get the file extension
            file_extension = file_path[dot_index + 1:].lower()
            if file_extension not in ['jpg', 'jpeg', 'png', 'bmp']:
                messagebox.showerror("Error", "File is not a valid image type.")
                return
        fname_without_extension = file_path[:dot_index]  # get the file name without extension
        # see if a label file exists with the same name (.txt suffix) and if so, read the first line
        # which contains idnum, x, y, width, height
        label_file = os.path.join(label_folder, os.path.basename(fname_without_extension) + '.txt')
        if os.path.exists(label_file):
            # read the first line of the label file
            with open(label_file, 'r') as f:
                line = f.readline().strip()
                if line:
                    try:
                        # example line is "0 0.5 0.5 0.2 0.2"
                        parts = line.split()
                        if len(parts) != 5:
                            raise ValueError(f"Label file format is incorrect, expected 5 parts, got {len(parts)}.")
                        x = float(parts[1])  # x center position
                        y = float(parts[2])  # y center position
                        width = float(parts[3])  # width of the bounding box
                        height = float(parts[4])  # height of the bounding box
                        # values are betwen 0 and 1, so scale them to the image size and store them
                        self.labelPosition = (x * self.image.width, y * self.image.height, width * self.image.width, height * self.image.height)
                        # self.draw_label_box()  # draw the label box on the image
                    except ValueError:
                        messagebox.showerror("Error", "Label file format is incorrect.") 

    def set_title(self, width, height):
        """Set the window title with image dimensions and file name."""
        if self.file_path:
            self.root.title(f"{width} x {height}   {os.path.basename(self.file_path)}")
        else:
            self.root.title(f"No image opened")

    def orig2croppedImage(self):
        self.image = self.originalImage.copy()
        if self.image.width > geomX or self.image.height > geomY:
            self.image = self.image.crop((self.displayPosition[0], self.displayPosition[1],
                                            min(self.image.width, geomX + self.displayPosition[0]),
                                            min(self.image.height, geomY + self.displayPosition[1])))
    def reset_position_vars(self):
        self.displayPosition = (0, 0)  # reset display position
        self.labelPosition = (0, 0, 0, 0)  # reset label position
        self.labelBoxCandidate = ((self.crop_size[0] // 2)-10, (self.crop_size[1] // 2)-10, (self.crop_size[0] // 2)+10, (self.crop_size[1] // 2)+10)  # reset label box candidate position

    def open_image_filepath(self, file_path):
        """Open an image file given its file path."""
        if not os.path.isfile(file_path):
            messagebox.showerror("Error", "File does not exist.")
            return
        try:
            self.file_path = file_path  # store the file path
            self.originalImage = Image.open(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image: {e}")
            return
        self.originalImage = ImageOps.exif_transpose(self.originalImage)  # handle EXIF orientation
        self.resize_factor = 1.0 # reset resize factor
        self.reset_position_vars()  # reset position variables
        self.orig2croppedImage() # copy originalImage to self.image and crop it at displayPosition origin to fit window geometry
        self.set_title(self.originalImage.width, self.originalImage.height)
        self.read_labelfile()  # read the label file if it exists, and set self.labelPosition
        self.display_image()

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file_path:
            try:
                self.open_image_filepath(file_path)  # use the method to open image by file path
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {e}")

    def save_image(self):
        if not self.image:
            messagebox.showwarning("Warning", "No image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                  filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("PNG files", "*.png")])
        if file_path:
            try:
                self.image.save(file_path)
                messagebox.showinfo("Success", "Image saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}")

    def display_image(self):
        if not self.image:
            return
        self.draw_label_box()  # draw the label box on the image if labelPosition is set
        img_tk = ImageTk.PhotoImage(self.image)
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk
    
    def draw_label_box(self):
        """Draw a bounding box around the label position."""
        # if labelPosition values are (0, 0, 0, 0) then return
        if self.labelPosition == (0, 0, 0, 0):
            return
        draw = ImageDraw.Draw(self.image)
        # draw the rectangle on the image
        width = self.labelPosition[2]
        height = self.labelPosition[3]
        x1 = self.labelPosition[0] - width // 2
        y1 = self.labelPosition[1] - height // 2
        x2 = self.labelPosition[0] + width // 2
        y2 = self.labelPosition[1] + height // 2
        thickness = 4  # thickness of the rectangle border
        x1 = x1 - thickness
        y1 = y1 - thickness
        x2 = x2 + thickness
        y2 = y2 + thickness
        draw.rectangle([x1, y1, x2, y2], outline="blue", width=thickness)

# main function
# image path is passed as a command line argument
def main():
    global folder
    # check that the labels folder exists
    if not os.path.exists(label_folder):
        print(f"Error: labels folder '{label_folder}' does not exist.")
        sys.exit(1)
    root = tk.Tk()
    # pass the image path as a command line argument to the ImageEditor class
    if len(sys.argv) > 1:
        folder = sys.argv[1]

    editor = ImageEditor(root)
    # file_selector = FileSelector(root)
    # layout the file selector and image editor
    # file_selector.pack(side="left", fill="y")
    # editor.image_label.pack(side="right", fill="both", expand=True)
    # root.title("Image Editor and File Explorer")
    # set the geometry of the window
    root.geometry(f"{geomX}x{geomY}")
    # display scrollbars
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.resizable(True, True)
    root.mainloop()

if __name__ == "__main__":
    main()


