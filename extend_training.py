"""Extended YOLOv8 training — Phase 2: resume from extended/last.pt

Phase 1 ran 44 epochs from the 30-epoch best.pt (total ~74 effective epochs).
Best result: mAP50=0.632, mAP50-95=0.435 at epoch 38-44.
Phase 1 crashed mid-validation on epoch 45.

Phase 2 resumes from last.pt with a lower LR to push past the plateau.
"""
from multiprocessing import freeze_support
from ultralytics import YOLO
import os

from melodious.seed import set_seed

def main():
    os.chdir(r"c:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code")
    set_seed(42)

    model = YOLO("outputs/yolov8_extended/train/weights/last.pt")
    print("Phase 2: resuming training from extended/last.pt (epoch 44)...")

    model.train(
        data=r"yolo_dataset\data.yaml",
        epochs=100,           # Will resume from epoch 44, running up to 100
        imgsz=640,
        batch=8,
        project="outputs/yolov8_extended",
        name="train",
        device=0,
        exist_ok=True,
        resume=True,          # Resume from where we left off
        patience=25,          # Early stop if no improvement for 25 epochs
        amp=True,             # Mixed precision for speed
        workers=0,            # Avoid multiprocessing issues on Windows
    )
    print("Extended training Phase 2 complete!")

if __name__ == "__main__":
    freeze_support()
    main()
