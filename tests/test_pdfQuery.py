from pdfquery import PDFQuery
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
import io
import xml.etree.ElementTree as ET
import math

file_path = r"C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf"
output_pdf_path = r"C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf"

pdf = PDFQuery(file_path)
pdf.load()
pdf.tree.write(r"C:\Users\sasha\projects\pdfTest\output\outXML.xml", pretty_print=True)

packet = io.BytesIO()
can = canvas.Canvas(packet)

def annotate_pdf_with_text(xml_path, input_pdf_path, output_pdf_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    results_bene = []
    results_pos = []

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
                results_bene.append([x0, y0, x1, y1, text])
                print(f"** Match Found Bene ** Coordinates: ({x0}, {y0}, {x1}, {y1}) - Text: {text}")
            if round(x1 * 10) / 10 == 403 and text:
                results_pos.append([x0, y0, x1, y1, text])
                print(f"** Match Found Position ** Coordinates: ({x0}, {y0}, {x1}, {y1}) - Position: {text}")


            #[17.65, 505.303, 184.118, 514.253, 'Aviva Investors UK Fund Services Limited']
            #[373.15, 385.303, 403.007, 394.252, '90,644']
            text_x = x0
            text_y = y0
            can.drawString(text_x, text_y, text)
        #     print(text_x, text_y, x1, y1, text)

        print(results_pos)
        print(results_bene)
        print("\n" + "=" * 40 + "\n")
        results_bene = []
        results_pos = []

        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]
        pdf_writer.add_page(new_page)

    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

annotate_pdf_with_text(r'C:\Users\sasha\projects\pdfTest\output\outXML.xml', r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf', r'C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf')