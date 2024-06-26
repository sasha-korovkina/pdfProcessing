import fitz
from PIL import Image
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
output_image_file = "/mnt/c/Users/sasha/projects/pdfTest/sampleScannedPDFI.png"

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
text_blocks = lp.Layout([b for b in layout if b.type=='Text'])
figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])
text_blocks = lp.Layout([b for b in text_blocks \
                   if not any(b.is_in(b_fig) for b_fig in figure_blocks)])


img_with_boxes = lp.draw_box(image, layout, box_width=3)
output_path = '/mnt/c/Users/sasha/projects/pdfTest/TableBank50.pdf'
img_with_boxes.save(output_path)
print("Image with layout saved at:", output_path)

