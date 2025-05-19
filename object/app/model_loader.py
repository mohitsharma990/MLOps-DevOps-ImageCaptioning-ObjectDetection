import logging
from io import BytesIO
from PIL import Image
import torch # Still potentially useful for device selection
import numpy as np
import cv2 # Import opencv

# Import YOLO from ultralytics
from ultralytics import YOLO
import os # Import os module

MODEL_PATH_ON_VOLUME = "/model-cache/yolo/yolo11m.pt"

logger = logging.getLogger(__name__)

# --- Configuration ---
# Choose a YOLOv8 model checkpoint (e.g., yolov8n.pt, yolov8s.pt, yolov8m.pt)
# 'n' is nano (fastest, lowest accuracy), 's' is small, 'm' is medium etc.
MODEL_NAME = "yolo11m.pt" # Using the nano version as a starting point
DEVICE = "cuda" if torch.cuda.is_available() else "cpu" # ultralytics can often auto-detect, but good to specify
CONFIDENCE_THRESHOLD = 0.40 # Adjust confidence threshold as needed for YOLOv8

# --- Global Variables ---
model = None # Initialize model to None or a placeholder
# image_processor is no longer needed from transformers

# --- Initialization ---
def load_model():
    """Loads the pre-trained YOLOv8 model."""
    global model
    if model:
        logger.info("YOLOv8 model already loaded.")
        return
    try:
        logger.info(f"Loading YOLOv11 model '{MODEL_NAME}' onto device '{DEVICE}'...")
        # Initialize YOLO model
        if not os.path.exists(MODEL_PATH_ON_VOLUME):
               raise RuntimeError(f"Model file not found at {MODEL_PATH_ON_VOLUME}. Init container might have failed.")
        model = YOLO(MODEL_PATH_ON_VOLUME)
        # You can explicitly move the model to a device if needed,
        # but YOLO often handles device placement automatically during predict.
        # model.to(DEVICE) # Usually not required unless specific device needed upfront
        logger.info(f"YOLOv11 model '{MODEL_NAME}' loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading YOLOv11 model: {e}", exc_info=True)
        model = None # Reset on failure
        raise RuntimeError(f"Failed to load ML model: {e}")

# --- Inference ---
def detect_objects(image_bytes: bytes) -> list:
    """Detects objects in the given image bytes using YOLOv8."""
    global model

    if not model:
        raise RuntimeError("YOLOv11 model is not loaded.")

    detections = []
    try:
        logger.debug("Opening image from bytes for YOLOv8 detection.")
        # Read image bytes into a PIL Image
        pil_image = Image.open(BytesIO(image_bytes))
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Convert PIL Image to NumPy array (OpenCV format - BGR)
        # Ultralytics predict can often handle PIL directly, but NumPy is robust
        img_np = np.array(pil_image)
        # No need to convert RGB -> BGR, ultralytics handles it
        # img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR) # Not needed for ultralytics>=8

        logger.debug("Performing YOLOv11 object detection inference...")

        # Perform prediction
        # Pass image directly, specify confidence, device, and disable verbose logs
        results = model.predict(source=img_np,
                                conf=CONFIDENCE_THRESHOLD,
                                device=DEVICE,
                                verbose=False) # Set verbose=True for debugging if needed

        # Check if results is a list and has items
        if not results or len(results) == 0:
             logger.info("YOLOv11 prediction returned no results.")
             return []

        # Process results - results is a list, usually with one element for single image
        result = results[0] # Get the results for the first (and only) image
        boxes = result.boxes # Access the Boxes object containing detections
        logger.info(f"Raw YOLOv11 prediction results: {len(boxes)} potential boxes found before filtering.")
        if len(boxes) > 0:
            raw_scores = boxes.conf.cpu().numpy().tolist()
            logger.info(f"Raw Scores (before threshold): {raw_scores}")
        # Extract data
        box_coords_tensor = boxes.xyxy # Bounding boxes in xyxy format (Tensor)
        scores_tensor = boxes.conf     # Confidence scores (Tensor)
        class_ids_tensor = boxes.cls   # Class IDs (Tensor)
        class_names = result.names     # Dictionary mapping class IDs to names

        # Convert tensors to lists
        box_coords_list = box_coords_tensor.cpu().numpy().tolist()
        scores_list = scores_tensor.cpu().numpy().tolist()
        class_ids_list = class_ids_tensor.cpu().numpy().astype(int).tolist()

        logger.debug(f"Raw detections: {len(box_coords_list)}")

        # Format results
        for box, score, class_id in zip(box_coords_list, scores_list, class_ids_list):
             # Check confidence again (though predict should have filtered)
             if score >= CONFIDENCE_THRESHOLD:
                 label = class_names.get(class_id, f"Unknown class {class_id}")
                 # Ensure box coordinates are integers
                 box_int = [round(coord) for coord in box]
                 detections.append({
                     "label": label,
                     "score": round(score, 4),
                     "box": box_int # [xmin, ymin, xmax, ymax]
                 })
                 logger.debug(f"Detected: {label} (Score: {score:.4f}) at Box: {box_int}")

        logger.info(f"YOLOv8 detection complete. Found {len(detections)} objects above threshold {CONFIDENCE_THRESHOLD}.")
        return detections

    except Exception as e:
        logger.error(f"Error during YOLOv8 object detection: {e}", exc_info=True)
        # Re-raise as a ValueError to be caught in the endpoint
        raise ValueError(f"Object detection failed: {e}")