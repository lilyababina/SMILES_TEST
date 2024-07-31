import os
import time
import logging

import numpy as np
import pandas as pd

from PIL import Image
from DECIMER import predict_SMILES
from pdf2image import convert_from_path
from datetime import datetime, timedelta
from decimer_segmentation import segment_chemical_structures_from_file

logging.basicConfig(
  format='%(asctime)s - %(levelname)s - %(message)s',
  datefmt="%d-%b-%y %H:%M:%S",
  level=logging.INFO,
  filename='logs.txt'
)


def remaining_time(start_time):
  end_time = time.time()
  time_spent = end_time - start_time
  formatted_time = str(timedelta(seconds=time_spent))
  return formatted_time


def find_smiles_from_pdf(pdf_path, p_res_images):
  list_files = []

  # detect segments
  segments = segment_chemical_structures_from_file(pdf_path, expand=True, poppler_path=None)
  for i in range(len(segments)):
    image_path = f'{os.path.basename(pdf_path)}_structure_{i}.png'
    image_path = os.path.join(p_res_images, image_path)
    Image.fromarray(segments[i]).save(image_path)
    list_files.append(image_path)

  smiles = []
  # SMILES translation for each segment
  for im in list_files:
    sm = predict_SMILES(im)
    smiles.append(sm)

  pdf_file_base_name = os.path.basename(pdf_path)
  list_patent = [pdf_file_base_name for i in range(len(smiles))]

  return smiles, list_patent


def find_smiles_for_directory(input_dir, p_res_images, output_path):
  list_smiles_all = []
  list_patents_all = []

  patents = os.listdir(input_dir)
  patents_count = len(patents)
  logging.info(
      f'Starting recognition SMILES for folder {input_dir} with {patents_count} patents')

  for i in range(patents_count):
    start_time = time.time()
    path = os.path.join(input_dir, patents[i])
    logging.info(f'Starting recognizing SMILES for file {i+1}/{patents_count}')

    smiles, list_patent = find_smiles_from_pdf(path, p_res_images)
    rem_time = remaining_time(start_time)
    logging.info(
        f'Recognition SMILES for file {i+1}/{patents_count} finished with time: {rem_time}')

    list_smiles_all.extend(smiles)
    list_patents_all.extend(list_patent)

    logging.info(f'Number of remaining patents {patents_count-i-1}')

  df = pd.DataFrame()
  df['SMILES'] = list_smiles_all
  df['Patent Name'] = list_patents_all
  df.to_csv(os.path.join(output_path, 'smiles.csv'), index=False)

  logging.info(f'Recognition SMILES for folder {input_dir} finished')


if __name__ == '__main__':

  output_path = 'output'  # catalog for result csv
  p_res_images = 'res'  # catalog for images with detected segments
  input_dir = 'input'
  os.mkdir(p_res_images)
  os.mkdir(output_path)

  find_smiles_for_directory(input_dir, p_res_images, output_path)
