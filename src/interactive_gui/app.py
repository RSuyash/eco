import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import sys
import threading
from src.interactive_gui.logger import logger
import sv_ttk
from src.interactive_gui.visualizations.plant_composition import create_plant_composition_plot
from src.interactive_gui.visualizations.carbon_stock import create_carbon_stock_plot
from src.interactive_gui.visualizations.canopy_cover import create_canopy_cover_plot
from src.interactive_gui.visualizations.canopy_analysis_images import create_canopy_analysis_images

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class VegetationAnalysisApp(tk.Tk):
    def __init__(self, base_dir, data_dir, image_dir):
        super().__init__()
        logger.info("Initializing Vegetation Analysis Dashboard...")

        self.title("Interactive Vegetation Analysis Dashboard")
        self.geometry("1500x950")
        sv_ttk.set_theme("light")

        self.base_dir = base_dir
        self.data_dir = data_dir
        self.image_dir = image_dir
        self.plot_numbers = []

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.report_callback_exception = self.log_exceptions

        self.create_widgets()
        self.load_data()

    def log_exceptions(self, exc, val, tb):
        logger.critical("Unhandled exception", exc_info=(exc, val, tb))
        self.show_error(f"An unexpected error occurred. Please check the log file for details.")

    def create_widgets(self):
        self.status_bar = ttk.Label(self, text="Initializing...", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_label = ttk.Label(header_frame, text="Vegetation Analysis Dashboard", font=("Arial", 22, "bold"))
        header_label.pack(side=tk.LEFT)

        plot_selection_frame = ttk.Frame(header_frame)
        plot_selection_frame.pack(side=tk.RIGHT, anchor='s')
        plot_label = ttk.Label(plot_selection_frame, text="Select Plot:", font=("Arial", 11))
        plot_label.pack(side=tk.LEFT, padx=(0, 8))
        self.selected_plot = tk.StringVar()
        self.plot_menu = ttk.Combobox(plot_selection_frame, textvariable=self.selected_plot, state='disabled', width=12)
        self.plot_menu.pack(side=tk.LEFT)
        self.plot_menu.bind("<<ComboboxSelected>>", self.update_plot_data)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}
        tab_names = ["General", "Carbon Analysis", "Canopy Cover", "Canopy Analysis Images"]
        for tab_name in tab_names:
            scrollable_tab = ScrollableFrame(self.notebook)
            self.notebook.add(scrollable_tab, text=tab_name, state='disabled')
            self.tabs[tab_name] = scrollable_tab.scrollable_frame

    def set_status(self, text):
        self.status_bar.config(text=text)
        self.update_idletasks()

    def set_busy(self, is_busy):
        if is_busy:
            self.config(cursor="watch")
        else:
            self.config(cursor="")
        self.update_idletasks()

    def load_data(self):
        self.set_status("Loading data...")
        self.set_busy(True)
        threading.Thread(target=self._load_data_thread, daemon=True).start()

    def _load_data_thread(self):
        try:
            logger.info(f"Loading data from: {os.path.abspath(self.data_dir)}")
            self.df_full = pd.read_csv(os.path.join(self.data_dir, 'cleaned_vegetation_data_full.csv'))
            self.df_trees = pd.read_csv(os.path.join(self.data_dir, 'ecological_analysis_results.csv'))
            self.df_canopy = pd.read_csv(os.path.join(self.data_dir, 'canopy_analysis_results.csv'))
            self.plot_numbers = sorted(self.df_full['Plot No.'].unique())
            logger.info(f"Successfully loaded data for plots: {self.plot_numbers}")
            self.after(0, self.on_data_loaded)
        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e.filename}")
            self.after(0, lambda: self.show_error(f"Data file not found: {e.filename}"))
        finally:
            self.after(0, lambda: self.set_busy(False))

    def on_data_loaded(self):
        self.plot_menu.config(values=self.plot_numbers, state='readonly')
        for tab_name in self.tabs:
            self.notebook.tab(self.tabs[tab_name].master.master, state='normal')
        if self.plot_numbers:
            self.plot_menu.set(self.plot_numbers[0])
            self.update_plot_data()
        self.set_status("Data loaded successfully.")

    def update_plot_data(self, event=None):
        plot_no = self.selected_plot.get()
        if not plot_no:
            return
        
        self.set_status(f"Loading data for Plot {plot_no}...")
        self.set_busy(True)
        
        threading.Thread(target=self._update_plots_thread, args=(plot_no,), daemon=True).start()

    def _update_plots_thread(self, plot_no):
        try:
            logger.info(f"Updating plots for Plot {plot_no}")
            self.after(0, self.display_general_data, plot_no)
            self.after(0, self.display_carbon_data, plot_no)
            self.after(0, self.display_canopy_data, plot_no)
            self.after(0, self.display_canopy_images, plot_no)
            self.after(0, lambda: self.set_status(f"Displaying data for Plot {plot_no}"))
        except Exception as e:
            logger.error(f"Failed to update plot data for Plot {plot_no}: {e}", exc_info=True)
            self.after(0, lambda: self.show_error(f"Failed to update plot data: {e}"))
        finally:
            self.after(0, lambda: self.set_busy(False))

    def clear_tab(self, tab_name):
        for widget in self.tabs[tab_name].winfo_children():
            widget.destroy()

    def display_general_data(self, plot_no):
        self.clear_tab("General")
        plot_data = self.df_full[self.df_full['Plot No.'] == int(plot_no)]
        create_plant_composition_plot(self.tabs["General"], plot_data, plot_no)

    def display_carbon_data(self, plot_no):
        self.clear_tab("Carbon Analysis")
        plot_data = self.df_trees[self.df_trees['Plot No.'] == int(plot_no)]
        create_carbon_stock_plot(self.tabs["Carbon Analysis"], plot_data, plot_no)

    def display_canopy_data(self, plot_no):
        self.clear_tab("Canopy Cover")
        plot_data = self.df_canopy[self.df_canopy['plot_id'] == f'plot-{plot_no}']
        create_canopy_cover_plot(self.tabs["Canopy Cover"], plot_data, plot_no, self.image_dir)

    def display_canopy_images(self, plot_no):
        self.clear_tab("Canopy Analysis Images")
        input_image_dir = os.path.join(self.base_dir, 'data', 'canopy_input_images')
        create_canopy_analysis_images(self.tabs["Canopy Analysis Images"], self.image_dir, input_image_dir, f'plot-{plot_no}')

    def show_error(self, message):
        logger.error(f"Displaying error to user: {message}")
        error_dialog = tk.Toplevel(self)
        error_dialog.title("Error")
        error_dialog.transient(self)
        label = ttk.Label(error_dialog, text=message, wraplength=380, font=("Arial", 11))
        label.pack(pady=20, padx=20)
        button = ttk.Button(error_dialog, text="OK", command=error_dialog.destroy)
        button.pack(pady=10)

    def on_closing(self):
        logger.info("Dashboard closed.")
        self.destroy()

if __name__ == "__main__":
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(BASE_DIR, 'output', 'data')
        image_dir = os.path.join(BASE_DIR, 'output', 'images')
        
        app = VegetationAnalysisApp(BASE_DIR, data_dir, image_dir)
        app.mainloop()
    except Exception as e:
        logger.critical("Fatal error on startup", exc_info=True)