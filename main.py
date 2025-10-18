import os
import logging
from src.data_processing.clean_data import clean_vegetation_data
from src.canopy_analysis.run_canopy_analysis import run_canopy_analysis
from src.ecological_analysis.calculate_biomass import calculate_biomass_and_carbon
from src.visualization.generate_plots import generate_all_plots

def main():
    """
    Main function to run the entire vegetation analysis pipeline.
    """
    # --- Configuration ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Input files
    raw_veg_data = os.path.join(BASE_DIR, 'data', 'plots-field-data','plots-field-data.csv')
    canopy_images_dir = os.path.join(BASE_DIR, 'data', 'canopy_input_images')

    # Output files and directories
    output_dir = os.path.join(BASE_DIR, 'output')
    log_dir = os.path.join(output_dir, 'logs')
    data_dir = os.path.join(output_dir, 'data')
    image_dir = os.path.join(output_dir, 'images')
    canopy_image_dir = os.path.join(image_dir, 'canopy_analysis')

    cleaned_veg_full_path = os.path.join(data_dir, 'cleaned_vegetation_data_full.csv')
    cleaned_veg_trees_path = os.path.join(data_dir, 'cleaned_vegetation_data_trees.csv')
    canopy_results_path = os.path.join(data_dir, 'canopy_analysis_results.csv')
    eco_results_path = os.path.join(data_dir, 'ecological_analysis_results.csv')
    
    # --- Logging Setup ---
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'pipeline.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.info("--- Starting Vegetation Analysis Pipeline ---")

    # --- Step 1: Clean Data ---
    try:
        logging.info("Step 1: Cleaning vegetation data.")
        clean_vegetation_data(raw_veg_data, cleaned_veg_full_path, cleaned_veg_trees_path)
        logging.info("Step 1: Completed.")
    except Exception as e:
        logging.error(f"Step 1 failed: {e}")
        return

    # --- Step 2: Canopy Analysis ---
    try:
        logging.info("Step 2: Running canopy analysis.")
        run_canopy_analysis(canopy_images_dir, canopy_results_path, canopy_image_dir)
        logging.info("Step 2: Completed.")
    except Exception as e:
        logging.error(f"Step 2 failed: {e}")
        return

    # --- Step 3: Ecological Calculations ---
    try:
        logging.info("Step 3: Calculating biomass and carbon.")
        calculate_biomass_and_carbon(cleaned_veg_trees_path, eco_results_path)
        logging.info("Step 3: Completed.")
    except Exception as e:
        logging.error(f"Step 3 failed: {e}")
        return

    # --- Step 4: Generate Plots ---
    try:
        logging.info("Step 4: Generating plots.")
        generate_all_plots(cleaned_veg_full_path, eco_results_path, canopy_results_path, image_dir)
        logging.info("Step 4: Completed.")
    except Exception as e:
        logging.error(f"Step 4 failed: {e}")
        return

    logging.info("--- Vegetation Analysis Pipeline Finished Successfully ---")

if __name__ == '__main__':
    main()
