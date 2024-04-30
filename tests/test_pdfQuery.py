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

for page in root.findall('.//LTPage'):
    page_num = int(page.get('page_index'))
    pdf_page = pdf_reader.pages[page_num]
    page_height = float(pdf_page.mediabox[3])  # Convert to regular float

    can.setPageSize((pdf_page.mediabox[2], pdf_page.mediabox[3]))

    for elem in page.findall('.//*[@bbox]'):
        bbox = eval(elem.get('bbox'))  # Convert string representation of list to actual list
        x0, y0, x1, y1 = map(float, bbox)
        print(x0, y0, x1, y1 )
        can.rect(x0, y0, x1-x0, y1 - y0, stroke=1, fill=0)
    can.showPage()
    pdf_writer.add_page(pdf_page)

# Save the changes to the new canvas
can.save()
packet.seek(0)
overlay_pdf = PdfReader(packet)

# Now merge pages properly
for page_num in range(len(pdf_reader.pages)):
    original_page = pdf_writer.pages[page_num]  # Access the already added page
    overlay_page = overlay_pdf.pages[page_num]  # Overlay page
    original_page.merge_page(overlay_page)

# Save the final output PDF
with open(output_pdf_path, "wb") as f_out:
    print(f_out)
    pdf_writer.write(f_out)