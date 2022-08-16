import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkinter import filedialog

import file_manager
import analyzer

WINDOW_TITLE = "Nano-indentation Analysis"
WINDOW_GEOMETRY = "1000x800"
FILETYPES = (
    ('text files', '*.txt'),
    ('All files', '*.*'))
FIGSIZE = (8, 4)


class NanoindentationAnalysis:
    def __init__(self):
        """create window"""
        # root
        self.window = Tk()

        # label
        self.first_direction_label = Label(text="1. Open a file to be analyzed")
        self.second_direction_label = Label(text="2. Select Curves")
        self.selected_file_label = Label(text="no data", width=20, bg='#eeeeee')

        # entry
        self.entry_strain_rate1 = Entry(self.window, width=10)
        self.entry_strain_rate2 = Entry(self.window, width=10)
        self.entry_strain_rate3 = Entry(self.window, width=10)
        self.entry_strain_rate4 = Entry(self.window, width=10)

        self.entry_strain_rate1.insert(0, "0.005")
        self.entry_strain_rate2.insert(0, "0.02")
        self.entry_strain_rate3.insert(0, "0.05")
        self.entry_strain_rate4.insert(0, "0.2")

        # button
        self.file_selection_btn = Button(self.window, text="Open a File", width=20, command=self.select_file)
        self.plot_update_btn1 = Button(self.window, text="Plot Update", command=self.update_button1)
        self.curves_merging_btn = Button(self.window, text="Merging and averaging", width=20,
                                         command=self.merging_curve_button)

        self.add_btn1 = Button(self.window, text='Add1', width=8, command=self.add1_btn_clicked)
        self.add_btn2 = Button(self.window, text='Add2', width=8, command=self.add2_btn_clicked)
        self.add_btn3 = Button(self.window, text='Add3', width=8, command=self.add3_btn_clicked)
        self.add_btn4 = Button(self.window, text='Add4', width=8, command=self.add4_btn_clicked)

        self.plot_update_btn2 = Button(self.window, text="Plot Update", width=20, command=self.update_button2)

        # listbox
        self.list_box_1 = Listbox(self.window, selectmode="multiple", height=5)

        # pre-created figures
        self.selected_list_preview = []
        self.legend = None
        self.create_figure()
        self.top_plot_update()
        self.botton_plot_update()

        # etc
        self.filename = None
        self.data = None
        self.combined_plot_dict = {}

        # init
        self.window_init_setting()

    def window_init_setting(self):
        self.window.title(WINDOW_TITLE)
        self.window.geometry(WINDOW_GEOMETRY)

        # first direction
        self.first_direction_label.place(x=10, y=10)
        self.file_selection_btn.place(x=10, y=35)
        self.selected_file_label.place(x=10, y=60)

        # second direction
        self.second_direction_label.place(x=10, y=105)
        self.plot_update_btn1.place(x=120, y=105)
        self.list_box_1.place(x=10, y=130)
        self.curves_merging_btn.place(x=10, y=230)

        self.entry_strain_rate1.place(x=10, y=260)
        self.add_btn1.place(x=120, y=262)
        self.entry_strain_rate2.place(x=10, y=290)
        self.add_btn2.place(x=120, y=292)
        self.entry_strain_rate3.place(x=10, y=320)
        self.add_btn3.place(x=120, y=322)
        self.entry_strain_rate4.place(x=10, y=350)
        self.add_btn4.place(x=120, y=352)
        self.plot_update_btn2.place(x=10, y=382)

    def create_figure(self):
        self.fig1 = plt.Figure(figsize=FIGSIZE, dpi=100, facecolor='grey')
        self.fig2 = plt.Figure(figsize=FIGSIZE, dpi=100, facecolor='grey')
        self.ax1 = self.fig1.add_subplot(111)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.window)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.window)


    def select_file(self):
        self.filename = filedialog.askopenfilename(
            title="Open a file",
            initialdir='/',
            filetypes=FILETYPES
        )
        self.load_file(self.filename)
        self.selected_file_label.config(text=f"{self.filename.split('/')[-1]}")

    def load_file(self, selected_file_path):
        self.data = file_manager.txt_to_df(selected_file_path)
        self.list_up_box()

    def list_up_box(self):
        curves_name = file_manager.return_curves_name_array(self.data)
        for i in range(len(curves_name)):
            self.list_box_1.insert(i, curves_name[i])

    def update_button1(self):
        # initializing
        self.fig1.clear()
        self.ax1.clear()
        self.create_figure()

        # updating
        self.return_selected_item()
        self.curves_selection()
        self.plot_setting()
        self.top_plot_update()

    def update_button2(self):
        # initializing
        self.fig2.clear()
        self.ax2.clear()
        self.create_figure()

        # updating
        self.combined_averaged_curves_plot()
        self.plot_setting()
        self.botton_plot_update()


    def return_selected_item(self):
        self.selected_list_preview = []
        for i in self.list_box_1.curselection():
            self.selected_list_preview.append(self.list_box_1.get(i))

    def curves_selection(self):
        for i in range(len(self.selected_list_preview)):
            x_name = f"X_{self.selected_list_preview[i]}_Pd_[nm]"
            y_name = f"Y_{self.selected_list_preview[i]}_Hardness (H)_[MPa]"
            x = self.data[x_name]
            y = self.data[y_name]
            self.ax1.plot(x, y, label=f'{self.selected_list_preview[i]}')

    def plot_setting(self):
        self.ax1.set_xlabel('Pd [nm]')
        self.ax1.set_ylim([0, 1900])

        self.ax2.set_xlabel('Pd [nm]')
        self.ax2.set_ylim([0, 1900])

    def top_plot_update(self):
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.window)
        self.canvas1.get_tk_widget().place(x=200, y=10)

    def botton_plot_update(self):
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.window)
        self.canvas2.get_tk_widget().place(x=200, y=400)

    def merging_curve_button(self):
        # initializing
        self.fig1.clear()
        self.ax1.clear()
        self.create_figure()

        self.curves_merging()
        self.plot_setting()
        self.top_plot_update()

    def curves_merging(self):
        df = analyzer.averaged_curve(self.data, self.selected_list_preview)
        self.current_merged_curve = df

        self.ax1.plot(df['x'], df['mean'])
        self.ax1.fill_between(df['x'], df['mean'] - df['std'], df['mean'] + df['std'], alpha=0.2)
        # plt.xlabel('Pd (Nm)')
        # plt.ylabel('Hardness (MPa)')
        # plt.xlim([0, 1900])
        # plt.ylim([-50, 1500])
        # plt.show()

    def add1_btn_clicked(self):
        self.merged_to_dict(self.entry_strain_rate1)

    def add2_btn_clicked(self):
        self.merged_to_dict(self.entry_strain_rate2)

    def add3_btn_clicked(self):
        self.merged_to_dict(self.entry_strain_rate3)

    def add4_btn_clicked(self):
        self.merged_to_dict(self.entry_strain_rate4)

    def merged_to_dict(self, entry_value):
        key_strain_rate = entry_value.get()
        self.combined_plot_dict[key_strain_rate] = self.current_merged_curve

    def combined_averaged_curves_plot(self):
        for strain_rate, dataframe in self.combined_plot_dict.items():
            self.ax2.plot(dataframe['x'], dataframe['mean'])
            self.ax2.fill_between(dataframe['x'], dataframe['mean'] - dataframe['std'],
                                  dataframe['mean'] + dataframe['std'], alpha=0.2)


def main():
    nanoindentation_analysis = NanoindentationAnalysis()
    nanoindentation_analysis.window.mainloop()


main()
