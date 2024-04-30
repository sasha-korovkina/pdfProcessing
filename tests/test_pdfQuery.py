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
    tree = ET.parse(xml_path)
    root = tree.getroot()

    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    for page in root.findall('.//LTPage'):
        page_num = int(page.get('page_index'))
        pdf_page = pdf_reader.pages[page_num]
        page_height = float(pdf_page.mediabox[3])

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(pdf_page.mediabox[2], page_height))
        can.setPageSize((pdf_page.mediabox[2], page_height))

        for elem in page.findall('.//*[@bbox]'):
            bbox = eval(elem.get('bbox'))
            x0, y0, x1, y1 = map(float, bbox)

            can.rect(x0, y0, x1 - x0, y1 - y0, stroke=1, fill=0)

            text = elem.text.strip() if elem.text else ""
            if x0 == 17.65 and text:
                print(f"** Match Found Bene ** Coordinates: ({x0}, {y0}, {x1}, {y1}) - Text: {text}")
            if x0 == 368.15 and text:
                print(f"** Match Found Position ** Coordinates: ({x0}, {y0}, {x1}, {y1}) - Position: {text}")

            text_x = x0
            text_y = y0
            can.drawString(text_x, text_y, text)
            if text:
                print(text_x, text_y, x1, y1, text)
        print("\n" + "=" * 40 + "\n")

        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]
        pdf_writer.add_page(new_page)

    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

annotate_pdf_with_text(r'C:\Users\sasha\projects\pdfTest\output\outXML.xml', r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf', r'C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf')