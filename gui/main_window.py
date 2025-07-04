import cv2
import base64
import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QCheckBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import AutoLocator

from app import toolbox_bases
import constants
import colors
from gui.gui_management import GUiManagement
from gui.gui_components import NoArrowComboBox


class MainWindow(QWidget, GUiManagement):
    """
    Main window class for the image processing application.
    This class initializes the UI components and manages drop events for reordering toolboxes.
    """

    def __init__(self):
        super().__init__()  

        # Create main layout and set it to the widget
        self.main_layout = QVBoxLayout(self) 
        self.main_layout.setContentsMargins(20, 5, 20, 5) 
        self.main_layout.setSpacing(15)

        # init top, mid and bottom layouts
        self.init_top_layout()
        self.init_midLayout()
        self.init_bottomLayout()

        # Initialize UI variables in UiManagement
        self.init_ui_variables(self.contentLayout, self.add_new_box, self.in_im_canvas, self.out_im_canvas, 
                               self.left_title, self.right_title, self.vis_mod_list, self.color_chan_list, self.zoom_btns)  


        # Decode and display the base64 encoded placeholder image 
        image_bytes = base64.b64decode(constants.NO_IMAGE_BASE64)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        initial_im = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
        self.display_images([initial_im, initial_im])


    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Recall the pipeline to update the output image when the window is resized
        self.pipeline_on_change()
        

    def init_top_layout(self):
        """
        Initialize the top layout with two labels for displaying images.
        """
        # Create top layout and add it to the main layout
        top_layout = QHBoxLayout()
        self.main_layout.addLayout(top_layout, 55)  

        # create leftLayout to hold the left image and title
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        top_layout.addLayout(left_layout, 48)

        # create leftTitle label for displaying the input image title
        self.left_title = QLabel("")
        self.left_title.setText("Channel")
        left_layout.addWidget(self.left_title, alignment=Qt.AlignCenter)
        self.left_title.hide()

        # Create input image canvas
        self.in_im_canvas = InteractiveCanvas()  
        left_layout.addWidget(self.in_im_canvas)

        # create spacer layout to separate the two labels
        spacer = QVBoxLayout()
        top_layout.addLayout(spacer, 4)
  
        # create options layput
        options_container = QWidget()
        options = QVBoxLayout(options_container)
        spacer.addWidget(options_container, stretch=1)
        self.zoom_btns = []  

        # create zoom_lock and reset buttons
        x_zoom_lock_btn = QCheckBox("Lock X Zoom")
        x_zoom_lock_btn.setCheckable(True)
        x_zoom_lock_btn.setChecked(False)
        options.addWidget(x_zoom_lock_btn)
        x_zoom_lock_btn.hide()  
        self.zoom_btns.append(x_zoom_lock_btn)

        y_zoom_lock_btn = QCheckBox("Lock Y Zoom")
        y_zoom_lock_btn.setCheckable(True)
        y_zoom_lock_btn.setChecked(False)
        options.addWidget(y_zoom_lock_btn)
        y_zoom_lock_btn.hide()  
        self.zoom_btns.append(y_zoom_lock_btn)

        reset_zoom_btn = QPushButton("Reset Zoom")
        options.addWidget(reset_zoom_btn)
        reset_zoom_btn.hide()  
        self.zoom_btns.append(reset_zoom_btn)
        
        # create text layout
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        spacer.addWidget(text_container, stretch=1)

        # create spacer label
        arrow = QLabel(">")
        font = QFont()              
        font.setPointSize(35)       
        arrow.setFont(font) 
        arrow.setAlignment(Qt.AlignCenter)  
        text_layout.addWidget(arrow, alignment=Qt.AlignCenter)

        # create bottom options
        bot_options_container = QWidget()
        bot_options = QVBoxLayout(bot_options_container)
        spacer.addWidget(bot_options_container, stretch=1)

        # create rightLayout to hold the right image and title
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        top_layout.addLayout(right_layout, 48)

        # create rightTitle label for displaying the output image title
        self.right_title = QLabel("")
        right_layout.addWidget(self.right_title, alignment=Qt.AlignCenter)
        self.right_title.hide()

        # Create output image canvas
        self.out_im_canvas = InteractiveCanvas()
        right_layout.addWidget(self.out_im_canvas)

        # connect zoom lock buttons to their respective methods
        x_zoom_lock_btn.toggled.connect(lambda checked: setattr(self.in_im_canvas, "lock_x_zoom", checked))
        x_zoom_lock_btn.toggled.connect(lambda checked: setattr(self.out_im_canvas, "lock_x_zoom", checked))
        y_zoom_lock_btn.toggled.connect(lambda checked: setattr(self.in_im_canvas, "lock_y_zoom", checked))
        y_zoom_lock_btn.toggled.connect(lambda checked: setattr(self.out_im_canvas, "lock_y_zoom", checked))
        reset_zoom_btn.clicked.connect(lambda: [canvas.reset_zoom(self.display_histogram) for canvas in (self.in_im_canvas, self.out_im_canvas)]) 


    def init_midLayout(self):
        """
        Initialize the mid layout with buttons for various actions.
        """
        # Create mid layout and add it to the main layout
        midLayout = QHBoxLayout()
        self.main_layout.addLayout(midLayout, 10) 

        # Create mid layout widgets and add them to the mid layout
        font = QFont()              
        font.setPointSize(10)  
        
        # Button 1 - open image
        btn = QPushButton(constants.OPEN_BUTTON)
        midLayout.addWidget(btn, 1)      
        btn.clicked.connect(self.open_new_image)   
        btn.setFlat(True)
        btn.setFont(font) 
        btn.setStyleSheet(f"""
            QPushButton {{
                padding-top: 10px;
                padding-bottom: 10px;
            }}
            QPushButton:hover {{
                background-color: {colors.COMBO_HOVER};
            }}
        """)

        # List 1 - Visualization type
        self.vis_mod_list = NoArrowComboBox(items=constants.VISUALIZATION_TYPES)
        midLayout.addWidget(self.vis_mod_list, 1)
        self.vis_mod_list.setFont(font)
        self.vis_mod_list.currentTextChanged.connect(lambda: self.switch_view(self.vis_mod_list.currentText()))  

        # List 2 - Color Channel
        self.color_chan_list = NoArrowComboBox(items=list(constants.VISUALIZATION_TYPES.values())[0])
        midLayout.addWidget(self.color_chan_list, 1)
        self.color_chan_list.setFont(font)
        self.color_chan_list.currentTextChanged.connect(lambda: self.switch_color_chan(self.color_chan_list.currentText())) 

        # Button 2 - save image
        btn = QPushButton(constants.SAVE_BUTTON)
        midLayout.addWidget(btn, 1)   
        btn.clicked.connect(lambda: self.save_image())   
        btn.setStyleSheet("padding-top: 10px; padding-bottom: 10px;")
        btn.setFont(font) 
        btn.setStyleSheet(f"""
            QPushButton {{
                padding-top: 10px;
                padding-bottom: 10px;
            }}
            QPushButton:hover {{
                background-color: {colors.COMBO_HOVER};
            }}
        """)


    def init_bottomLayout(self):
        """
        Initialize the bottom layout with scroll area for function boxes.
        """
        # Create bottom layout and add it to the main layout
        bottomLayout = QHBoxLayout()
        self.main_layout.addLayout(bottomLayout, 35)
          
        # create scroll area widget and add it to the bottom layout
        scrollArea = QScrollArea()         
        scrollArea.setWidgetResizable(True)        
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)   
        bottomLayout.addWidget(scrollArea)        
        
        # create content widget and set it to the scroll area
        contentWidget = QWidget()  
        scrollArea.setWidget(contentWidget)  

        # create content layout and set it to the content widget
        self.contentLayout = QHBoxLayout(contentWidget)
        self.contentLayout.setAlignment(Qt.AlignLeft)
                
        # insert 'new function' box
        self.add_new_box = toolbox_bases.AddNewBox()
        self.contentLayout.addWidget(self.add_new_box)
        self.add_new_box.trigger.connect(self.insert_toolbox)  # connect click event to 'add_new_toolbox' method

        # drag and drop functionality
        contentWidget.setAcceptDrops(True)
        contentWidget.dragEnterEvent = self.dragEnterEvent
        contentWidget.dropEvent = self.dropEvent


    def dragEnterEvent(self, event):
        """
        Handle the drag enter event to allow drag-and-drop functionality.
        Args:
            event (QDragEnterEvent): The drag enter event containing information about the dragged data.
        """
        # Check if the event contains mime data and accept the proposed action
        if event.mimeData():
            event.acceptProposedAction()


    def dropEvent(self, event):
        """
        Handle the drop event to allow reordering of function boxes in the pipeline.
        Args:
            event (QDropEvent): The drop event containing information about the dropped data.
        """
        pos = event.position().toPoint()                # Get the position where the item is dropped
        source = event.source()                         # Get the source widget being dragged
        index = self.find_insert_index(pos)             # Find the index where the item should be inserted

        # Check if the source is a valid FunctionBox
        if source and isinstance(source, toolbox_bases.Toolbox):
            self.pipeline.move_step(source, index)              # move the function box in the pipeline
            self.contentLayout.removeWidget(source)             # Remove the widget from its current position in the layout
            self.contentLayout.insertWidget(index, source)      # Insert the widget at the new index in the layout

            event.acceptProposedAction()            # Accept the proposed action for the drop event
            self.pipeline_on_change()                     # Rerun the pipeline to update the output image


    def find_insert_index(self, pos):
        """
        Find the index in the layout where a widget should be inserted based on the drop position.
        Args:
            pos (QPoint): The position where the item is dropped.
        Returns:
            int: The index where the widget should be inserted.
        """
        # Iterate through all widgets in the content layout
        for i in range(self.contentLayout.count()):
            widget = self.contentLayout.itemAt(i).widget()
            # Check if the widget is valid and not the special footer widget (add_new_box)
            if widget and widget != self.add_new_box:
                # If the drop position is within the geometry of the widget, return its index
                if widget.geometry().contains(pos):
                    return i
        # If no suitable position is found, return the last index (before add_new_box)
        return self.contentLayout.count() - 1



