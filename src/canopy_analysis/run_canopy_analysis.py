import cv2
import numpy as np
import os
import math
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_canopy_image(image_path, plot_id, csv_writer, output_image_dir):
    """Analyzes a single canopy image and writes the results to a CSV."""
    base_filename = os.path.basename(image_path)
    
    gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if gray_image is None:
        logging.error(f"Could not read image {image_path}")
        return

    _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    total_pixels = binary_image.size
    sky_pixels = np.sum(binary_image == 255)
    canopy_pixels = total_pixels - sky_pixels
    canopy_cover_percent = (canopy_pixels / total_pixels) * 100
    gap_fraction = sky_pixels / total_pixels

    if gap_fraction > 0:
        estimated_lai = -2 * 0.537 * math.log(gap_fraction)
    else:
        estimated_lai = float('inf')

    # --- Create new visualization ---

    # 1. Create the base color mask
    gray_bgr = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
    color_mask = np.zeros_like(gray_bgr)
    color_mask[binary_image == 0] = [0, 180, 0]  # Green for canopy
    color_mask[binary_image == 255] = [200, 50, 50] # Blue for sky

    # 2. Create the semi-transparent overlay
    alpha = 0.6 # Transparency factor
    blended_image = cv2.addWeighted(gray_bgr, 1 - alpha, color_mask, alpha, 0)

    # 3. Add contour lines for sky gaps
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(blended_image, contours, -1, (50, 255, 255), 1) # Bright yellow contours

    # 4. Add footer with results
    footer_height = 60
    footer = np.zeros((footer_height, blended_image.shape[1], 3), dtype=np.uint8)
    text = f"Canopy Cover: {canopy_cover_percent:.2f}%  |  Estimated LAI: {estimated_lai:.2f}"
    cv2.putText(footer, text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # 5. Combine the blended image and the footer
    final_image = cv2.vconcat([blended_image, footer])
    
    # Save the final visual analysis image
    plot_output_dir = os.path.join(output_image_dir, plot_id)
    os.makedirs(plot_output_dir, exist_ok=True)
    output_image_path = os.path.join(plot_output_dir, f"analysis_{base_filename}")
    cv2.imwrite(output_image_path, final_image)

    csv_writer.writerow([plot_id, base_filename, canopy_cover_percent, estimated_lai, gap_fraction])
    logging.info(f"Canopy analysis complete for {os.path.join(plot_id, base_filename)}")

def run_canopy_analysis(input_dir, output_csv_path, output_image_dir):
    """
    Runs the canopy analysis for all images in a directory, 
    processing subdirectories as separate plots.
    """
    logging.info("Starting canopy analysis with subdirectory processing.")
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    os.makedirs(output_image_dir, exist_ok=True)

    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['plot_id', 'filename', 'canopy_cover_percent', 'estimated_lai', 'gap_fraction'])

        # Check for subdirectories (plots)
        subdirs = [d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))]

        if subdirs:
            for plot_id in sorted(subdirs):
                plot_dir = os.path.join(input_dir, plot_id)
                for filename in sorted(os.listdir(plot_dir)):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(plot_dir, filename)
                        analyze_canopy_image(image_path, plot_id, csv_writer, output_image_dir)
        else:
            # Process files in the root if no subdirectories are found
            for filename in sorted(os.listdir(input_dir)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(input_dir, filename)
                    analyze_canopy_image(image_path, 'default', csv_writer, output_image_dir)

    logging.info(f"Canopy analysis finished. Results saved to {output_csv_path}")

if __name__ == '__main__':
    input_image_dir = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\data\\canopy_input_images'
    output_csv = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\data\\canopy_analysis_results.csv'
    output_img_dir = 'D:\\MIT WPU\\Assignments\\LULC Analysis\\vegetation_analysis_app\\output\\images\\canopy_analysis'
    
    run_canopy_analysis(input_image_dir, output_csv, output_img_dir)