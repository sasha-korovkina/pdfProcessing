import io
from xml.etree import ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import pink
from PyPDF2 import PdfReader, PdfWriter

xml_path = r"C:\Users\sasha\projects\pdfTest\input\testUnderline.xml"
output_pdf_path = r"C:\Users\sasha\projects\pdfTest\output\testUnderlineResult.pdf"

tree = ET.parse(xml_path)
root = tree.getroot()

all_text = []
pdf_writer = PdfWriter()  # Initialize a PdfFileWriter object


for page in root.findall('.//LTPage'):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setPageSize(A4)  # This is redundant as you've already set the pagesize when initializing the canvas

    for elem in page.findall('.//*[@bbox]'):
        bbox = eval(elem.get('bbox'))
        x0, y0, x1, y1 = map(float, bbox)

        can.rect(x0, y0, x1 - x0, y1 - y0, stroke=1, fill=0)
        text = elem.text.strip() if elem.text else ""
        text_x = x0
        text_y = y0
        if text:
            can.drawString(text_x, text_y, text)
            all_text.append([text_x, text_y, x1, y1, text])

    for elem in page.findall('.//LTRect[@bbox]'):
        bbox = eval(elem.get('bbox'))
        x0, y0, x1, y1 = map(float, bbox)

        can.setStrokeColor(pink)
        can.setLineWidth(1)
        can.line(x0, y0, x1, y1)

    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    new_page = new_pdf.pages[0]
    pdf_writer.add_page(new_page)

# Writing to the output PDF file
with open(output_pdf_path, 'wb') as output_pdf:
    pdf_writer.write(output_pdf)

print("PDF generation complete.")