import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.interactive_gui.logger import logger

# Helper functions for creating plots, moved outside the main function
def _create_quadrant_comparison_plot(parent, plot_data, plot_no):
    logger.info(f"Creating quadrant comparison plot for Plot {plot_no}")
    try:
        for widget in parent.winfo_children():
            widget.destroy()
        colors = {'m1': '#4E79A7', 'm2': '#F28E2B'}
        fig = Figure(figsize=(10, 5), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#F7F7F7')

        plot_summary = plot_data.groupby('Quadrant')[['CO2_Eq_M1_kg', 'CO2_Eq_M2_kg']].sum().reindex(['Q1', 'Q2', 'Q3', 'Q4'])
        quadrants = plot_summary.index
        x = np.arange(len(quadrants))
        width = 0.35

        rects1 = ax.bar(x - width/2, plot_summary['CO2_Eq_M1_kg'], width, label='Method 1', color=colors['m1'])
        rects2 = ax.bar(x + width/2, plot_summary['CO2_Eq_M2_kg'], width, label='Method 2', color=colors['m2'])

        ax.set_title(f'Comparison of CO₂ Sequestered by Quadrant for Plot {plot_no}', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Quadrant', fontsize=11)
        ax.set_ylabel('Total CO₂ Equivalent (kg)', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(quadrants)
        ax.legend(frameon=False, fontsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.bar_label(rects1, padding=3, fmt='%.1f', fontsize=8)
        ax.bar_label(rects2, padding=3, fmt='%.1f', fontsize=8)

        fig.tight_layout(pad=2.0)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        logger.error(f"Error in _create_quadrant_comparison_plot: {e}", exc_info=True)

def _create_tree_contribution_plot(parent, plot_data, plot_no):
    logger.info(f"Creating tree contribution plot for Plot {plot_no}")
    try:
        for widget in parent.winfo_children():
            widget.destroy()
        colors = {'m1': '#4E79A7'}
        fig = Figure(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#F7F7F7')

        tree_data = plot_data.nlargest(20, 'CO2_Eq_M1_kg').sort_values(by='CO2_Eq_M1_kg', ascending=True)
        tree_labels = [f"{row['Species']} (ID: {row['ID']})" for index, row in tree_data.iterrows()]

        ax.barh(tree_labels, tree_data['CO2_Eq_M1_kg'], color=colors['m1'])

        ax.set_title(f'Top 20 Trees by Contribution to Carbon Stock (Method 1)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('CO₂ Equivalent (kg)', fontsize=11)
        ax.set_ylabel('Tree', fontsize=11)
        ax.grid(axis='x', linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        fig.tight_layout(pad=2.0)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        logger.error(f"Error in _create_tree_contribution_plot: {e}", exc_info=True)

def create_carbon_stock_plot(parent_tab, plot_data, plot_no):
    """Creates and embeds carbon stock plots with button-based navigation."""
    logger.info(f"Initializing carbon stock tab for Plot {plot_no}")
    try:
        for widget in parent_tab.winfo_children():
            widget.destroy()

        if plot_data.empty:
            logger.warning(f"No carbon data available for Plot {plot_no}")
            ttk.Label(parent_tab, text=f"No carbon data available for Plot {plot_no}").pack(pady=20, padx=20)
            return

        main_frame = ttk.Frame(parent_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        explanation_frame = ttk.Frame(main_frame, padding=(10, 10), style='Card.TFrame')
        explanation_frame.pack(fill=tk.X, pady=(0, 15))
        explanation_title = ttk.Label(explanation_frame, text="Carbon Estimation Methods", font=("Arial", 12, "bold"))
        explanation_title.pack(anchor=tk.W)
        explanation_text = (
            "This analysis uses two allometric equations to estimate Aboveground Biomass (AGB):\n\n"
            "- Method 1 (Height-Inclusive): Incorporates tree height for a comprehensive estimate.\n"
            "- Method 2 (Height-Exclusive): Relies only on Diameter at Breast Height (DBH)."
        )
        explanation_label = ttk.Label(explanation_frame, text=explanation_text, wraplength=1000, justify=tk.LEFT)
        explanation_label.pack(anchor=tk.W, pady=(5, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        
        # Use lambda to ensure commands are stable
        quadrant_btn = ttk.Button(button_frame, text="Compare Quadrants", 
                                  command=lambda: _create_quadrant_comparison_plot(plot_frame, plot_data, plot_no), 
                                  style="Accent.TButton")
        quadrant_btn.pack(side=tk.LEFT, padx=(0, 10))

        tree_btn = ttk.Button(button_frame, text="View Tree Contributions", 
                              command=lambda: _create_tree_contribution_plot(plot_frame, plot_data, plot_no))
        tree_btn.pack(side=tk.LEFT)

        # Show the default plot
        _create_quadrant_comparison_plot(plot_frame, plot_data, plot_no)

    except Exception as e:
        logger.error(f"Error initializing carbon stock tab for Plot {plot_no}: {e}", exc_info=True)
        ttk.Label(parent_tab, text=f"Error generating content: {e}").pack(pady=20, padx=20)