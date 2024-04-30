import fitz
from PIL import Image, ImageFont
import io
import numpy as np
import layoutparser as lp
import random
import cv2
import matplotlib.pyplot as plt

# Define the path to the image file
# C:\Users\sasha\projects\pdfTest\CI Games Authorisation Letter 2023.jpg
# C:\Users\sasha\projects\pdfTest\sampleScannedPDFl.jpg
#"C:\Users\sasha\projects\pdfTest\sampleScannedPDFl.jpg"
#
image_file = "/mnt/c/Users/sasha/projects/pdfTest/input/Various 20230331 (2)-1.png"

# Define the path to save the image
output_image_file = "/mnt/c/Users/sasha/projects/pdfTest/output/Various 20230331 (2)-1.png"

# Attempt to read the image
image = cv2.imread(image_file)

# Check if the image is read successfully
if image is None:
    print("Error: Unable to read the image file. Please check if the file format is supported.")
else:
    plt.imshow(image)
    plt.savefig(output_image_file)
    print("Image saved to:", output_image_file)

image = image[..., ::-1]

model = lp.Detectron2LayoutModel('lp://TableBank/faster_rcnn_R_50_FPN_3x/config',
                                 label_map={0: "Table"})

layout = model.detect(image)
lp.elements.Layout
font = ImageFont.load_default()
img_with_boxes = lp.draw_box(image, layout, box_width=3, box_alpha = 0.5, show_element_type=True, id_font_size = 16)

output_path = '/mnt/c/Users/sasha/projects/pdfTest/output/PrimaLayout.pdf'
img_with_boxes.save(output_path)
print("Image with layout saved at:", output_path)
