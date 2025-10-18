import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from PIL import Image, ImageTk
from src.interactive_gui.logger import logger

def create_canopy_cover_plot(parent_tab, plot_data, plot_no, image_dir):
    """Creates and embeds a more breathable and compact canopy cover plot and image gallery."""
    logger.info(f"Creating canopy cover plot for Plot {plot_no}")
    try:
        for widget in parent_tab.winfo_children():
            widget.destroy()

        if plot_data.empty:
            logger.warning(f"No canopy cover data available for Plot {plot_no}")
            ttk.Label(parent_tab, text=f"No canopy cover data available for Plot {plot_no}").pack(pady=20, padx=20)
            return

        logger.debug(f"Plot data for canopy cover (Plot {plot_no}):\n{plot_data.head()}")

        main_frame = ttk.Frame(parent_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Canopy Cover Bar Chart ---
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(fill=tk.X, expand=False)

        fig = Figure(figsize=(10, 5), dpi=100) # Reduced height
        fig.patch.set_facecolor('#FFFFFF')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#F7F7F7')

        plot_data['display_name'] = plot_data['filename'].str.replace('.jpg', '', regex=False).str.capitalize()
        bars = ax.bar(plot_data['display_name'], plot_data['canopy_cover_percent'], color='#59A14F', width=0.6)

        ax.set_title(f'Canopy Cover by Quadrant Location for Plot {plot_no}', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Quadrant Location', fontsize=11)
        ax.set_ylabel('Canopy Cover (%)', fontsize=11)
        ax.tick_params(axis='x', rotation=0, labelsize=10)
        ax.tick_params(axis='y', labelsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(0, 100)

        ax.bar_label(bars, fmt='%.1f%%', fontsize=9, color='#333333')
        fig.tight_layout(pad=2.0)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=20)

        # --- Image Gallery ---
        gallery_container = ttk.Frame(main_frame)
        gallery_container.pack(fill=tk.BOTH, expand=True)

        gallery_title = ttk.Label(gallery_container, text="Analyzed Canopy Images", font=("Arial", 14, "bold"))
        gallery_title.pack(pady=(0, 15), anchor=tk.W)

        analysis_image_dir = os.path.join(image_dir, 'canopy_analysis', f'plot-{plot_no}')
        logger.info(f"Looking for canopy analysis images in: {os.path.abspath(analysis_image_dir)}")

        if os.path.exists(analysis_image_dir):
            image_files = sorted([f for f in os.listdir(analysis_image_dir) if f.startswith('analysis_')])
            if not image_files:
                logger.warning(f"No 'analysis_' images found in {analysis_image_dir}")
                ttk.Label(gallery_container, text="No analyzed images found for this plot.").pack(anchor=tk.W)
                return

            image_grid_frame = ttk.Frame(gallery_container)
            image_grid_frame.pack(fill=tk.BOTH, expand=True)

            num_cols = 3
            for i, image_file in enumerate(image_files):
                row, col = divmod(i, num_cols)
                image_grid_frame.grid_columnconfigure(col, weight=1)

                image_frame = ttk.Frame(image_grid_frame, padding=10)
                image_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

                try:
                    image_path = os.path.join(analysis_image_dir, image_file)
                    logger.debug(f"Loading image: {image_path}")
                    img = Image.open(image_path)
                    img.thumbnail((320, 320))
                    photo = ImageTk.PhotoImage(img)
                    
                    label = ttk.Label(image_frame, image=photo)
                    label.image = photo # Keep a reference!
                    label.pack(pady=5)

                    filename_label = ttk.Label(image_frame, text=image_file.replace('analysis_', ''), font=("Arial", 9, "italic"))
                    filename_label.pack(pady=(0, 5))
                except Exception as img_e:
                    logger.error(f"Error loading image {image_file}: {img_e}", exc_info=True)
                    error_label = ttk.Label(image_frame, text=f"Error loading\n{image_file}")
                    error_label.pack(pady=5)
        else:
            logger.warning(f"Analysis image directory not found: {analysis_image_dir}")
            ttk.Label(gallery_container, text="No analyzed images found for this plot.").pack(anchor=tk.W)

        logger.info(f"Successfully created canopy cover plot for Plot {plot_no}")

    except Exception as e:
        logger.error(f"Error generating canopy cover content for Plot {plot_no}: {e}", exc_info=True)
        ttk.Label(parent_tab, text=f"Error generating content: {e}").pack(pady=20, padx=20)