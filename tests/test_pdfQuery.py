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

def dataframe_text(all_text, flat_list, results_bene, results_pos, results_isin, results_date, results_owner):
    curr_record = None
    for record in all_text:
        if record in flat_list:
            results_owner.append(record)

        if record[4] == 'End':
            if results_bene or results_pos:  # Check if there are any records to process
                df_bene = pd.DataFrame(results_bene, columns=['x0', 'y0', 'x1', 'y1', 'text_bene', 'owner'])
                df_pos = pd.DataFrame(results_pos, columns=['x0', 'y0', 'x1', 'y1', 'text_pos'])

                # Column Rounding
                for df in [df_bene, df_pos]:
                    for col in ['y0', 'y1', 'x0', 'x1']:
                        df[col] = df[col].round().astype(int)

                # Merge the DataFrames based on the y1 coordinate
                merged_df = pd.merge(df_bene, df_pos, on='y1', how='inner')
                merged_df = merged_df[merged_df['text_pos'] != 'Holding']

                # Print the merged DataFrame
                if not merged_df.empty:
                    merged_df['ISIN'] = results_isin[0][4]
                    merged_df['Holding Date'] = results_date[0]
                    print(merged_df[['Holding Date', 'ISIN', 'text_pos', 'text_bene', 'owner']])

            results_bene = []  # Reset the beneficiary results list
            results_pos = []  # Reset the position results list
            results_isin = []
            results_date = []
            results_owners = []
            continue  # Skip to the next iteration of the loop

        if record in results_owner:
            curr_record = record[4]
        if 17 < record[0] < 18:
            modified_record = record + [curr_record]
            results_bene.append(modified_record)
        if 402 < record[2] < 404:
            results_pos.append(record)
        if 95 < record[0] < 96 and 625 < record[1] < 626 and 156 < record[2] < 157 and 634 < record[3] < 635:
            results_isin.append(record)
        if 17 < record[0] < 18 and 685 < record[1] < 686 and 123 < record[2] < 124 and 693 < record[3] < 694:
            clean_date = record[4].replace('Holding Date : ', '')
            results_date.append(clean_date)

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
    underline_text = []

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
            can.drawString(text_x, text_y, text)

            if text:
                all_text.append([text_x, text_y, x1, y1, text])

        for elem in page.findall('.//LTRect[@bbox]'):
            bbox = eval(elem.get('bbox'))
            x0, y0, x1, y1 = map(float, bbox)

            can.setStrokeColor(blue)
            can.setLineWidth(1)
            can.line(x0, y0, x1, y1)

            # coordinate_text = f'({x0:.2f}, {y0:.2f}) - ({x1:.2f}, {y1:.2f})'
            # text_x = (x0 + x1) / 2  # Position the label in the middle of the line horizontally
            # text_y = y0 + 2  # Position the label slightly above the line vertically
            # can.drawString(text_x, text_y, coordinate_text)

            underline_text.append([x0, y0, x1, y1])

        for elem in page.findall('.//LTLine[@bbox]'):  # Adjust this XPath if necessary
            bbox = eval(elem.get('bbox'))  # Safely parse 'bbox' attribute to get coordinates
            x0, y0, x1, y1 = map(float, bbox)  # Convert all coordinates to floats

            can.setStrokeColor(pink)
            can.setLineWidth(1)  # Set line width, adjust as needed
            can.line(x0, y0, x1, y1)  # Draw a line from start to end point

        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        new_page = new_pdf.pages[0]
        pdf_writer.add_page(new_page)

    print('All text is: ' + str(all_text))
    print('Underlined text is: ' + str(underline_text))

    matched_records = []  # Initialize outside to accumulate data over multiple iterations
    collections = []  #

    for record in all_text:
        if record[4] == 'End':
            if matched_records:
                collections.append(matched_records.copy())  # Add the copy of the list to collections
                matched_records.clear()  # Clear the list for the next set of records
        else:
            for row in underline_text:
                if round(row[0]) == round(record[0]) and round(row[2]) == round(record[2]):
                    matched_records.append(record)  # Store matched records

    flat_list = [sublist2 for sublist1 in collections for sublist2 in sublist1]
    print(f'Collections are: {flat_list}')

    dataframe_text(all_text, flat_list, results_bene, results_pos, results_isin, results_date, results_owner)

    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)


process_pdf_file(r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf')
annotate_pdf_with_text(r'C:\Users\sasha\projects\pdfTest\output\outXML.xml', r'C:\Users\sasha\projects\pdfTest\input\Various 20230331 (2).pdf', r'C:\Users\sasha\projects\pdfTest\output\Various 20230331 (2).pdf')