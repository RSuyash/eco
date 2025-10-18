import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'sans-serif'; plt.rcParams['figure.dpi'] = 120
plt.rcParams['axes.titleweight'] = 'bold'; plt.rcParams['axes.labelweight'] = 'bold'

def plot_nested_sampling_design(output_path):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal', adjustable='box'); ax.set_xlim(-1, 11); ax.set_ylim(-1, 11)
    ax.set_xticks(np.arange(0, 11, 1)); ax.set_yticks(np.arange(0, 11, 1))
    fig.suptitle("Figure 1: Nested Sampling Plot Design", fontsize=18)
    ax.set_title("10x10m plot with quadrants numbered anti-clockwise from top-left.", fontsize=12, pad=10)
    ax.set_xlabel("West-East Direction (meters)", fontsize=12); ax.set_ylabel("South-North Direction (meters)", fontsize=12)
    main_plot = patches.Rectangle((0, 0), 10, 10, linewidth=4, edgecolor='black', facecolor='none', zorder=10)
    ax.add_patch(main_plot)
    quadrant_coords = {"Q1": (0, 5), "Q2": (0, 0), "Q3": (5, 0), "Q4": (5, 5)}
    for name, (x, y) in quadrant_coords.items():
        ax.add_patch(patches.Rectangle((x, y), 5, 5, linewidth=2.5, edgecolor='#003366', facecolor='#aaccff', alpha=0.6))
        ax.text(x + 2.5, y + 2.5, name, ha='center', va='center', fontsize=14, fontweight='bold', color='#003366')
    for x, y in [(0, 0), (9, 0), (0, 9), (9, 9)]:
        ax.add_patch(patches.Rectangle((x, y), 1, 1, linewidth=2, edgecolor='#990000', facecolor='#ff9999', alpha=0.8))
    legend_patches = [patches.Patch(edgecolor='black', facecolor='none', linewidth=4, label='10x10m Main Plot'),
                      patches.Patch(edgecolor='#003366', facecolor='#aaccff', alpha=0.6, label='5x5m Quadrant'),
                      patches.Patch(edgecolor='#990000', facecolor='#ff9999', alpha=0.8, label='1x1m Sub-plot (Herbs)')]
    ax.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, ncol=3, fontsize=11)
    fig.tight_layout(rect=[0, 0.05, 1, 0.95]); plt.savefig(output_path)
    plt.close(fig)
    logging.info(f"Generated plot: {output_path}")

def plot_plant_composition(df_cleaned, output_path):
    counts_per_plot = df_cleaned.groupby(['Quadrant', 'Type'])['Number'].sum().unstack(fill_value=0).reindex(['Q1','Q2','Q3','Q4'])
    fig, ax = plt.subplots(figsize=(10, 7))
    counts_per_plot.plot(kind='bar', stacked=True, ax=ax, width=0.7)
    fig.suptitle('Figure 2: Plant Composition by Quadrant', fontsize=18)
    ax.set_title("Shows the total count and type of plants recorded in each quadrant.", fontsize=12, pad=10)
    ax.set_xlabel('Quadrant', fontsize=12); ax.set_ylabel('Total Number of Individuals', fontsize=12)
    ax.tick_params(axis='x', rotation=0, labelsize=11)
    ax.legend(title='Plant Type', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=11, title_fontsize=12)
    fig.tight_layout(rect=[0, 0, 0.88, 0.96]); plt.savefig(output_path)
    plt.close(fig)
    logging.info(f"Generated plot: {output_path}")

