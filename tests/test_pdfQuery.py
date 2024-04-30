from pdfquery import PDFQuery
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
import io
import xml.etree.ElementTree as ET

file_path = r"C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf"
output_pdf_path = r"C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf"

pdf = PDFQuery(file_path)
pdf.load()

pdf.tree.write(r"C:\Users\sasha\projects\pdfTest\output\outXML.xml", pretty_print=True)

tree = ET.parse(r"C:\Users\sasha\projects\pdfTest\output\outXML.xml")
root = tree.getroot()

pdf_reader = PdfReader(r"C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf")
pdf_writer = PdfWriter()

packet = io.BytesIO()
can = canvas.Canvas(packet)

def annotate_pdf_with_text(xml_path, input_pdf_path, output_pdf_path):
    # Load the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Load the PDF
    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    # Iterate over pages in the XML
    for page in root.findall('.//LTPage'):
        page_num = int(page.get('page_index'))
        pdf_page = pdf_reader.pages[page_num]
        page_height = float(pdf_page.mediabox[3])  # The top edge of the PDF page

        # Create a canvas to draw on
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(pdf_page.mediabox[2], page_height))
        can.setPageSize((pdf_page.mediabox[2], page_height))

        # Draw rectangles and text
        for elem in page.findall('.//*[@bbox]'):
            bbox = eval(elem.get('bbox'))  # Convert string representation to actual list
            x0, y0, x1, y1 = map(float, bbox)

            # Adjust y-coordinates
            adjusted_y0 = page_height - y1
            adjusted_y1 = page_height - y0

            # Draw the rectangle
            can.rect(x0, y0, x1 - x0, y1 - y0, stroke=1, fill=0)

            # Retrieve and draw the text if available
            text = elem.text.strip() if elem.text else ""
            text_x = x0
            text_y = y0 # Center text vertically in the rectangle
            can.drawString(text_x, text_y, text)
            print(text_x, text_y, text)

        # Finalize the canvas and add it to the PDF
        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]
        pdf_writer.add_page(new_page)

    # Save the modified PDF
    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

# Usage
annotate_pdf_with_text(r'C:\Users\sasha\projects\pdfTest\output\outXML.xml', r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf', r'C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf')