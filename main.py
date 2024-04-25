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
image_file = "/mnt/c/Users/sasha/projects/pdfTest/CI Games Authorisation Letter 2023.jpg"

# Define the path to save the image
output_image_file = "/mnt/c/Users/sasha/projects/pdfTest/CI Games Authorisation Letter 2023 - out.png"

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

model = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                                 extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                                 label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})

layout = model.detect(image)
img_with_boxes = lp.draw_box(image, layout, box_width=3)
output_path = '/mnt/c/Users/sasha/projects/pdfTest/theFile.pdf'
img_with_boxes.save(output_path)
print("Image with layout saved at:", output_path)

