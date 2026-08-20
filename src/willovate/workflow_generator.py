from willovate.banner_theme import BannerThemeManager
from willovate.schemas import IntentDetectionResponse, Workflow


class WorkflowGenerator:
    def generate(self, result: IntentDetectionResponse) -> Workflow:
        intent = result.intent.value
        entities = result.entities or {}

        if intent == "ADD_CUSTOMER":
            return Workflow.model_validate({
                "steps": [
                    {
                        "action": "OPEN_PAGE",
                        "target": "customers",
                        "value": None
                    },
                    {
                        "action": "CLICK",
                        "target": "#add-customer-btn",
                        "value": None
                    },
                    {
                        "action": "ENTER_TEXT",
                        "target": "#customer-name",
                        "value": entities.get("customer_name")
                    },
                    {
                        "action": "ENTER_TEXT",
                        "target": "#phone-number",
                        "value": entities.get("phone_number")
                    },
                    {
                        "action": "SUBMIT",
                        "target": "#save-customer",
                        "value": None
                    },
                    {
                        "action": "OPEN_PAGE",
                        "target": "customers",
                        "value": None
                    },
                    {
                        "action": "READ_TABLE",
                        "target": "#customer-table-body",
                        "value": None
                    }
                ]
            })

        if intent == "ADD_PRODUCT":
            steps = [
                {
                    "action": "OPEN_PAGE",
                    "target": "products",
                    "value": None
                },
                {
                    "action": "ENTER_TEXT",
                    "target": "#product-name",
                    "value": entities.get("product_name")
                },
                {
                    "action": "SELECT_OPTION",
                    "target": "#product-category",
                    "value": entities.get("category")
                },
                {
                    "action": "ENTER_TEXT",
                    "target": "#product-price",
                    "value": entities.get("price")
                },
                {
                    "action": "ENTER_TEXT",
                    "target": "#product-stock",
                    "value": entities.get("stock")
                }
            ]

            if entities.get("status"):
                steps.append({
                    "action": "SELECT_OPTION",
                    "target": "#product-status",
                    "value": entities.get("status")
                })

            steps.extend([
                {
                    "action": "SUBMIT",
                    "target": "#save-product",
                    "value": None
                },
                {
                    "action": "OPEN_PAGE",
                    "target": "products",
                    "value": None
                },
                {
                    "action": "READ_TABLE",
                    "target": "#product-table-body",
                    "value": None
                }
            ])

            return Workflow.model_validate({
                "steps": steps
            })

        if intent == "UPDATE_PRODUCT":
            product_name = entities.get("product_name", "").strip()

            steps = [
                {
                    "action": "OPEN_PAGE",
                    "target": "products",
                    "value": None
                }
            ]

            if product_name:
                steps.append({
                    "action": "CLICK",
                    "target": f'button.edit[data-product-name="{product_name}"]',
                    "value": None
                })

            if entities.get("name"):
                steps.append({
                    "action": "ENTER_TEXT",
                    "target": "#product-name",
                    "value": entities["name"]
                })

            if entities.get("category"):
                steps.append({
                    "action": "SELECT_OPTION",
                    "target": "#product-category",
                    "value": entities["category"]
                })

            if entities.get("price"):
                steps.append({
                    "action": "ENTER_TEXT",
                    "target": "#product-price",
                    "value": entities["price"]
                })

            if entities.get("stock"):
                steps.append({
                    "action": "ENTER_TEXT",
                    "target": "#product-stock",
                    "value": entities["stock"]
                })

            if entities.get("status"):
                steps.append({
                    "action": "SELECT_OPTION",
                    "target": "#product-status",
                    "value": entities["status"]
                })

            steps.extend([
                {
                    "action": "SUBMIT",
                    "target": "#save-product",
                    "value": None
                },
                {
                    "action": "OPEN_PAGE",
                    "target": "products",
                    "value": None
                },
                {
                    "action": "READ_TABLE",
                    "target": "#product-table-body",
                    "value": None
                }
            ])

            return Workflow.model_validate({
                "steps": steps
            })

        if intent == "DELETE_CUSTOMER":
            customer_name = entities.get("customer_name", "").strip()

            target = (
                "__CUSTOMER_DELETE__"
                if customer_name
                else "#customer-table-body .action-button.delete"
            )

            return Workflow.model_validate({
                "steps": [
                    {
                        "action": "OPEN_PAGE",
                        "target": "customers",
                        "value": None
                    },
                    {
                        "action": "CLICK",
                        "target": target,
                        "value": customer_name or None
                    },
                    {
                        "action": "DELETE",
                        "target": "#confirm-delete-btn",
                        "value": None
                    },
                    {
                        "action": "OPEN_PAGE",
                        "target": "customers",
                        "value": None
                    },
                    {
                        "action": "READ_TABLE",
                        "target": "#customer-table-body",
                        "value": None
                    }
                ]
            })

        if intent == "DOWNLOAD_REPORT":
            report_type = entities.get("report_type", "").lower()

            if "sales" in report_type:
                target = "#download-sales-report"
            elif "monthly" in report_type:
                target = "#download-monthly-report"
            else:
                target = "#download-daily-report"

            return Workflow.model_validate({
                "steps": [
                    {
                        "action": "OPEN_PAGE",
                        "target": "reports",
                        "value": None
                    },
                    {
                        "action": "DOWNLOAD_FILE",
                        "target": target,
                        "value": None
                    }
                ]
            })

        if intent == "UPLOAD_FILE":
            return Workflow.model_validate({
                "steps": [
                    {
                        "action": "OPEN_PAGE",
                        "target": "files",
                        "value": None
                    },
                    {
                        "action": "UPLOAD_FILE",
                        "target": "#file-upload",
                        "value": entities.get("file_name")
                    },
                    {
                        "action": "CLICK",
                        "target": "#upload-file",
                        "value": None
                    }
                ]
            })

        if intent == "SEND_EMAIL":
            return Workflow.model_validate({
                "steps": [
                    {
                        "action": "OPEN_PAGE",
                        "target": "email",
                        "value": None
                    },
                    {
                        "action": "ENTER_TEXT",
                        "target": "#recipient",
                        "value": entities.get("recipient")
                    },
                    {
                        "action": "ENTER_TEXT",
                        "target": "#subject",
                        "value": entities.get("subject")
                    },
                    {
                        "action": "ENTER_TEXT",
                        "target": "#email-body",
                        "value": entities.get("body")
                    },
                    {
                        "action": "CLICK",
                        "target": "#send-email",
                        "value": None
                    }
                ]
            })

        if intent == "READ_TABLE":
            table = entities.get("table") or entities.get("table_name")

            target = "#customer-table-body"
            page = "customers"

            if table:
                table_lower = str(table).lower()

                if "product" in table_lower:
                    target = "#product-table-body"
                    page = "products"
                elif "employee" in table_lower:
                    target = "#employee-table-body"
                    page = "employees"
                elif "sales" in table_lower:
                    target = "#sales-table-body"
                    page = "reports"
                elif "customer" in table_lower:
                    target = "#customer-table-body"
                    page = "customers"

            return Workflow.model_validate({
                "steps": [
                    {
                        "action": "OPEN_PAGE",
                        "target": page,
                        "value": None
                    },
                    {
                        "action": "READ_TABLE",
                        "target": target,
                        "value": None
                    }
                ]
            })

        if intent == "FILL_FORM":
            return Workflow.model_validate({
                "steps": [
                    {
                        "action": "OPEN_PAGE",
                        "target": "customer-form",
                        "value": None
                    },
                    {
                        "action": "ENTER_TEXT",
                        "target": "#customer-name",
                        "value": entities.get("customer_name")
                    },
                    {
                        "action": "ENTER_TEXT",
                        "target": "#phone-number",
                        "value": entities.get("phone_number")
                    },
                    {
                        "action": "SUBMIT",
                        "target": "#save-customer",
                        "value": None
                    }
                ]
            })

        if intent == "CUSTOMIZE_PAGE":
            target_element = entities.get(
                "target_element", "heading"
            )
            new_value = entities.get("new_value", "")
            visual_theme = (
                entities.get("visual_theme")
                or entities.get("theme")
                or entities.get("style_prompt")
                or ""
            )

            target_map = {
                "heading": "#hero-heading",
                "subtitle": "#hero-subtitle",
                "banner_text": "#hero-banner-text",
                "announcement": "#hero-announcement",
                "contact_number": "#contact-number",
            }

            selector = target_map.get(
                target_element, "#hero-heading"
            )

            steps = [
                {
                    "action": "OPEN_PAGE",
                    "target": "homepage",
                    "value": None
                },
                {
                    "action": "READ_TEXT",
                    "target": selector,
                    "value": None
                },
                {
                    "action": "UPDATE_TEXT",
                    "target": selector,
                    "value": new_value
                }
            ]

            if target_element == "heading" and new_value:
                dynamic_sub = BannerThemeManager.generate_sale_description(new_value)
                steps.append({
                    "action": "UPDATE_TEXT",
                    "target": "#hero-subtitle",
                    "value": dynamic_sub
                })
                steps.append({
                    "action": "ENTER_TEXT",
                    "target": "#hidden-subtitle",
                    "value": dynamic_sub
                })

            theme_prompt = f"{new_value} {visual_theme}".strip()
            theme_info = BannerThemeManager.detect_and_generate_theme(theme_prompt)

            if theme_info and theme_info.get("banner_style"):
                steps.append({
                    "action": "APPLY_STYLE",
                    "target": "#hero-banner",
                    "value": f"background: {theme_info['banner_style']}; color: {theme_info['heading_color']}; padding: 28px; border-radius: 12px; margin-bottom: 24px; position: relative; overflow: hidden;"
                })
                steps.append({
                    "action": "ENTER_TEXT",
                    "target": "#hidden-banner_style",
                    "value": theme_info["banner_style"]
                })
                steps.append({
                    "action": "ENTER_TEXT",
                    "target": "#hidden-banner_theme",
                    "value": theme_info["theme_name"]
                })

            steps.extend([
                {
                    "action": "CLICK",
                    "target": "#save-homepage",
                    "value": None
                },
                {
                    "action": "TAKE_SCREENSHOT",
                    "target": "screenshot_customize.png",
                    "value": "screenshot_customize.png"
                },
            ])

            return Workflow.model_validate({"steps": steps})

        if intent == "UPLOAD_IMAGE":
            target_location = entities.get(
                "target_location", "logo"
            )
            file_name = entities.get("file_name", "")

            upload_map = {
                "logo": (
                    "#logo-upload",
                    "#save-homepage",
                ),
                "banner": (
                    "#banner-upload",
                    "#save-homepage",
                ),
            }

            upload_selector, save_selector = upload_map.get(
                target_location,
                ("#logo-upload", "#save-homepage"),
            )

            steps = [
                {
                    "action": "OPEN_PAGE",
                    "target": "homepage",
                    "value": None
                },
                {
                    "action": "UPLOAD_FILE",
                    "target": upload_selector,
                    "value": file_name
                },
                {
                    "action": "CLICK",
                    "target": save_selector,
                    "value": None
                },
                {
                    "action": "TAKE_SCREENSHOT",
                    "target": "screenshot_upload.png",
                    "value": "screenshot_upload.png"
                },
            ]

            return Workflow.model_validate({"steps": steps})

        if intent == "CREATE_OFFER":
            steps = [
                {
                    "action": "OPEN_PAGE",
                    "target": "offers",
                    "value": None
                },
                {
                    "action": "ENTER_TEXT",
                    "target": "#offer-name",
                    "value": entities.get("offer_name")
                },
                {
                    "action": "ENTER_TEXT",
                    "target": "#offer-discount",
                    "value": entities.get("discount")
                },
            ]

            if entities.get("category"):
                steps.append({
                    "action": "SELECT_OPTION",
                    "target": "#offer-category",
                    "value": entities["category"]
                })

            if entities.get("end_date"):
                steps.append({
                    "action": "ENTER_TEXT",
                    "target": "#offer-end-date",
                    "value": entities["end_date"]
                })

            if entities.get("description"):
                steps.append({
                    "action": "ENTER_TEXT",
                    "target": "#offer-description",
                    "value": entities["description"]
                })

            steps.extend([
                {
                    "action": "SUBMIT",
                    "target": "#save-offer",
                    "value": None
                },
                {
                    "action": "OPEN_PAGE",
                    "target": "offers",
                    "value": None
                },
                {
                    "action": "READ_TABLE",
                    "target": "#offer-table-body",
                    "value": None
                },
                {
                    "action": "TAKE_SCREENSHOT",
                    "target": "screenshot_offer.png",
                    "value": "screenshot_offer.png"
                },
            ])

            return Workflow.model_validate({"steps": steps})

        return Workflow.model_validate({
            "steps": []
        })
