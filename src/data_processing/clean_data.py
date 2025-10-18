import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_vegetation_data(input_path, output_path_full, output_path_trees):
    """
    Cleans and preprocesses vegetation survey data.

    Args:
        input_path (str): The path to the raw CSV data file.
        output_path_full (str): The path to save the full cleaned CSV data file.
        output_path_trees (str): The path to save the cleaned trees CSV data file.
    """
    logging.info(f"Starting data cleaning process for {input_path}")

    df = pd.read_csv(input_path)

    # Rename columns for consistency
    df.rename(columns={
        'Quadrant ID': 'Quadrant',
        'GBH (Girth at Breast Height) - First Branch': 'Girth_cm_Stem1',
        'GBH (Girth at Breast Height) - Second Branch': 'Girth_cm_Stem2',
        'GBH (Girth at Breast Height) - Third Branch': 'Girth_cm_Stem3',
        'Height (m)': 'Height_m'
    }, inplace=True)

    df_cleaned = df.copy()
    df_cleaned['Quadrant'] = df_cleaned['Quadrant'].fillna(method='ffill')
    df_cleaned['Type'] = df_cleaned['Type'].str.strip().replace('Saplings', 'Sapling')
    
    # Add a unique ID for each plant entry
    df_cleaned['ID'] = df_cleaned.index + 1

    numeric_cols = ['Number', 'Girth_cm_Stem1', 'Girth_cm_Stem2', 'Girth_cm_Stem3', 'Height_m']
    for col in numeric_cols:
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')

    # --- Data Cleaning for Species ---
    df_cleaned['Species'] = df_cleaned['Species'].str.strip()
    df_cleaned['Species'].replace('', np.nan, inplace=True)
    
    # Save the full cleaned data
    os.makedirs(os.path.dirname(output_path_full), exist_ok=True)
    df_cleaned.to_csv(output_path_full, index=False)
    logging.info(f"Full cleaned data saved to {output_path_full}")

    df_trees = df_cleaned[df_cleaned['Type'] == 'Tree'].copy()
    df_trees.dropna(subset=['Girth_cm_Stem1'], inplace=True)
    
    # Calculate DBH for each stem
    df_trees['DBH1_cm'] = df_trees['Girth_cm_Stem1'] / np.pi
    df_trees['DBH2_cm'] = df_trees['Girth_cm_Stem2'] / np.pi
    df_trees['DBH3_cm'] = df_trees['Girth_cm_Stem3'] / np.pi
    
    # Calculate effective DBH
    df_trees['Effective_DBH_cm'] = np.sqrt(
        df_trees['DBH1_cm'].fillna(0)**2 + 
        df_trees['DBH2_cm'].fillna(0)**2 + 
        df_trees['DBH3_cm'].fillna(0)**2
    )
    
    df_trees.dropna(subset=['Height_m'], inplace=True)

    # Save the cleaned trees data
    os.makedirs(os.path.dirname(output_path_trees), exist_ok=True)
    df_trees.to_csv(output_path_trees, index=False)
    logging.info(f"Cleaned tree data saved to {output_path_trees}")
    
    return df_cleaned, df_trees

if __name__ == '__main__':
    # This allows the script to be run directly for testing
    input_file = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\data\\vegitation-survey-new.csv'
    output_file_full = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\data\\cleaned_vegetation_data_full.csv'
    output_file_trees = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\data\\cleaned_vegetation_data_trees.csv'
    clean_vegetation_data(input_file, output_file_full, output_file_trees)