import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.interactive_gui.logger import logger

def create_plant_composition_plot(parent_tab, plot_data, plot_no):
    """Creates and embeds a more visually appealing and compact plant composition plot."""
    logger.info(f"Creating plant composition plot for Plot {plot_no}")
    try:
        for widget in parent_tab.winfo_children():
            widget.destroy()

        if plot_data.empty:
            logger.warning(f"No general data available for Plot {plot_no}")
            ttk.Label(parent_tab, text=f"No general data available for Plot {plot_no}").pack(pady=20, padx=20)
            return

        logger.debug(f"Plot data for plant composition (Plot {plot_no}):\n{plot_data.head()}")

        colors = {
            'Tree': '#4E79A7', 'Shrub': '#F28E2B', 'Herb': '#59A14F',
            'Grass': '#EDC948', 'Liana': '#B07AA1'
        }

        counts_per_plot = plot_data.groupby(['Quadrant', 'Type'])['Number'].sum().unstack(fill_value=0).reindex(['Q1', 'Q2', 'Q3', 'Q4'])
        logger.debug(f"Counts per plot:\n{counts_per_plot}")

        fig = Figure(figsize=(10, 5.5), dpi=100) # Reduced height
        fig.patch.set_facecolor('#FFFFFF')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#F7F7F7')

        plant_types = [col for col in colors if col in counts_per_plot.columns]
        if not plant_types:
            logger.warning(f"No plant types to plot for Plot {plot_no}")
            ttk.Label(parent_tab, text=f"No plant types to display for Plot {plot_no}").pack(pady=20, padx=20)
            return

        counts_per_plot[plant_types].plot(kind='bar', stacked=True, ax=ax, width=0.6, color=[colors[pt] for pt in plant_types])

        for c in ax.containers:
            labels = [f'{v:.0f}' if v > 0 else '' for v in c.datavalues]
            ax.bar_label(c, labels=labels, label_type='center', color='white', fontsize=9, fontweight='bold')

        ax.set_title(f'Plant Composition for Plot {plot_no}', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Quadrant', fontsize=11)
        ax.set_ylabel('Total Number of Individuals', fontsize=11)
        ax.tick_params(axis='x', rotation=0, labelsize=10)
        ax.tick_params(axis='y', labelsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.legend(title='Plant Type', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False, fontsize=9)
        fig.tight_layout(pad=3.0)

        canvas = FigureCanvasTkAgg(fig, master=parent_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X, expand=False, padx=20, pady=20)
        logger.info(f"Successfully created plant composition plot for Plot {plot_no}")

    except Exception as e:
        logger.error(f"Error generating plant composition plot for Plot {plot_no}: {e}", exc_info=True)
        ttk.Label(parent_tab, text=f"Error generating plot: {e}").pack(pady=20, padx=20)