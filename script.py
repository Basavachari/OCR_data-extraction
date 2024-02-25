#  script to create only table data 
# !pip install ocr-nanonets-wrapper

from nanonets import NANONETSOCR
model = NANONETSOCR()
model.set_token('5964bc42-d39f-11ee-b890-ee231041c3b2')
import os
import json
import csv
import cv2
import numpy as np
import pandas as pd
import re

def get_tables(filename):
  pred_json = model.convert_to_tables(filename)
  # print(json.dumps(pred_json, indent=2))
  tables = []
  for table in pred_json[0]['prediction']:

    values = table['cells']
    cur_df = pd.DataFrame(index=range(1, max(cell['row'] for cell in values) + 1),
                    columns=range(1, max(cell['col'] for cell in values) + 1))
    for cell in values:
        cur_df.at[cell['row'], cell['col']] = cell['text']

    cur = {
        'id' : table['id'],
        'data' : cur_df.values.tolist(),
        'xmin': table['xmin'],
        'ymin': table['ymin'], 
        'xmax': table['xmax'], 
        'ymax': table['ymax']
    }
    tables.append(cur)

  # print(tables)
  return tables
def get_lines(filename):
  pred_json = model.convert_to_prediction(filename)
  print(json.dumps(pred_json, indent=2))
  df = pd.DataFrame(pred_json['results'][0]['page_data'][0]['words'])
  lines = []
  current_line = []
  for i, row in df.iterrows():
    if current_line and ((row['ymax'] - current_line[-1]['ymax']) > 20 or ( row['ymin'] - current_line[-1]['ymin']) > 20):
      lines.append(current_line)
      current_line = []
    current_line.append(row)
  lines.append(current_line)
  print(lines)
  line_list = []
  for line in lines:
    xmin = min(row['xmin'] for row in line)
    
    ymin = min(row['ymin'] for row in line)
    xmax = max(row['xmax'] for row in line)
    ymax = max(row['ymax'] for row in line)
    text = (' '.join(row['text'] for row in line)) # this need to be modified further
    row_dict = {
      'text' : text,
      'xmin' : xmin,
      'xmax' : xmax,
      'ymin' : ymin,
      'ymax' : ymax
    }
    line_list.append(row_dict)
  # print(pd.DataFrame(line_list))
  return line_list
def crop_image(image, xmin, ymin, xmax, ymax):
    cropped_image = image[ymin:ymax, xmin:xmax]
    return cropped_image
def combine_data(text_lines, tables):
    combined_data = []
    
    # Add text lines
    for line in text_lines:
        combined_data.append(line)
    
    # Add tables
    for i, table in enumerate(tables, start=1):
        table['table_id'] = f"table_{i}"
        combined_data.append(table)
    
    # Sort combined data by y-coordinate (top to bottom)
    combined_data.sort(key=lambda item: item.get('ymin', 0))
    
    return combined_data

def process_image(image_path):
    # Read input image
    image = cv2.imread(image_path)

    # Detect tables
    table_boxes = get_tables(image_path)

    # Mask the image where tables exist
    table_mask = np.zeros_like(image[:, :, 0], dtype=np.uint8)
    for table in table_boxes:
        xmin, ymin, xmax, ymax = table['xmin'],table['ymin'],table['xmax'],table['ymax']
        cv2.rectangle(table_mask, (xmin, ymin), (xmax, ymax), (255), thickness=cv2.FILLED)

    # Invert the mask to keep everything except the table regions
    masked_image = cv2.bitwise_and(image, image, mask=cv2.bitwise_not(table_mask))
    # Save the modified image
    directory, original_filename = os.path.split(image_path)
    
    modified_image_path =  os.path.join(directory, "modified_" + image_path)

    modified_image_path = "modified_" + original_filename
    cv2.imwrite(modified_image_path, masked_image)
    
    # Detect lines on the masked image
    text_lines = get_lines(modified_image_path)
    # print(text_lines)
    # Combine data
    combined_data = combine_data(text_lines, table_boxes )
  

    return combined_data

# input_image_path = "./sample1.png"
# # combined_data = process_image(input_image_path)
# # print(combined_data)

# text_lines = get_lines('./sample2.jpg')
# print(text_lines)

