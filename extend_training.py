"""Extended YOLOv8 training: 70 more epochs from best.pt checkpoint."""
from ultralytics import YOLO
import os

os.chdir(r"c:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code")

model = YOLO("outputs/yolov8_runs/train/weights/best.pt")
print("Starting extended training (70 epochs from best checkpoint)...")
model.train(
    data=r"yolo_dataset\data.yaml",
    epochs=70,
    imgsz=640,
    batch=8,
    project="outputs/yolov8_extended",
    name="train",
    device=0,
    exist_ok=True,
    lr0=0.001,
    lrf=0.01,
    warmup_epochs=2,
    mosaic=1.0,
    close_mosaic=10,
    patience=20,      # Early stop if no improvement for 20 epochs
)
print("Extended training complete!")