def plot_schematic_plant_distribution(df_cleaned, df_trees, output_path):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal', adjustable='box'); ax.set_xlim(-1, 11); ax.set_ylim(-1, 11)
    ax.set_xticks(np.arange(0, 11, 1)); ax.set_yticks(np.arange(0, 11, 1))
    fig.suptitle("Figure 3: Schematic Plant Distribution", fontsize=18)
    ax.set_title("Structured locations of plants. Circle size is scaled by tree diameter or count.", fontsize=12, pad=10)
    ax.set_xlabel("West-East Direction (meters)", fontsize=12); ax.set_ylabel("South-North Direction (meters)", fontsize=12)
    quadrant_coords = {"Q1": (0, 5), "Q2": (0, 0), "Q3": (5, 0), "Q4": (5, 5)}
    plot_centers = {"Q1": (2.5, 7.5), "Q2": (2.5, 2.5), "Q3": (7.5, 2.5), "Q4": (7.5, 7.5)}
    for name, (x, y) in quadrant_coords.items():
        ax.add_patch(patches.Rectangle((x, y), 5, 5, linewidth=1.5, edgecolor='lightgrey', facecolor='#f0fff0', alpha=0.5, zorder=1))
        ax.text(x + 2.5, y + 2.5, name, ha='center', va='center', fontsize=12, color='darkgrey', zorder=2)

    plant_colors = {'Tree': '#006400', 'Sapling': '#FF8C00', 'Shrub': '#8A2BE2', 'Herb': '#556B2F'}
    df_viz = pd.merge(df_cleaned, df_trees[['Quadrant', 'ID', 'Effective_DBH_cm']], on=['Quadrant', 'ID'], how='left')

    for quadrant_name, center_coords in plot_centers.items():
        quadrant_data = df_viz[df_viz['Quadrant'] == quadrant_name].reset_index(drop=True)
        num_items = len(quadrant_data)
        if num_items == 0: continue
        grid_size = int(np.ceil(np.sqrt(num_items)))
        x_points = np.linspace(center_coords[0] - 1.5, center_coords[0] + 1.5, grid_size) if grid_size > 1 else [center_coords[0]]
        y_points = np.linspace(center_coords[1] - 1.5, center_coords[1] + 1.5, grid_size) if grid_size > 1 else [center_coords[1]]
        positions = [(x, y) for y in y_points for x in x_points]

        for i, (index, row) in enumerate(quadrant_data.iterrows()):
            if i >= len(positions): break
            plot_x, plot_y = positions[i]
            
            if row['Type'] == 'Tree' and pd.notna(row['Effective_DBH_cm']):
                size = row['Effective_DBH_cm'] * 30
                label = f"ID {row['ID']}: DBH {row['Effective_DBH_cm']:.1f}cm"
            else:
                size = row['Number'] * 35
                label = f"ID {row['ID']}: {int(row['Number'])} {row['Type']}(s)"
            
            ax.scatter(plot_x, plot_y, s=size, c=plant_colors.get(row['Type'], 'black'), alpha=0.9, label=row['Type'], zorder=5, edgecolors='black', linewidth=0.5)
            text_y_offset = 0.7
            if i % 2 == 1: text_y_offset = -0.7
            ax.text(plot_x, plot_y + text_y_offset, label, ha='center', va='center', fontsize=8, weight='semibold', zorder=6,
                    bbox=dict(facecolor='white', alpha=0.85, edgecolor='none', boxstyle='round,pad=0.2'))

    legend_handles = [patches.Patch(color=color, label=label) for label, color in plant_colors.items()]
    ax.legend(handles=legend_handles, title='Plant Type', loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, fontsize=12, borderpad=1, labelspacing=1.2)
    fig.tight_layout(rect=[0, 0, 0.88, 0.95])
    plt.savefig(output_path)
    plt.close(fig)
    logging.info(f"Generated plot: {output_path}")

def plot_species_distribution(df_cleaned, output_path):
    species_counts = df_cleaned.dropna(subset=['Species']).groupby('Species')['Number'].sum().sort_values(ascending=False).reset_index()
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.barplot(x='Number', y='Species', data=species_counts, palette='viridis', ax=ax)
    fig.suptitle('Figure 4: Distribution of Identified Plant Species', fontsize=18)
    ax.set_title("Shows the total abundance for each species that was identified in the field.", fontsize=12, pad=10)
    ax.set_xlabel('Total Number of Individuals', fontsize=12); ax.set_ylabel('Species', fontsize=12)
    fig.tight_layout(); plt.savefig(output_path)
    plt.close(fig)
    logging.info(f"Generated plot: {output_path}")

