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
image_file = "/mnt/c/Users/sasha/projects/pdfTest/sampleScannedPDFI.jpg"

# Define the path to save the image
output_image_file = "/mnt/c/Users/sasha/projects/pdfTest/output/sampleScannedPDFI.png"

# Attempt to read the image
image = plt.imread(image_file)

# Check if the image is read successfully
if image is None:
    print("Error: Unable to read the image file. Please check if the file format is supported.")
else:
    plt.imshow(image)
    plt.savefig(output_image_file)
    print("Image saved to:", output_image_file)

image = image[..., ::-1]

# PubLayNet
model = lp.Detectron2LayoutModel('lp://PrimaLayout/mask_rcnn_R_50_FPN_3x/config',
                                 label_map={1:"TextRegion", 2:"ImageRegion", 3:"TableRegion", 4:"MathsRegion", 5:"SeparatorRegion", 6:"OtherRegion"})

layout = model.detect(image)
lp.elements.Layout
font = ImageFont.load_default()
img_with_boxes = lp.draw_box(image, layout, box_width=3, box_alpha = 0.5, show_element_type=True)

output_path = '/mnt/c/Users/sasha/projects/pdfTest/output/PrimaLayoutTest.pdf'
img_with_boxes.save(output_path)
print("Image with layout saved at:", output_path)
