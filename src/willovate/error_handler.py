import logging

logger = logging.getLogger(__name__)


class AutomationErrorHandler:
    def handle(self, error: Exception, step=None, attempt=1):
        error_text = str(error)

        if "Timeout" in error_text or "waiting for locator" in error_text:
            suggestion = "The target element was not found. Recheck the page and try an alternative selector."
        elif "not found" in error_text:
            suggestion = "The requested item was not found. Verify the item name and try again."
        elif "File not found" in error_text:
            suggestion = "The file could not be found. Check the file path and try again."
        elif "Unsupported action" in error_text:
            suggestion = "The workflow contains an unsupported action. Generate a supported action instead."
        else:
            suggestion = "The action failed. Recheck the current page state and retry."

        logger.error(
            "Automation failed | step=%s | attempt=%s | error=%s",
            step,
            attempt,
            error,
        )

        print(f"Automation error: {error_text}")
        print(f"Failed step: {step}")
        print(f"Suggested recovery: {suggestion}")

        return {
            "success": False,
            "step": step,
            "error": error_text,
            "suggestion": suggestion,
            "retry": attempt < 2,
        }