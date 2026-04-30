🎨 CMYK Conversion and Ink Optimization

This project implements a complete pipeline for converting digital images from RGB (BGR in OpenCV) to CMYK color space, optimizing ink usage for printing, and analyzing perceptual quality loss.

📌 Overview

Digital images are typically represented in RGB, while printers operate in CMYK. A direct conversion can lead to: Excessive ink usage (up to 400% coverage) Printing issues (smudging, slow drying) Color inaccuracies

This project addresses these challenges by: Performing pixel-wise RGB → CMYK conversion Estimating and limiting total ink coverage Reconstructing the image back to RGB Evaluating perceptual differences using Delta-E

📁 Project Structure

The project uses absolute paths to ensure the code works regardless of the execution directory.

Assignment_1/
├── Doxyfile                # Documentation configuration
├── (Doxygen-generated files)
├── Src/
│   └── main.py             # Core implementation
└── Pics/                   # Auto-generated output directory
    ├── cyan_gs.png
    ├── ...
    ├── diff_image.png              # Difference between original & reconstructed
    ├── est_ink_consumption.png     # Delta-E heatmap
    ├── input.png                   # Input image (RGB)
    └── reconst_img.png             # Reconstructed (CMYK → RGB)

⚙️ Dependencies

Install the required Python libraries:

pip install numpy opencv-python matplotlib colour-science scipy

▶️ Execution

Run the script from anywhere inside the project:

python3 Src/main.py

🖥️ Platform Compatibility

Primary OS: Linux (Ubuntu/Debian) Display Support: Wayland / X11

The script suppresses Qt/Wayland font warnings to keep terminal output clean.

Although developed on Linux, the use of os.path and standard Python libraries makes it compatible with Windows and macOS.

📊 Output

The program generates:

CMYK channel visualizations Ink consumption estimates Reconstructed RGB image Difference image Delta-E heatmap

All outputs are saved automatically in the Pics/ directory.

🧠 Notes OpenCV uses BGR format, which is handled internally. Ink optimization ensures print-safe total coverage. Delta-E is used for perceptual accuracy evaluation.