class InteractiveCanvas(FigureCanvas):
    """
    A custom canvas for displaying and interacting with matplotlib figures.
    This canvas supports panning and zooming using mouse events and the scroll wheel.
    """
    def __init__(self, parent=None):
        self.figure = Figure(facecolor=(1,1,1,0))

        super().__init__(self.figure)
        self.setParent(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self._axes = self.figure.add_subplot(111)               # Create a single axes 

        # Initialize panning variables 
        self._is_panning = False
        self._pan_start = None

        # Variables to store x a nd y limits for zooming and panning
        self._xlim = None
        self._ylim = None

        # Variables to store original x and y limits for zooming and panning limits
        self._orig_xlim = None
        self._orig_ylim = None

        self.lock_x_zoom = False    # Flag to lock x-axis zooming
        self.lock_y_zoom = False    # Flag to lock y-axis zooming
        self.is_zoomed = False      # Flag to indicate if the canvas is zoomed
        self.plot_type = "image"  

        # Set the canvas to be transparent
        self.setStyleSheet("background: transparent;")  


    def wheelEvent(self, event):
        """
        Handle the mouse wheel event for zooming in and out of the plot.
        Args:
            event (QWheelEvent): The wheel event containing information about the scroll direction.
        """
        if self._axes is None:
            return
        
        pos = event.position()
        x, y = pos.x(), pos.y()
        xdata, ydata = self._axes.transData.inverted().transform((x, y))

        xlim = self._axes.get_xlim()
        ylim = self._axes.get_ylim()

        step = event.angleDelta().y()
        factor = 1.05 if step < 0 else 0.95

        # calculate new limits
        self._xlim = [
            xdata - (xdata - xlim[0]) * factor,
            xdata + (xlim[1] - xdata) * factor
        ]
        self._ylim = [
            ydata - (ydata - ylim[0]) * factor,
            ydata + (ylim[1] - ydata) * factor
        ]

        if self.plot_type != "histogram":
            # ensure the new limits do not go below 0 or exceed original limits
            self._xlim[0] = max(0, self._xlim[0])  
            self._ylim[1] = max(0, self._ylim[1])  
            self._xlim[1] = min(self._orig_xlim[1], self._xlim[1]) 
            self._ylim[0] = min(self._orig_ylim[0], self._ylim[0])  

        # Lock the zooming if the flags are set
        self._xlim = xlim if self.lock_x_zoom else self._xlim
        self._ylim = ylim if self.lock_y_zoom else self._ylim

        # Update the axes limits and redraw the canvas
        self._axes.set_xlim(self._xlim)
        self._axes.set_ylim(self._ylim)

        # Reconfigure the figure
        if self.plot_type == "image":
            self.configure_imgae_plot()
        elif self.plot_type == "histogram":
            self.configure_hist_plot()
        
        self.draw()

        self.is_zoomed = True

    def mousePressEvent(self, event):
        """
        Handle the mouse press event to initiate panning.
        Args:
            event (QMouseEvent): The mouse event containing information about the button pressed.
        """
        # Check if the left mouse button is pressed to start panning
        if event.button() == Qt.LeftButton:
            self._is_panning = True
            self._pan_start = event.position()


    def mouseMoveEvent(self, event):
        """
        Handle the mouse move event to update the plot during panning.
        Args:
            event (QMouseEvent): The mouse event containing information about the current position.
        """
        # Check if panning is active and the pan start position is set
        if self._is_panning and self._pan_start:

            # Calculate the distance moved in pixels
            dx = event.position().x() - self._pan_start.x()
            dy = event.position().y() - self._pan_start.y()

            # Convert the pixel movement to data coordinates
            dx_data = dx / self.width() * (self._axes.get_xlim()[1] - self._axes.get_xlim()[0])
            dy_data = dy / self.height() * (self._axes.get_ylim()[1] - self._axes.get_ylim()[0])

            # Update the x and y limits based on the pan distance
            self._xlim = [
                self._axes.get_xlim()[0] - dx_data,
                self._axes.get_xlim()[1] - dx_data
            ]
            self._ylim = [
                self._axes.get_ylim()[0] + dy_data,
                self._axes.get_ylim()[1] + dy_data
            ]

            if self.plot_type == "histogram":
                self._axes.set_xlim(self._xlim)
                self._axes.set_ylim(self._ylim)
            else:
                # ensure the new limits do not go below 0 or exceed original limits
                if not (self._xlim[0] < 0 or self._xlim[1] > self._orig_xlim[1]):
                    self._axes.set_xlim(self._xlim)
                if not (self._ylim[1] < 0 or self._ylim[0] > self._orig_ylim[0]):
                    self._axes.set_ylim(self._ylim)

            self._pan_start = event.position()
            self.draw()

            self.is_zoomed = True


    def mouseReleaseEvent(self, event):
        """
        Handle the mouse release event to stop panning.
        Args:
            event (QMouseEvent): The mouse event containing information about the button released.
        """
        # Check if the left mouse button is released to stop panning
        if event.button() == Qt.LeftButton:
            self._is_panning = False
            self._pan_start = None


    def configure_imgae_plot(self):
        """Configure the axes for image plots."""
        if not self.is_zoomed:
            # get original x and y limits to limit zooming and panning
            self._orig_xlim = self._axes.get_xlim()
            self._orig_ylim = self._axes.get_ylim()

        # set the x and y limits to the previous values if any to keep the zoom level
        if self._xlim and self._ylim:
            self._axes.set_xlim(self._xlim)
            self._axes.set_ylim(self._ylim)
        
        self._axes.axis('off')  
        self._axes.grid(False)
        self.figure.set_facecolor((1,1,1,0))  
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0) 


    def configure_hist_plot(self):
        """Configure the axes for histogram plots."""
        if not self.is_zoomed:
            self.figure.set_facecolor((1,1,1,1)) 
            self._axes.set_xlim(-1, 256)
            self._axes.set_aspect('auto')  
            self._axes.xaxis.set_major_locator(AutoLocator())
            self._axes.yaxis.set_major_locator(AutoLocator())
            self.figure.tight_layout(pad=1.5)

        self._axes.axis('on')  
        self._axes.grid(True)
        # set the x and y limits to the previous values if any to keep the zoom level
        if self._xlim and self._ylim:
            self._axes.set_xlim(self._xlim)
            self._axes.set_ylim(self._ylim)


    def reset_plot(self):
        """Reset the plot by clearing the axes and resetting zoom and panning variables."""
        self._axes.clear()                             
        self.is_zoomed = False
        self._xlim = 0
        self._ylim = 0    


    def set_plot_type(self, plot_type):
        """Set the type of plot to be displayed on the canvas."""
        self._axes.clear()  
        self.plot_type = plot_type

    def reset_zoom(self, plot_func):
        """Reset the zoom and panning state of the canvas."""
        self.reset_plot()
        plot_func()
