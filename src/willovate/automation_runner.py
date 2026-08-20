from pathlib import Path
from playwright.sync_api import sync_playwright
from willovate.error_handler import AutomationErrorHandler
from willovate.schemas import Workflow
from willovate.rollback_manager import RollbackManager
from willovate.visual_verifier import VisualVerifier


class AutomationRunner:
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.error_handler = AutomationErrorHandler()
        self.rollback_manager = RollbackManager()
        self.visual_verifier = VisualVerifier()

    def open_page(self, page, target):
        pages = {
            "crm": "/",
            "dashboard": "/",
            "customers": "/customers",
            "customer-form": "/customers/add",
            "products": "/products",
            "reports": "/reports",
            "files": "/files",
            "email": "/email",
            "homepage": "/homepage",
            "offers": "/offers",
        }

        if target in pages:
            url = self.base_url + pages[target]
        elif target.startswith("http"):
            url = target
        else:
            url = self.base_url + "/" + target.strip("/")

        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)

    def wait_for_element(self, page, selector, timeout=10000):
        page.locator(selector).wait_for(
            state="visible",
            timeout=timeout
        )

    def find_product_edit_button(self, page, product_name):
        rows = page.locator("#product-table-body tr")
        count = rows.count()

        for i in range(count):
            row = rows.nth(i)
            if product_name.lower() in row.inner_text().lower():
                button = row.locator("button.action-button.edit")
                if button.count():
                    return button.first

        raise ValueError(
            f"Product '{product_name}' was not found."
        )

    def find_customer_delete_button(self, page, customer_name):
        rows = page.locator("#customer-table-body tr")
        count = rows.count()

        for i in range(count):
            row = rows.nth(i)
            if customer_name.lower() in row.inner_text().lower():
                button = row.locator("button.action-button.delete")
                if button.count():
                    return button.first

        raise ValueError(
            f"Customer '{customer_name}' was not found."
        )

    def resolve_file(self, filename):
        if not filename:
            raise ValueError("No file name provided.")

        path = Path(filename)

        candidates = [
            path,
            Path.cwd() / filename,
            Path.cwd() / "uploads" / filename,
            Path.cwd() / "sample_crm" / "uploads" / filename,
            Path.home() / "Downloads" / filename
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return str(candidate.resolve())

        raise FileNotFoundError(
            f"File not found: {filename}"
        )

    def click(self, page, selector):
        self.wait_for_element(page, selector)
        page.locator(selector).click()

    def enter_text(self, page, selector, value):
        if "hidden" in selector or selector.startswith("#hidden"):
            page.locator(selector).evaluate("(el, val) => el.value = val", str(value or ""))
        else:
            self.wait_for_element(page, selector)
            page.locator(selector).fill(str(value or ""))

    def run(self, workflow: Workflow):
        results = []
        expected_ocr_text = None

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            try:
                for step in workflow.steps:
                    for attempt in range(1, 3):
                        try:
                            action = step.action.value

                            if action == "OPEN_URL":
                                page.goto(
                                    step.target,
                                    wait_until="domcontentloaded"
                                )
                                page.wait_for_timeout(500)

                            elif action == "OPEN_PAGE":
                                self.open_page(page, step.target)

                            elif action == "CLICK":
                                if step.target == "__PRODUCT_EDIT__":
                                    button = self.find_product_edit_button(
                                        page,
                                        step.value
                                    )
                                    button.click()
                                elif step.target == "__CUSTOMER_DELETE__":
                                    button = self.find_customer_delete_button(
                                        page,
                                        step.value
                                    )
                                    button.click()
                                else:
                                    self.click(page, step.target)

                            elif action == "DELETE":
                                if step.target == "__CUSTOMER_DELETE__":
                                    button = self.find_customer_delete_button(
                                        page,
                                        step.value
                                    )
                                    button.click()
                                else:
                                    self.click(page, step.target)

                            elif action == "ENTER_TEXT":
                                self.enter_text(
                                    page,
                                    step.target,
                                    step.value
                                )
                                if step.value:
                                    expected_ocr_text = str(step.value)

                            elif action == "UPDATE_TEXT":
                                self.wait_for_element(page, step.target)
                                try:
                                    current_val = page.locator(step.target).inner_text()
                                    self.rollback_manager.record_change(
                                        target=step.target,
                                        previous_value=current_val,
                                        attribute="textContent"
                                    )
                                except Exception:
                                    pass

                                page.locator(step.target).evaluate(
                                    "(el, val) => el.textContent = val", step.value or ""
                                )
                                if step.value:
                                    expected_ocr_text = str(step.value)

                            elif action == "SET_ATTRIBUTE":
                                self.wait_for_element(page, step.target)
                                attr_name, attr_val = (
                                    step.value.split("=", 1)
                                    if "=" in step.value
                                    else ("src", step.value)
                                )
                                try:
                                    current_val = page.locator(step.target).get_attribute(attr_name) or ""
                                    self.rollback_manager.record_change(
                                        target=step.target,
                                        previous_value=current_val,
                                        attribute=attr_name
                                    )
                                except Exception:
                                    pass

                                page.locator(step.target).evaluate(
                                    "(el, [a, v]) => el.setAttribute(a, v)",
                                    [attr_name, attr_val]
                                )

                            elif action == "APPLY_STYLE":
                                self.wait_for_element(page, step.target)
                                try:
                                    current_val = page.locator(step.target).get_attribute("style") or ""
                                    self.rollback_manager.record_change(
                                        target=step.target,
                                        previous_value=current_val,
                                        attribute="style"
                                    )
                                except Exception:
                                    pass

                                page.locator(step.target).evaluate(
                                    "(el, val) => el.style.cssText = val",
                                    step.value or ""
                                )

                            elif action == "SELECT_OPTION":
                                self.wait_for_element(
                                    page,
                                    step.target
                                )
                                page.locator(
                                    step.target
                                ).select_option(step.value)

                            elif action == "UPLOAD_FILE":
                                file_path = self.resolve_file(step.value)
                                page.locator(
                                    step.target
                                ).set_input_files(file_path)

                            elif action == "DOWNLOAD_FILE":
                                self.wait_for_element(
                                    page,
                                    step.target
                                )

                                with page.expect_download() as download_info:
                                    page.locator(
                                        step.target
                                    ).click()

                                download = download_info.value
                                path = download.path()

                                results.append({
                                    "filename": download.suggested_filename,
                                    "path": str(path)
                                })

                                print(
                                    f"Downloaded: "
                                    f"{download.suggested_filename}"
                                )

                            elif action == "READ_TEXT":
                                self.wait_for_element(
                                    page,
                                    step.target
                                )
                                text_val = page.locator(step.target).inner_text()
                                results.append(text_val)

                            elif action == "READ_TABLE":
                                self.wait_for_element(
                                    page,
                                    step.target
                                )
                                table_val = page.locator(step.target).inner_text()
                                results.append(table_val)

                            elif action == "SCROLL":
                                if step.target:
                                    page.locator(
                                        step.target
                                    ).scroll_into_view_if_needed()
                                else:
                                    page.mouse.wheel(0, 700)

                            elif action == "WAIT":
                                page.wait_for_timeout(
                                    int(step.value or 1000)
                                )

                            elif action == "TAKE_SCREENSHOT":
                                screenshot_path = step.value or "screenshot.png"
                                page.screenshot(path=screenshot_path)
                                print(f"Screenshot saved: {screenshot_path}")

                                # Trigger OCR verification
                                verif_res = self.visual_verifier.verify(
                                    image_path=screenshot_path,
                                    expected_text=expected_ocr_text,
                                    dom_passed=True
                                )
                                results.append({
                                    "type": "verification_result",
                                    "result": verif_res.model_dump()
                                })

                            elif action == "SUBMIT":
                                self.click(page, step.target)

                            else:
                                raise ValueError(
                                    f"Unsupported action: {action}"
                                )

                            break

                        except Exception as error:
                            result = self.error_handler.handle(
                                error,
                                step=step,
                                attempt=attempt
                            )

                            if not result["retry"]:
                                results.append({
                                    "success": False,
                                    "step": str(step),
                                    "error": result["error"],
                                    "suggestion": result["suggestion"],
                                })
                                print("Automation stopped safely after retry attempts.")
                                break

            finally:
                print("\nBrowser automation completed.")
                try:
                    import sys
                    if sys.stdin and sys.stdin.isatty():
                        input("Press Enter to close the browser...")
                except (EOFError, KeyboardInterrupt):
                    pass
                browser.close()

        return results
