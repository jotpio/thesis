# from tkinter import ttk
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from tktooltip import ToolTip
from tkcalendar import Calendar, DateEntry
from ttkthemes import ThemedTk
# from tkinter.ttk import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


from datetime import date
import argparse
import sys
import numpy as np

from plot import plot_all_positions, plot_position_hexmap
from load_data import load_robot_data, load_fish_data, load_behavior_data
from extend_robot_data import extend_robot_data
from util import get_all_positions

class LoadingGUI():
    
    dates_dict=None
    window=None
    
    def openNewWindow(self):
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self.window)

        # sets the title of the
        # Toplevel widget
        newWindow.title("New Window")

        # sets the geometry of toplevel
        newWindow.geometry("1000x1000")

        # A Label widget to show in toplevel
        Label(newWindow, text ="Plots").pack()
        
        return newWindow
    
    def browse_robot_button(self):
        filename = filedialog.askdirectory()
        self.input_robot.delete(0,END)
        self.input_robot.insert(0, filename)

    def browse_fish_button(self):
        filename = filedialog.askdirectory()
        self.input_fish.delete(0,END)
        self.input_fish.insert(0, filename)

    def browse_behavior_button(self):
        filename = filedialog.askdirectory()
        self.input_beh.delete(0,END)
        self.input_beh.insert(0, filename)

    def browse_user_button(self):
        filename = filedialog.askdirectory()
        self.input_user.delete(0,END)
        self.input_user.insert(0, filename)

    def load_data(self):
        robot_path = self.input_robot.get()
        fish_path = self.input_fish.get()
        beh_path = self.input_beh.get()
        user_path = self.input_user.get()
        
        start_date = self.start_date_cal.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date_cal.get_date().strftime("%Y-%m-%d")
        ignore_standing_pos = self.ignore_standing_pos.get()
        
        self.dates_dict = load_robot_data(robot_path, start_date, end_date)
        self.dates_dict = load_behavior_data(beh_path, self.dates_dict, start_date, end_date)
        self.dates_dict = load_fish_data(fish_path, self.dates_dict, start_date, end_date)
        self.dates_dict = extend_robot_data(self.dates_dict, ignore_standing_pos)

    def plot_all_positions(self):
        if self.dates_dict is not None and len(self.dates_dict.keys()) > 0:            
            
            # matplotlib.use('TkAgg')
            #init window
            plot_window = self.openNewWindow() 
            
            # create a figure
            figure = Figure(figsize=(15, 15), dpi=80)
            ax1 = figure.add_subplot(111)
            # create FigureCanvasTkAgg object
            figure_canvas = FigureCanvasTkAgg(figure, master=plot_window)
            # figure_canvas.draw()
            figure_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            
            # plot in figure
            plot_all_positions(self.dates_dict, start_date=None, end_date=None, ax=ax1)

            # create the toolbar
            # toolbar = NavigationToolbar2Tk(figure_canvas, plot_window)
            # toolbar.update()
            # create axes
            # axes = figure.add_subplot()
            # figure_canvas.get_tk_widget().pack()            
            
        else:
            print("No loaded data!")


    def plot_loaded_data(self):
        plt_pos_hexm, plt_allpos = self.load_plot_parameters() # load parameters from checkboxes
  
        if plt_pos_hexm:
            # create_plot_window()
            # init window
            plot_window = self.openNewWindow()
            
            top_frame = ttk.Frame(plot_window, padding = (10, 10))
            top_frame.pack()
            # create a figure
            figure = Figure(figsize=(15, 15), dpi=80)
            ax1 = figure.add_subplot(111)
                        
            #plot in figure
            pos = get_all_positions(self.dates_dict, challenges=True, successful=True)
            plot_position_hexmap(pos, ax=None)

            # create FigureCanvasTkAgg object
            figure_canvas = FigureCanvasTkAgg(figure, master=top_frame)
            # figure_canvas.draw()
            # figure_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            
            toolbar = NavigationToolbar2Tk(figure_canvas, top_frame)
            toolbar.update()
            figure_canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

            
            
        if plt_allpos:
            #init window
            plot_window = self.openNewWindow() 
            top_frame = ttk.Frame(plot_window, padding = (10, 10))
            top_frame.pack()
            # create a figure
            figure = Figure(figsize=(15, 15), dpi=80)
            ax1 = figure.add_subplot(111)
            
            
            # plot in figure
            plot_all_positions(self.dates_dict, start_date=None, end_date=None, ax=None)
            
            # create FigureCanvasTkAgg object
            figure_canvas = FigureCanvasTkAgg(figure, master=top_frame)
            # figure_canvas.draw()
            # figure_canvas.draw()        
                       
            
            # toolbar = NavigationToolbar2Tk(figure_canvas, top_frame)
            # toolbar.update()
            figure_canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)


    def load_plot_parameters(self):
        return self.plt_pos_hexm.get(), self.plt_allpos.get()

    def __init__(self, base_dir):
        '''
        ################################################################################################################
                                                            Loading
        ################################################################################################################
        '''
            
        # directories
        self.fish_dir=base_dir+"fish"
        self.robot_dir=base_dir+"robot"
        self.behavior_dir=base_dir+"behavior_prints"
        self.user_input_dir=base_dir+"user_input"
        
        # style = ttk.Style()
        # style.configure("BW.TLabel", foreground="black", background="white")

        # The main tkinter window
        # self.window = ThemedTk(theme="adapta")
        self.window = Tk()
        # setting the title
        self.window.title('Load and Plot Humboldt Forum Data')
        # setting the dimensions of the main window
        # self.window.geometry("500x500")

        row = 0

        # robot path dialog
        button2 = Button(master=self.window, text="Browse robot data", command=self.browse_robot_button, width=20)
        button2.grid(row=row, column=0)
        self.input_robot = Entry(self.window, width = 50)
        self.input_robot.insert(0,self.robot_dir)
        self.input_robot.grid(row=row, column=1)
        row += 1

        # fish path dialog
        button3 = Button(master=self.window, text="Browse fish data", command=self.browse_fish_button, width=20)
        button3.grid(row=row, column=0)
        self.input_fish = Entry(self.window, width = 50)
        self.input_fish.insert(0,self.fish_dir)
        self.input_fish.grid(row=row, column=1)
        row += 1

        # behavior path dialog
        button4 = Button(master=self.window, text="Browse behavior data", command=self.browse_behavior_button, width=20)
        button4.grid(row=row, column=0)
        self.input_beh = Entry(self.window, width = 50)
        self.input_beh.insert(0,self.behavior_dir)
        self.input_beh.grid(row=row, column=1)
        row += 1

        # user input path dialog
        button5 = Button(master=self.window, text="Browse user input data", command=self.browse_user_button, width=20)
        button5.grid(row=row, column=0)
        self.input_user = Entry(self.window, width = 50)
        self.input_user.insert(0,self.user_input_dir)
        self.input_user.grid(row=row, column=1)
        row += 1

        #separator
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=row, columnspan=10,sticky="ew", pady=(5, 5))
        row += 1

        # date dialog
        start_date_label = Label(self.window,text="Start date:").grid(row=row, column=0)
        self.start_date_cal = DateEntry(self.window, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2022, month=2, day=2)
        self.start_date_cal.grid(row=row, column=1)
        row += 1
        end_date_label = Label(self.window,text="End date:").grid(row=row, column=0)
        self.end_date_cal = DateEntry(self.window, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2022, month=2, day=3)
        self.end_date_cal.grid(row=row, column=1)
        row += 1
        
        # position heatmap checkbox
        self.ignore_standing_pos = IntVar()
        self.ignore_standing_pos_cb = Checkbutton(self.window, 
                                                  text='remove robot standing still',
                                                  variable=self.ignore_standing_pos, 
                                                  onvalue=1, offvalue=0)
        self.ignore_standing_pos_cb.grid(row=row, column=0)
        ToolTip(self.ignore_standing_pos_cb, msg="remove positions where previous position is the same")
        row += 1
        
        # load data button
        button6 = Button(master=self.window, text="Load data", command=self.load_data, width=40)
        button6.grid(row=row, columnspan=10, pady=5)
        row += 1
        
        # separator
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=row, columnspan=10,sticky="ew", pady=(5, 5))
        row += 1
        
        '''
        ################################################################################################################
                                                            Plotting
        ################################################################################################################
        '''

        # all position checkbox
        self.plt_allpos = IntVar()
        self.plt_allpos_button = Checkbutton(self.window, text="scatter all positions", 
                                             variable=self.plt_allpos, 
                                             onvalue=1, offvalue=0).grid(row=row, column=0)
        row += 1

        # rotation histogram position heatmap checkbox
        self.plt_pos_hexm = IntVar()
        self.pos_hm_cb = Checkbutton(self.window, text='all position hexmap',
                                     variable=self.plt_pos_hexm, 
                                     onvalue=1, offvalue=0).grid(row=row, column=0)
        row += 1

        # button that displays the plot
        plot_button = Button(master=self.window, width=20, text="Generate Plots", command=self.plot_loaded_data)
        plot_button.grid(row=row, column=0)
        row += 1

        # run the gui
        self.window.mainloop()
        
if __name__ == '__main__':
    # Execute when the module is not initialized from an import statement.
    parser = argparse.ArgumentParser(description='Load Humboldt-Forum data')
    parser.add_argument('--base_dir', '-b', required=True,
                    help='path containing all other log directories')

    args = parser.parse_args()    
    
    LoadingGUI(args.base_dir)