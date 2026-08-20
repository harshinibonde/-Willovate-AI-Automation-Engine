import os
from pathlib import Path
from willovate.schemas import VerificationResult
from willovate.logger import get_logger

logger = get_logger(__name__)


class OCREngine:
    def __init__(self):
        self._ocr_available = None

    def is_available(self) -> bool:
        if self._ocr_available is not None:
            return self._ocr_available

        try:
            import pytesseract
            from PIL import Image
            # Try running pytesseract get_tesseract_version to confirm binary exists
            pytesseract.get_tesseract_version()
            self._ocr_available = True
        except Exception as e:
            logger.warning(f"OCR/Tesseract unavailable: {e}")
            self._ocr_available = False

        return self._ocr_available

    def extract_text(self, image_path: str) -> str:
        if not self.is_available():
            raise RuntimeError(
                "Tesseract OCR is not installed or available on this system."
            )

        import pytesseract
        from PIL import Image

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Screenshot image file not found: {image_path}")

        image = Image.open(path)
        # Convert to grayscale for better OCR accuracy
        image = image.convert("L")
        text = pytesseract.image_to_string(image)
        return text.strip()


class VisualVerifier:
    def __init__(self):
        self.ocr_engine = OCREngine()

    def verify(
        self,
        image_path: str | None,
        expected_text: str | None,
        dom_passed: bool = True,
    ) -> VerificationResult:
        dom_status = "PASS" if dom_passed else "FAIL"

        if not image_path or not expected_text:
            return VerificationResult(
                dom_result=dom_status,
                ocr_result="SKIPPED",
                combined="VERIFIED" if dom_passed else "FAILED",
                details="DOM verification completed. Visual check not requested or missing expected text."
            )

        if not self.ocr_engine.is_available():
            return VerificationResult(
                dom_result=dom_status,
                ocr_result="UNAVAILABLE",
                combined="VERIFIED" if dom_passed else "FAILED",
                details="OCR engine unavailable. Verified using DOM check only."
            )

        try:
            extracted_text = self.ocr_engine.extract_text(image_path)
            # Case-insensitive substring match
            is_found = expected_text.lower() in extracted_text.lower()
            ocr_status = "PASS" if is_found else "FAIL"

            if dom_passed and is_found:
                combined = "VERIFIED"
                details = f"Both DOM and OCR verified expected text: '{expected_text}'"
            elif dom_passed and not is_found:
                combined = "PARTIAL"
                details = f"DOM verified, but OCR did not detect expected text '{expected_text}' in screenshot."
            elif not dom_passed and is_found:
                combined = "PARTIAL"
                details = f"DOM verification failed, but OCR detected expected text '{expected_text}' in screenshot."
            else:
                combined = "FAILED"
                details = f"Both DOM and OCR failed to verify expected text '{expected_text}'."

            return VerificationResult(
                dom_result=dom_status,
                ocr_result=ocr_status,
                combined=combined,
                details=details,
            )

        except Exception as e:
            logger.error(f"Visual verification error: {e}")
            return VerificationResult(
                dom_result=dom_status,
                ocr_result="FAIL",
                combined="PARTIAL" if dom_passed else "FAILED",
                details=f"OCR execution failed with error: {str(e)}",
            )
