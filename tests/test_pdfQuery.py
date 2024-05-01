from pdfquery import PDFQuery
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
import io
import xml.etree.ElementTree as ET
import math
import os
import pandas as pd

# C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf
# C:\Users\sasha\projects\pdfTest\input\Sample Current Disclosure Forms.pdf
file_path = r"C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf"
output_pdf_path = r"C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf"

pdf = PDFQuery(file_path)
pdf.load()
pdf.tree.write(r"C:\Users\sasha\projects\pdfTest\output\outXML.xml", pretty_print=True)

packet = io.BytesIO()
can = canvas.Canvas(packet)

def process_pdf_file(pdf_file_path):
    print(f"Processing {pdf_file_path}...")
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        metadata = pdf_reader.metadata

    # Access and print the /Producer parameter from metadata
    producer = metadata.get('/Producer', 'Producer not found')
    print(f"Producer: {producer}\n")


def annotate_pdf_with_text(xml_path, input_pdf_path, output_pdf_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    results_bene = []
    results_pos = []
    all_text = []

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
            #print(text)
            if x0 < 18 and x0 > 17 and text:
                results_bene.append([x0, y0, x1, y1, text])
                #print(f"** Match Found Bene ** Coordinates: ({x0}, {y0}, {x1}, {y1}) - Text: {text}")
            if x1 > 402 and x1 < 404 and text:
                results_pos.append([x0, y0, x1, y1, text])
                #print(f"** Match Found Position ** Coordinates: ({x0}, {y0}, {x1}, {y1}) - Position: {text}")


            #[17.65, 505.303, 184.118, 514.253, 'Aviva Investors UK Fund Services Limited']
            #[373.15, 385.303, 403.007, 394.252, '90,644']
            text_x = x0
            text_y = y0
            can.drawString(text_x, text_y, text)
            # 360.65 493.303 402.947 502.253
            # 368.15 511.303 402.983 520.253

            if text:
                all_text.append([text_x, text_y, x1, y1, text])

        print(all_text)
        filtered_arrays = [array for array in all_text if len(array) >= 5 and array[4] == "ISIN"]
        print(filtered_arrays)
        # print(results_pos)
        # print(results_bene)
        print("\n" + "=" * 40 + "\n")
        df_bene = pd.DataFrame(results_bene, columns=['x0', 'y0', 'x1', 'y1', 'text_bene'])
        df_pos = pd.DataFrame(results_pos, columns=['x0', 'y0', 'x1', 'y1', 'text_pos'])
        df_bene['y0'] = df_bene['y0'].round().astype(int)
        df_bene['y1'] = df_bene['y1'].round().astype(int)
        df_pos['y0'] = df_pos['y0'].round().astype(int)
        df_pos['y1'] = df_pos['y1'].round().astype(int)
        df_bene['x0'] = df_bene['x0'].round().astype(int)
        df_bene['x1'] = df_bene['x1'].round().astype(int)
        df_pos['x0'] = df_pos['x0'].round().astype(int)
        df_pos['x1'] = df_pos['x1'].round().astype(int)

        # print(df_pos.columns)
        # print(df_pos[['x1', 'text_pos']])
        # print(df_bene[['y1', 'text_bene']])

        # Merge the DataFrames based on the y1 coordinate
        merged_df = pd.merge(df_bene, df_pos, on='y1', how='inner')
        merged_df = merged_df[merged_df['text_pos'] != 'Holding']

        # Display the merged DataFrame
        if not merged_df.empty:
            print(merged_df[['text_pos', 'text_bene']])
            results_bene = []
            results_pos = []

        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]
        pdf_writer.add_page(new_page)

        all_text = []

    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)


process_pdf_file(r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf')
annotate_pdf_with_text(r'C:\Users\sasha\projects\pdfTest\output\outXML.xml', r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf', r'C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf')