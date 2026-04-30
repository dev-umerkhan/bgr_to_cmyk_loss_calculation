"""
@file main.py
@brief CMYK color space processing and analysis

@author
    Muhammad Umer Khan  
    Muhammad Abdullah Raja  

@date 24.04.2025

@details
- Converts BGR to CMYK
- Displays CMYK components
- Estimates ink consumption
- Limits ink usage
- Converts back to BGR
- Performs Delta-E analysis

@references
[1] Sharma et al., "CIEDE2000", 2005  
[2] Adobe PostScript Language Reference, 3rd Ed.
"""

import cv2 as cv
import numpy as np
import sys
import colour
import os


MAX_INK_CONSUMTION_VALUE = 250

def bgr_to_cmyk(input_image):
    """
    Convert a BGR image to the CMYK color space.

    @param input_image numpy.ndarray (H, W, 3)
        Input image in BGR format with values in range [0, 255].

    @return numpy.ndarray (H, W, 4)
        Output image in CMYK format with values in range [0, 1].

    @note Uses an epsilon guard when K ≈ 1 to prevent division by zero.

    @see Adobe Systems, "PostScript Language Reference", 3rd Ed.,
         Section 7.2 for CMYK color space conversions.
    """
    
    # Normalizing bgr components since cmyk requires values between 0-1
    blue_norm, green_norm, red_norm = cv.split(input_image.astype(np.float32)/255)

    black = 1 - np.maximum(np.maximum(blue_norm, green_norm), red_norm)

    cyan = np.zeros_like(black)
    magenta = np.zeros_like(black)
    yellow = np.zeros_like(black)

    # Calculation of CMYK matrices
    for i in range(black.shape[0]):
        for j in range(black.shape[1]):

            epsilon = 1e-7
            if black[i][j] >= 1 - epsilon:             # If black component value is one or closer it results in undefined/ very large value for other components
                cyan[i][j] = 0
                magenta[i][j] = 0
                yellow[i][j] = 0

            else:
                cyan[i][j] = (1 - red_norm[i][j] - black[i][j])/(1 - black[i][j])
                magenta[i][j] = (1 - green_norm[i][j] - black[i][j])/(1 - black[i][j])
                yellow[i][j] = (1 - blue_norm[i][j] - black[i][j])/(1 - black[i][j])

    return cv.merge([cyan, magenta, yellow, black])



def disp_save_cmyk_comp(cmyk_img):
    """
    Display and save CMYK components as grayscale images.

    @param cmyk_img numpy.ndarray (H, W, 4)
        Image in CMYK format with values in range [0, 1].
    """

    cyan_comp_image     = (cmyk_img[ :, :, 0]*255).astype(np.uint8)
    magenta_comp_image  = (cmyk_img[ :, :, 1]*255).astype(np.uint8)
    yellow_comp_image   = (cmyk_img[ :, :, 2]*255).astype(np.uint8)
    black_comp_image    = (cmyk_img[ :, :, 3]*255).astype(np.uint8)

    cv.imshow("Cyan Grayscale", cyan_comp_image)
    cv.waitKey(0)
    cv.imwrite(os.path.join(PICS_DIR, "cyan_gs.png"),cyan_comp_image)
    cv.destroyWindow("Cyan Grayscale")

    cv.imshow("Magenta Grayscale", magenta_comp_image)
    cv.waitKey(0)
    cv.imwrite(os.path.join(PICS_DIR, "magenta_gs.png"),magenta_comp_image)
    cv.destroyWindow("Magenta Grayscale")


    cv.imshow("Yellow Grayscale", yellow_comp_image)
    cv.waitKey(0)
    cv.imwrite(os.path.join(PICS_DIR, "yellow_gs.png"),yellow_comp_image)
    cv.destroyWindow("Yellow Grayscale")


    cv.imshow("Black Grayscale", black_comp_image)
    cv.waitKey(0)
    cv.imwrite(os.path.join(PICS_DIR, "black_gs.png"),black_comp_image)
    cv.destroyWindow("Black Grayscale")



def est_ink_consumption(cmyk_image):
    """
    Estimate ink consumption per pixel for a CMYK image.

    @param cmyk_image numpy.ndarray (H, W, 4)
        Image in CMYK format.

    @return numpy.ndarray (H, W)
        Matrix representing total ink consumption per pixel.
    """
    consumption_matrix = np.sum(cmyk_image, axis=2)

    heatmap_gray = ((consumption_matrix / 4.0)* 255).astype(np.uint8)
    heatmap_color = cv.applyColorMap(heatmap_gray, cv.COLORMAP_JET)

    cv.imshow("Consumption Matrix", heatmap_color)
    cv.waitKey(0)
    cv.destroyWindow("Consumption Matrix")

    cv.imwrite(os.path.join(PICS_DIR, "est_ink_consumption.png"),heatmap_color)
    return consumption_matrix



def limit_ink_consumption(consumption_matrix, cmyk_image):
    """
    Limit ink consumption per pixel to a maximum threshold.

    @param consumption_matrix numpy.ndarray (H, W)
        Ink consumption per pixel.

    @param cmyk_image numpy.ndarray (H, W, 4)
        CMYK image to be modified in-place.

    @note The maximum ink limit is defined by MAX_INK_CONSUMPTION_VALUE.
    """
    # Calculate the factor by which each channel needs to be reduced to go below threshold
    for i in range(consumption_matrix.shape[0]):
         for j in range(consumption_matrix.shape[1]):

            if consumption_matrix[i][j]*100 < MAX_INK_CONSUMTION_VALUE:
                continue

            factor = MAX_INK_CONSUMTION_VALUE/(consumption_matrix[i][j]*100)
            cyan = cmyk_image[i][j][0]*factor
            magenta = cmyk_image[i][j][1]*factor
            yellow = cmyk_image[i][j][2]*factor
            black = cmyk_image[i][j][3]*factor

            cmyk_image[i][j] = [cyan, magenta, yellow, black]



def cmyk_to_bgr(cmyk_image):
    """
    Convert a CMYK image back to BGR color space.

    @param cmyk_image numpy.ndarray (H, W, 4)
        Image in CMYK format.

    @return numpy.ndarray (H, W, 3)
        Output image in BGR format with values in range [0, 255].
    """
    cyan, magenta, yellow, black = cv.split(cmyk_image)

    red = (1 - cyan)*(1 - black)*255
    green = (1 - magenta)*(1- black)*255
    blue = (1 - yellow)*(1 - black)*255

    return cv.merge([blue, green, red]).clip(0,255).astype(np.uint8)


def calc_delta_E(original_image, converted_image):
    """
    Compute Delta-E (CIEDE2000) between original and converted images.

    @param original_image numpy.ndarray (H, W, 3)
        Original image in BGR format.

    @param converted_image numpy.ndarray (H, W, 3)
        Reconstructed image in BGR format.

    @return numpy.ndarray (H, W)
        Matrix of Delta-E values per pixel.

    @cite ISO/CIE 11664-6:2014 standard for colorimetry.

    @see Sharma et al. (2005) for details on CIEDE2000.
    """

    # Convert images to CIELAB format for delta-E analysis
    orig_image_lab = cv.cvtColor(original_image.astype(np.float32)/255, cv.COLOR_BGR2LAB)
    conv_image_lab = cv.cvtColor(converted_image.astype(np.float32)/255, cv.COLOR_BGR2LAB)

    delta_e_matrix = colour.delta_E(orig_image_lab, conv_image_lab, method='CIE2000')

    return delta_e_matrix



# -----------------------------------------------------------------Main Logic-----------------------------------------------------------------------------------#


# 1. Get the absolute path of the directory where THIS script is saved
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Define your output directory relative to the script location
# This ensures it always finds "Pics" inside your project folder
PICS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "pics")

# Source: https://www.digitalphotomentor.com/photography/2016/09/processing-sins-over-saturation-750px-09.jpg
input_image = cv.imread(os.path.join(PICS_DIR, "input.png"))
if input_image is None:
    sys.exit("Could not find image")

cmyk_image = np.zeros( (input_image.shape[0], input_image.shape[1], 4), dtype=np.float32)
ink_consumption_matrix = np.zeros( (input_image.shape[0], input_image.shape[1]), dtype=np.float32)
bgr_image = np.zeros( (input_image.shape[0], input_image.shape[1], 3), dtype=np.uint8)
delta_e_matrix = np.zeros((input_image.shape[0], input_image.shape[1]), dtype=np.float32)

# Convert BGR to CMYK pixel-wise
cmyk_image = bgr_to_cmyk(input_image)

# Display and save the 4 components as grayscale images
disp_save_cmyk_comp(cmyk_image)

ink_consumption_matrix = est_ink_consumption(cmyk_image)

limit_ink_consumption(ink_consumption_matrix, cmyk_image)

bgr_image = cmyk_to_bgr(cmyk_image)
cv.imwrite(os.path.join(PICS_DIR, "reconst_img.png"),bgr_image)

diff_raw = cv.absdiff(input_image, bgr_image).astype(np.float32)
diff_image = np.clip(diff_raw * 50, 0, 255).astype(np.uint8)

cv.imshow("Difference Image", diff_image)
cv.waitKey(0)
cv.imwrite(os.path.join(PICS_DIR, "diff_image.png"),diff_image)


delta_e_matrix = calc_delta_E(input_image, bgr_image)

os.system('clear')

print("\n" + "="*40)
print(" CMYK TRANSFORMATION QUALITY ANALYSIS")
print("="*40)
print(f"Mean Delta-E (CIE 2000) :  {np.mean(delta_e_matrix):.4f}")
print(f"Max Delta-E (Worst Case):  {np.max(delta_e_matrix):.4f}")
print("-"*40)

# Interpretation logic for the delta-E
if np.mean(delta_e_matrix) < 1.0:
    print("Conclusion: Perceptually Lossless Reconstruction.")
else:
    print("Conclusion: Noticeable Perceptual Shifts Detected.")
print("="*40 + "\n")

cv.destroyAllWindows()