def plot_co2_sequestered(df_trees, output_path_m1, output_path_m2):
    # Method 1
    plot_summary_m1 = df_trees.groupby('Quadrant')['CO2_Eq_M1_kg'].sum().reset_index()
    fig5, ax5 = plt.subplots(figsize=(10, 7))
    bars = sns.barplot(x='Quadrant', y='CO2_Eq_M1_kg', data=plot_summary_m1, palette='mako', ax=ax5, order=['Q1','Q2','Q3','Q4'])
    fig5.suptitle('Figure 5: CO₂ Sequestered by Quadrant (Method 1)', fontsize=18)
    ax5.set_title("Estimates based on the Height-Inclusive allometric equation.", fontsize=12, pad=10)
    ax5.set_xlabel('Quadrant', fontsize=12); ax5.set_ylabel('Total CO₂ Equivalent (kg)', fontsize=12)
    for bar in bars.patches:
        ax5.annotate(f'{bar.get_height():.0f} kg', (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha='center', va='center', size=11, weight='bold', xytext=(0, 8), textcoords='offset points')
    ax5.set_ylim(0, plot_summary_m1['CO2_Eq_M1_kg'].max() * 1.2)
    fig5.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig(output_path_m1)
    plt.close(fig5)
    logging.info(f"Generated plot: {output_path_m1}")

    # Method 2
    plot_summary_m2 = df_trees.groupby('Quadrant')['CO2_Eq_M2_kg'].sum().reset_index()
    fig7, ax7 = plt.subplots(figsize=(10, 7))
    bars = sns.barplot(x='Quadrant', y='CO2_Eq_M2_kg', data=plot_summary_m2, palette='viridis', ax=ax7, order=['Q1','Q2','Q3','Q4'])
    fig7.suptitle('Figure 7: CO₂ Sequestered by Quadrant (Method 2)', fontsize=18)
    ax7.set_title("Estimates based on the robust Height-Exclusive (DBH-only) allometric equation.", fontsize=12, pad=10)
    ax7.set_xlabel('Quadrant', fontsize=12); ax7.set_ylabel('Total CO₂ Equivalent (kg)', fontsize=12)
    for bar in bars.patches:
        ax7.annotate(f'{bar.get_height():.0f} kg', (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha='center', va='center', size=11, weight='bold', xytext=(0, 8), textcoords='offset points')
    ax7.set_ylim(0, plot_summary_m2['CO2_Eq_M2_kg'].max() * 1.2)
    fig7.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig(output_path_m2)
    plt.close(fig7)
    logging.info(f"Generated plot: {output_path_m2}")

def plot_tree_contribution(df_trees, output_path_m1, output_path_m2):
    df_trees['Tree_Label'] = df_trees['Quadrant'] + " - ID " + df_trees['ID'].astype(str)

    # Method 1
    fig6, ax6 = plt.subplots(figsize=(10, 8))
    df_m1 = df_trees.sort_values('Carbon_Stock_M1_kg', ascending=True)
    ax6.barh(df_m1['Tree_Label'], df_m1['Carbon_Stock_M1_kg'], color='skyblue')
    ax6.set_xlabel('Carbon Stock (kg)')
    ax6.set_ylabel('Tree')
    fig6.suptitle('Figure 6: Tree Contribution to Total Carbon Stock (Method 1)', fontsize=18)
    ax6.set_title("Shows the carbon stored by each tree using Method 1.", fontsize=12, pad=10)
    fig6.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig(output_path_m1)
    plt.close(fig6)
    logging.info(f"Generated plot: {output_path_m1}")

    # Method 2
    fig8, ax8 = plt.subplots(figsize=(10, 8))
    df_m2 = df_trees.sort_values('Carbon_Stock_M2_kg', ascending=True)
    ax8.barh(df_m2['Tree_Label'], df_m2['Carbon_Stock_M2_kg'], color='lightcoral')
    ax8.set_xlabel('Carbon Stock (kg)')
    ax8.set_ylabel('Tree')
    fig8.suptitle('Figure 8: Tree Contribution to Total Carbon Stock (Method 2)', fontsize=18)
    ax8.set_title("Shows the carbon stored by each tree using Method 2.", fontsize=12, pad=10)
    fig8.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig(output_path_m2)
    plt.close(fig8)
    logging.info(f"Generated plot: {output_path_m2}")

def plot_comparison_figures(df_trees, output_path_co2, output_path_biomass):
    # CO2 Comparison
    plot_summary_comp = df_trees.groupby('Quadrant').agg(CO2_M1=('CO2_Eq_M1_kg', 'sum'), CO2_M2=('CO2_Eq_M2_kg', 'sum')).reset_index()
    plot_summary_melted = plot_summary_comp.melt(id_vars='Quadrant', var_name='Method', value_name='CO2_kg')
    plot_summary_melted['Method'] = plot_summary_melted['Method'].map({'CO2_M1': 'M1 (Height-Inclusive)', 'CO2_M2': 'M2 (Height-Exclusive)'})
    fig9, ax9 = plt.subplots(figsize=(12, 8))
    sns.barplot(x='Quadrant', y='CO2_kg', hue='Method', data=plot_summary_melted, palette='cividis', ax=ax9, order=['Q1','Q2','Q3','Q4'])
    fig9.suptitle('Figure 9: Comparison of CO₂ Sequestered by Quadrant', fontsize=18)
    ax9.set_title("Shows the range of estimates between the two allometric equations for each quadrant.", fontsize=12, pad=10)
    ax9.set_xlabel('Quadrant', fontsize=12); ax9.set_ylabel('Total CO₂ Equivalent (kg)', fontsize=12)
    ax9.legend(title='Calculation Method', fontsize=11, title_fontsize=12); fig9.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig(output_path_co2)
    plt.close(fig9)
    logging.info(f"Generated plot: {output_path_co2}")

    # Biomass Comparison
    fig10, ax10 = plt.subplots(figsize=(12, 8))
    sns.scatterplot(data=df_trees, x='Effective_DBH_cm', y='AGB_M1_kg', s=200, ax=ax10, label='Method 1 (Height-Inclusive)', zorder=10)
    sns.scatterplot(data=df_trees, x='Effective_DBH_cm', y='AGB_M2_kg', s=250, ax=ax10, marker='X', label='Method 2 (Height-Exclusive)', zorder=10)
    fig10.suptitle('Figure 10: Comparison of Biomass Estimates vs. Tree Diameter', fontsize=18)
    ax10.set_title("Each tree is represented by two points, showing the biomass estimate from each method.", fontsize=12, pad=10)
    ax10.set_xlabel('Effective Stem Diameter (cm)', fontsize=12); ax10.set_ylabel('Estimated Aboveground Biomass (kg)', fontsize=12)
    ax10.legend(fontsize=11, title_fontsize=12); fig10.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig(output_path_biomass)
    plt.close(fig10)
    logging.info(f"Generated plot: {output_path_biomass}")

def plot_canopy_analysis(df_canopy, output_path_cover, output_path_lai):
    # Canopy Cover
    fig11, ax11 = plt.subplots(figsize=(10, 7))
    bars = sns.barplot(x='filename', y='canopy_cover_percent', data=df_canopy, palette='summer', ax=ax11)
    fig11.suptitle('Figure 11: Summary of Canopy Cover by Quadrant Location', fontsize=18)
    ax11.set_title("Canopy cover calculated from hemispherical photographs.", fontsize=12, pad=10)
    ax11.set_xlabel('Quadrant Location (Image Filename)', fontsize=12); ax11.set_ylabel('Canopy Cover (%)', fontsize=12)
    ax11.set_ylim(0, 100); plt.xticks(rotation=15, ha="right")
    for bar in bars.patches:
        ax11.annotate(f'{bar.get_height():.1f}%', (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha='center', va='center', size=11, weight='bold', xytext=(0, 8), textcoords='offset points')
    fig11.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig(output_path_cover)
    plt.close(fig11)
    logging.info(f"Generated plot: {output_path_cover}")

    # LAI Summary
    fig12, ax12 = plt.subplots(figsize=(10, 7))
    bars = sns.barplot(x='filename', y='estimated_lai', data=df_canopy, palette='autumn', ax=ax12)
    fig12.suptitle('Figure 12: Summary of Estimated LAI by Quadrant Location', fontsize=18)
    ax12.set_title("Leaf Area Index (LAI) estimated from canopy gap fraction.", fontsize=12, pad=10)
    ax12.set_xlabel('Quadrant Location (Image Filename)', fontsize=12); ax12.set_ylabel('Estimated Leaf Area Index (LAI)', fontsize=12)
    plt.xticks(rotation=15, ha="right")
    for bar in bars.patches:
        ax12.annotate(f'{bar.get_height():.2f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha='center', va='center', size=11, weight='bold', xytext=(0, 8), textcoords='offset points')
    ax12.set_ylim(0, df_canopy['estimated_lai'].max() * 1.2)
    fig12.tight_layout(rect=[0, 0, 1, 0.96]); plt.savefig(output_path_lai)
    plt.close(fig12)
    logging.info(f"Generated plot: {output_path_lai}")


def generate_all_plots(full_data_path, tree_data_path, canopy_data_path, output_dir):
    logging.info("Starting plot generation with per-plot categorized output.")
    
    # --- Load Data ---
    df_cleaned_full = pd.read_csv(full_data_path)
    df_trees_full = pd.read_csv(tree_data_path)
    df_canopy_full = pd.read_csv(canopy_data_path)

    # --- Generate General, non-plot-specific plots ---
    general_output_dir = os.path.join(output_dir, '00_general_overview')
    os.makedirs(general_output_dir, exist_ok=True)
    plot_nested_sampling_design(os.path.join(general_output_dir, 'figure_1_nested_sampling_plot_design.png'))
    
    # --- Generate Per-Plot Vegetation Plots ---
    if 'Plot No.' not in df_cleaned_full.columns:
        logging.error("'Plot No.' column not found. Cannot generate per-plot vegetation plots.")
    else:
        plot_numbers = df_cleaned_full['Plot No.'].unique()
        for plot_no in plot_numbers:
            logging.info(f"--- Generating vegetation plots for Plot No. {plot_no} ---")
            
            plot_output_dir = os.path.join(output_dir, f'plot-{plot_no}')
            general_dir = os.path.join(plot_output_dir, '01_general')
            carbon_dir = os.path.join(plot_output_dir, '02_carbon_analysis')
            os.makedirs(general_dir, exist_ok=True)
            os.makedirs(carbon_dir, exist_ok=True)

            # Filter data
            df_cleaned = df_cleaned_full[df_cleaned_full['Plot No.'] == plot_no]
            df_trees_with_eco = df_trees_full[df_trees_full['Plot No.'] == plot_no]

            # Generate plots
            plot_plant_composition(df_cleaned, os.path.join(general_dir, 'figure_2_plant_composition_by_quadrant.png'))
            plot_schematic_plant_distribution(df_cleaned, df_trees_with_eco, os.path.join(general_dir, 'figure_3_schematic_plant_distribution.png'))
            plot_species_distribution(df_cleaned, os.path.join(general_dir, 'figure_4_distribution_of_identified_plant_species.png'))
            
            plot_co2_sequestered(df_trees_with_eco,
                                 os.path.join(carbon_dir, 'figure_5_co2_sequestered_by_quadrant_m1.png'),
                                 os.path.join(carbon_dir, 'figure_7_co2_sequestered_by_quadrant_m2.png'))
            
            plot_tree_contribution(df_trees_with_eco,
                                   os.path.join(carbon_dir, 'figure_6_tree_contribution_to_carbon_stock_m1.png'),
                                   os.path.join(carbon_dir, 'figure_8_tree_contribution_to_carbon_stock_m2.png'))

            plot_comparison_figures(df_trees_with_eco,
                                    os.path.join(carbon_dir, 'figure_9_comparison_of_co2_sequestered_by_quadrant.png'),
                                    os.path.join(carbon_dir, 'figure_10_comparison_of_biomass_estimates_vs_tree_diameter.png'))

    # --- Generate Per-Plot Canopy Plots ---
    if 'plot_id' not in df_canopy_full.columns:
        logging.error("'plot_id' column not found. Cannot generate per-plot canopy plots.")
    else:
        canopy_plot_ids = df_canopy_full['plot_id'].unique()
        for plot_id in canopy_plot_ids: # plot_id will be 'plot-1', 'plot-2' etc.
            logging.info(f"--- Generating canopy plots for {plot_id} ---")
            
            plot_output_dir = os.path.join(output_dir, plot_id)
            canopy_dir = os.path.join(plot_output_dir, '03_canopy_analysis')
            os.makedirs(canopy_dir, exist_ok=True)

            df_canopy = df_canopy_full[df_canopy_full['plot_id'] == plot_id]
            
            plot_canopy_analysis(df_canopy,
                                 os.path.join(canopy_dir, 'figure_11_summary_of_canopy_cover.png'),
                                 os.path.join(canopy_dir, 'figure_12_summary_of_estimated_lai.png'))

    logging.info("All plots generated in per-plot categorized folders.")

if __name__ == '__main__':
    full_data_path = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\data\\cleaned_vegetation_data_full.csv'
    tree_data_path = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\data\\ecological_analysis_results.csv'
    canopy_data_path = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\data\\canopy_analysis_results.csv'
    output_dir = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\images'
    
    generate_all_plots(full_data_path, tree_data_path, canopy_data_path, output_dir)