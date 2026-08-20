from willovate.schemas import RollbackEntry
from willovate.logger import get_logger

logger = get_logger(__name__)


class RollbackManager:
    def __init__(self):
        self._history: list[RollbackEntry] = []

    def record_change(
        self,
        target: str,
        previous_value: str,
        attribute: str = "textContent"
    ):
        entry = RollbackEntry(
            target=target,
            attribute=attribute,
            previous_value=previous_value
        )
        self._history.append(entry)
        logger.info(f"Recorded rollback entry for {target} ({attribute}): '{previous_value}'")

    def has_rollback_history(self) -> bool:
        return len(self._history) > 0

    def get_last_change(self) -> RollbackEntry | None:
        return self._history[-1] if self._history else None

    def rollback_last(self, page) -> dict:
        if not self._history:
            return {
                "success": False,
                "message": "No modification history available to rollback."
            }

        entry = self._history.pop()

        try:
            if entry.attribute == "textContent":
                page.locator(entry.target).evaluate(
                    "(el, val) => el.textContent = val", entry.previous_value
                )
            else:
                page.locator(entry.target).evaluate(
                    "(el, [attr, val]) => el.setAttribute(attr, val)",
                    [entry.attribute, entry.previous_value]
                )

            logger.info(f"Successfully rolled back {entry.target} to '{entry.previous_value}'")
            return {
                "success": True,
                "target": entry.target,
                "restored_value": entry.previous_value,
                "message": f"Rolled back {entry.target} to previous state."
            }

        except Exception as e:
            logger.error(f"Failed to execute rollback on {entry.target}: {e}")
            return {
                "success": False,
                "target": entry.target,
                "error": str(e),
                "message": f"Failed to rollback {entry.target}: {str(e)}"
            }

    def clear_history(self):
        self._history.clear()
