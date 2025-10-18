import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_biomass_and_carbon(input_path, output_path):
    """
    Calculates biomass and carbon stock for trees.

    Args:
        input_path (str): Path to the cleaned vegetation data CSV.
        output_path (str): Path to save the data with ecological calculations.
    """
    logging.info(f"Starting ecological calculations for {input_path}")
    df_trees = pd.read_csv(input_path)

    # --- Ecological Calculations ---
    wood_density_map = {
        'Ficus racemosa': 0.48, 
        'Pongamia pinnata': 0.65, 
        'Indian drumstick': 0.45,
        'Azadirachta indica': 0.58,
        'Caesalpinia pulcherrima': 0.6, # Using a generic value for ornamental tree
        'Hibiscus rosa-sinensis': 0.5, # Using a generic value for large shrub/small tree
        'Neem': 0.58, # Synonym for Azadirachta indica
        'default': 0.62
    }
    df_trees['Wood_Density_g_cm3'] = df_trees['Species'].map(wood_density_map).fillna(wood_density_map['default'])

    # Method 1 (Height-Inclusive)
    df_trees['AGB_M1_kg'] = 0.0673 * (df_trees['Wood_Density_g_cm3'] * df_trees['Effective_DBH_cm']**2 * df_trees['Height_m'])**0.976
    df_trees['Carbon_Stock_M1_kg'] = (df_trees['AGB_M1_kg'] * 1.26) * 0.47
    df_trees['CO2_Eq_M1_kg'] = df_trees['Carbon_Stock_M1_kg'] * (44/12)

    # Method 2 (Height-Exclusive)
    D = df_trees['Effective_DBH_cm']
    rho = df_trees['Wood_Density_g_cm3']
    df_trees['AGB_M2_kg'] = np.exp(-1.803 - 0.976 * np.log(rho) + 2.673 * np.log(D) - 0.0299 * (np.log(D))**2)
    df_trees['Carbon_Stock_M2_kg'] = (df_trees['AGB_M2_kg'] * 1.26) * 0.47
    df_trees['CO2_Eq_M2_kg'] = df_trees['Carbon_Stock_M2_kg'] * (44/12)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_trees.to_csv(output_path, index=False)
    logging.info(f"Ecological calculations complete. Results saved to {output_path}")
    
    return df_trees

if __name__ == '__main__':
    input_file = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\data\\cleaned_vegetation_data_trees.csv'
    output_file = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\data\\ecological_analysis_results.csv'
    calculate_biomass_and_carbon(input_file, output_file)