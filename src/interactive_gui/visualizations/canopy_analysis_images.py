import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from src.interactive_gui.logger import logger

def create_canopy_analysis_images(parent_tab, image_dir, input_image_dir_base, plot_id):
    """Creates and embeds a more scientific and visually appealing image comparison gallery."""
    logger.info(f"Creating canopy analysis image gallery for {plot_id}")
    try:
        for widget in parent_tab.winfo_children():
            widget.destroy()

        analysis_image_dir = os.path.join(image_dir, 'canopy_analysis', plot_id)
        input_image_dir = os.path.join(input_image_dir_base, plot_id)

        logger.info(f"Looking for analysis images in: {os.path.abspath(analysis_image_dir)}")
        logger.info(f"Looking for input images in: {os.path.abspath(input_image_dir)}")

        if not os.path.exists(analysis_image_dir) or not os.path.exists(input_image_dir):
            logger.warning(f"Image directories not found for {plot_id}. Searched in {analysis_image_dir} and {input_image_dir}")
            ttk.Label(parent_tab, text=f"Image directories not found for {plot_id}").pack(pady=20, padx=20)
            return

        image_files = sorted([f for f in os.listdir(analysis_image_dir) if f.startswith('analysis_')])
        if not image_files:
            logger.warning(f"No 'analysis_' images found in {analysis_image_dir}")
            ttk.Label(parent_tab, text=f"No analyzed images found for {plot_id}").pack(pady=20, padx=20)
            return

        main_frame = ttk.Frame(parent_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for i, image_file in enumerate(image_files):
            original_image_file = image_file.replace('analysis_', '')
            title = original_image_file.replace('.jpg', '').replace('_', ' ').capitalize()

            # Main container for the pair
            pair_container = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
            pair_container.pack(fill=tk.X, expand=True, pady=10)

            title_label = ttk.Label(pair_container, text=title, font=("Arial", 14, "bold"))
            title_label.pack(anchor=tk.W, pady=(0, 10))

            # Frame to hold the two images side-by-side
            images_frame = ttk.Frame(pair_container)
            images_frame.pack(fill=tk.X, expand=True)
            images_frame.columnconfigure(0, weight=1)
            images_frame.columnconfigure(1, weight=1)

            # --- Original Image ---
            create_image_display(images_frame, input_image_dir, original_image_file, "Original Image", 0)
            
            # --- Analyzed Image ---
            create_image_display(images_frame, analysis_image_dir, image_file, "Analyzed Image (Binary)", 1)
            
            if i < len(image_files) - 1:
                ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

        logger.info(f"Successfully created canopy analysis image gallery for {plot_id}")

    except Exception as e:
        logger.error(f"Error creating canopy analysis image gallery for {plot_id}: {e}", exc_info=True)
        ttk.Label(parent_tab, text=f"Error loading images: {e}").pack(pady=20, padx=20)

def create_image_display(parent, img_dir, img_file, label_text, grid_col):
    """Helper function to create a more detailed and scientific labeled image display."""
    img_path = os.path.join(img_dir, img_file)
    
    img_frame = ttk.Frame(parent)
    img_frame.grid(row=0, column=grid_col, sticky="nsew", padx=10)

    if os.path.exists(img_path):
        try:
            logger.debug(f"Loading image: {img_path}")
            img = Image.open(img_path)
            original_dims = f"{img.width}x{img.height}"
            img.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(img)
            
            # Title for the image
            title_label = ttk.Label(img_frame, text=label_text, font=("Arial", 11, "bold"))
            title_label.pack(anchor=tk.W)

            # Image itself
            label = ttk.Label(img_frame, image=photo)
            label.image = photo # Keep a reference!
            label.pack(pady=5, fill=tk.X, expand=True)

            # Details frame
            details_frame = ttk.Frame(img_frame)
            details_frame.pack(anchor=tk.W)

            ttk.Label(details_frame, text=f"Source: ", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
            ttk.Label(details_frame, text=img_file, font=("Arial", 9), wraplength=350, justify=tk.LEFT).grid(row=0, column=1, sticky=tk.W)
            ttk.Label(details_frame, text=f"Dimensions: ", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W)
            ttk.Label(details_frame, text=original_dims, font=("Arial", 9)).grid(row=1, column=1, sticky=tk.W)

        except Exception as e:
            logger.error(f"Failed to load image {img_path}: {e}", exc_info=True)
            ttk.Label(img_frame, text=f"Error loading\n{img_file}").pack(anchor=tk.W)
    else:
        logger.warning(f"Image file not found: {img_path}")
        ttk.Label(img_frame, text=f"Image not found:\n{img_file}").pack(anchor=tk.W)