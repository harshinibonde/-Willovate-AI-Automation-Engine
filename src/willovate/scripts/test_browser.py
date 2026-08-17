from pathlib import Path

from playwright.sync_api import sync_playwright


def main():

    crm_path = (
        Path(__file__).resolve().parents[3]
        / "sample_app"
        / "crm.html"
    )

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(crm_path.as_uri())

        page.locator("#customer-name").fill("Pankaj Koche")
        page.locator("#phone-number").fill("9876543210")
        page.locator("#save-customer").click()

        print(
            page.locator("#customer-table-body").inner_text()
        )

        input("Press Enter to close the browser...")

        browser.close()


if __name__ == "__main__":
    main()