import fitz
from PIL import Image
import io
import numpy as np
import layoutparser as lp
import random
import cv2

# Define the path to the image file
image_file = "/mnt/c/Users/sasha/projects/business.jpg"

# Attempt to read the image
image = cv2.imread(image_file)

# Check if the image is read successfully
if image is None:
    print("Error: Unable to read the image file. Please check if the file format is supported.")
    exit()

print('Image successfully read.')

# Reverse the color channels to convert BGR to RGB
image = image[..., ::-1]

model = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                                 extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                                 label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})

layout = model.detect(image)
lp.draw_box(image, layout, box_width=3)

# model = lp.Detectron2LayoutModel('lp://HJDataset/faster_rcnn_R_50_FPN_3x/config')

# images = convert_pdf_to_pil_images(pdf_no_img)
#
# image_arrays = [np.array(image) for image in images]
# image_array = np.array(image_arrays)
# image_array = image_array.astype(np.uint8)
# print(image_array.shape)
#
# for i, img in enumerate(image_array):
#     layout = model.detect(img)
#     img_with_boxes = lp.draw_box(img, layout, box_width=3)
#
#     # Save the modified image with layout boxes
#     output_path = '/mnt/c/Users/sasha/projects/pdfTest/theFile.pdf'
#
#     # Convert numpy array to PIL image
#     output_image = Image.fromarray(img_with_boxes)
#
#     # Save the image
#     output_image.save(output_path)
#
#     print("Image with layout saved at:", output_path)
#
# print('All images processed and saved with layout boxes.')