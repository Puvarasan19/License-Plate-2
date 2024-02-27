# -*- coding: utf-8 -*-
"""ocrtesting

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xqeyCNgG3koo7yAkV1tgiUvbLRwkJo42
"""

# Ultralytics YOLO , GPL-3.0 license

import hydra
import torch
import easyocr
import cv2
from ultralytics.yolov8 import Detector
from ultralytics.yolov8.utils.torch_utils import torch_distributed_zero_first
from ultralytics.yolov8.utils.downloads import download
from ultralytics.yolov8.utils.loggers import WandbLogger, CSVLogger

def getOCR(im, coors):
  x,y,w, h = int(coors[0]), int(coors[1]), int(coors[2]),int(coors[3])
  im = im[y:h,x:w]
  conf = 0.2

  gray = cv2.cvtColor(im , cv2.COLOR_RGB2GRAY)
  results = reader.readtext(gray)
  ocr = ""

  for result in results:
    if len(results) == 1:
      ocr = result[1]
    if len(results) >1 and len(results[1])>6 and results[2]> conf:
      ocr = result[1]

  return str(ocr)

class DetectionPredictor:

  def __init__(self, cfg):
    self.model = Detector(cfg.model, device=cfg.device)  # Use Detector class
    self.args = cfg

  def get_annotator(self, img):
    return Annotator(img, line_width=self.args.line_thickness, example=str(self.model.names))

  def preprocess(self, img):
    img = torch.from_numpy(img).to(self.model.device)
    img = img.half() if self.model.fp16 else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    return img

  def postprocess(self, results, img, orig_img):
    results = self.model.xyxy[0]  # Access results directly

    for i, pred in enumerate(results):
      shape = orig_img[i].shape if self.args.webcam else orig_img.shape
      pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()

    return results

  def write_results(self, idx, results, batch):
    p, im, im0 = batch
    log_string = ""
    if len(im.shape) == 3:
      im = im[None]  # expand for batch dim
    self.seen += 1
    im0 = im0.copy()
    if self.args.webcam:  # batch_size >= 1
      log_string += f'{idx}: '
      frame = self.dataset.count
    else:
      frame = getattr(self.dataset, 'frame', 0)

    self.data_path = p
    # save_path = str(self.save_dir / p.name)  # im.jpg
    self.txt_path = str(self.save_dir / 'labels' / p.stem) + ('' if self.dataset.mode == 'image' else f'_{frame}')
    log_string += '%gx%g ' % im.shape[2:]  # print string
    self.annotator = self.get_annotator(im0)

    # ... (rest of the code remains the same) ...

@hydra.main(version_base=None, config_path=str(DEFAULT_CONFIG.parent), config_name=DEFAULT_CONFIG.name)
def predict(cfg):
  cfg.model = cfg.model or "yolov8n.pt"
  cfg.imgsz = check_imgsz(cfg.imgsz, min_dim=2)  # check image size
  cfg.source = cfg.source if cfg.source is not None else ROOT / "assets"
  predictor = DetectionPredictor(cfg)
  predictor()


if __name__ == "__main__":
  reader = easyocr.Reader(['en'])
  predict()