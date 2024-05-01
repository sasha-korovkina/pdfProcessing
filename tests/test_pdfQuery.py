from pdfquery import PDFQuery
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
import io
import xml.etree.ElementTree as ET
import pandas as pd
from reportlab.lib.colors import pink, blue

pd.set_option('display.max_columns', None)

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
    results_isin = []
    results_pos = []
    results_date = []
    results_owner = []
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
            text_x = x0
            text_y = y0
            #can.drawString(text_x, text_y, text)

            if text:
                all_text.append([text_x, text_y, x1, y1, text])

        for elem in page.findall('.//LTRect[@bbox]'):
            bbox = eval(elem.get('bbox'))
            x0, y0, x1, y1 = map(float, bbox)

            can.setStrokeColor(blue)
            can.setLineWidth(1)
            can.line(x0, y0, x1, y1)

        for elem in page.findall('.//LTLine[@bbox]'):  # Adjust this XPath if necessary
            bbox = eval(elem.get('bbox'))  # Safely parse 'bbox' attribute to get coordinates
            x0, y0, x1, y1 = map(float, bbox)  # Convert all coordinates to floats
            print(f'Coordinates of the underline: {x0, y0, x1, y1}')

            # Set the color for drawing to pink
            can.setStrokeColor(pink)
            can.setLineWidth(1)  # Set line width, adjust as needed
            # Draw a line for LTLine elements
            can.line(x0, y0, x1, y1)  # Draw a line from start to end point

        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]
        pdf_writer.add_page(new_page)

    print(all_text)

    for record in all_text:
        if record[4] == 'End':
            if results_bene or results_pos:  # Check if there are any records to process
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

                # Merge the DataFrames based on the y1 coordinate
                merged_df = pd.merge(df_bene, df_pos, on='y1', how='inner')
                merged_df = merged_df[merged_df['text_pos'] != 'Holding']

                # Print the merged DataFrame
                if not merged_df.empty:
                    print(results_bene)
                    merged_df['ISIN'] = results_isin[0][4]
                    merged_df['Holding Date'] = results_date[0]
                    print(merged_df[['Holding Date', 'ISIN', 'text_pos', 'text_bene']])

            results_bene = []  # Reset the beneficiary results list
            results_pos = []  # Reset the position results list
            results_isin = []
            results_date = []
            results_owner = []
            continue  # Skip to the next iteration of the loop

        if 17 < record[0] < 18:
            results_bene.append(record)
        if 402 < record[2] < 404:
            results_pos.append(record)
        if 95 < record[0] < 96 and 625 < record[1] < 626 and 156 < record[2] < 157 and 634 < record[3] < 635:
            results_isin.append(record)
        if 17 < record[0] < 18 and 685 < record[1] < 686 and 123 < record[2] < 124 and 693 < record[3] < 694:
            clean_date = record[4].replace('Holding Date : ', '')
            results_date.append(clean_date)

    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)


process_pdf_file(r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf')
annotate_pdf_with_text(r'C:\Users\sasha\projects\pdfTest\output\outXML.xml', r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf', r'C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf')