import re

class BannerThemeManager:
    """
    Translates natural language theme descriptions into CSS background gradients,
    color schemes, and dynamic contextual sale descriptions.
    """

    THEME_PRESETS = {
        "summer": {
            "theme_name": "summer",
            "banner_style": "radial-gradient(circle at 80% 50%, rgba(255, 255, 255, 0.85) 0%, transparent 60%), linear-gradient(135deg, #e0f2fe 0%, #f3e8ff 50%, #e0f7fa 100%)",
            "announcement_bg": "#e0f2fe",
            "announcement_color": "#0284c7",
            "heading_color": "#1e3a8a",
            "banner_text_color": "#0369a1",
        },
        "christmas": {
            "theme_name": "christmas",
            "banner_style": "linear-gradient(135deg, #991b1b 0%, #15803d 50%, #064e3b 100%)",
            "announcement_bg": "rgba(255, 255, 255, 0.25)",
            "announcement_color": "#ffffff",
            "heading_color": "#ffffff",
            "banner_text_color": "#fef08a",
        },
        "winter": {
            "theme_name": "winter",
            "banner_style": "linear-gradient(135deg, #1e3a8a 0%, #0284c7 50%, #e0f2fe 100%)",
            "announcement_bg": "rgba(255, 255, 255, 0.2)",
            "announcement_color": "#ffffff",
            "heading_color": "#ffffff",
            "banner_text_color": "#bfdbfe",
        },
        "festival": {
            "theme_name": "festival",
            "banner_style": "linear-gradient(135deg, #581c87 0%, #c026d3 50%, #f59e0b 100%)",
            "announcement_bg": "rgba(255, 255, 255, 0.25)",
            "announcement_color": "#ffffff",
            "heading_color": "#ffffff",
            "banner_text_color": "#fef08a",
        },
        "sunset": {
            "theme_name": "sunset",
            "banner_style": "linear-gradient(135deg, #c2410c 0%, #ea580c 50%, #eab308 100%)",
            "announcement_bg": "rgba(255, 255, 255, 0.25)",
            "announcement_color": "#ffffff",
            "heading_color": "#ffffff",
            "banner_text_color": "#fef08a",
        },
        "red_green": {
            "theme_name": "red_green",
            "banner_style": "linear-gradient(135deg, #b91c1c 0%, #15803d 100%)",
            "announcement_bg": "rgba(255, 255, 255, 0.25)",
            "announcement_color": "#ffffff",
            "heading_color": "#ffffff",
            "banner_text_color": "#fef08a",
        },
        "indian_flag": {
            "theme_name": "indian_flag",
            "banner_style": "linear-gradient(135deg, #ff9933 0%, #ffffff 50%, #138808 100%)",
            "announcement_bg": "rgba(0, 0, 128, 0.1)",
            "announcement_color": "#000080",
            "heading_color": "#000080",
            "banner_text_color": "#138808",
        },
        "default": {
            "theme_name": "default",
            "banner_style": "radial-gradient(circle at 80% 50%, rgba(255, 255, 255, 0.85) 0%, transparent 60%), linear-gradient(135deg, #e0f2fe 0%, #f3e8ff 50%, #e0f7fa 100%)",
            "announcement_bg": "#e0f2fe",
            "announcement_color": "#0284c7",
            "heading_color": "#1e3a8a",
            "banner_text_color": "#0369a1",
        }
    }

    @classmethod
    def detect_and_generate_theme(cls, prompt: str) -> dict:
        if not prompt:
            return cls.THEME_PRESETS["default"].copy()

        p = str(prompt).lower()

        if any(w in p for w in ["indian", "flag", "independence", "tricolor", "tri-color", "saffron", "republic"]):
            return cls.THEME_PRESETS["indian_flag"].copy()

        if any(w in p for w in ["summer", "beach", "ocean", "waves", "sun", "tropical", "shells", "seashell"]):
            if "sunset" in p:
                return cls.THEME_PRESETS["sunset"].copy()
            return cls.THEME_PRESETS["summer"].copy()

        if any(w in p for w in ["christmas", "snow", "xmas", "santa", "tree", "lights"]):
            return cls.THEME_PRESETS["christmas"].copy()

        if "red" in p and "green" in p:
            return cls.THEME_PRESETS["red_green"].copy()

        if any(w in p for w in ["winter", "ice", "frost", "cold"]):
            return cls.THEME_PRESETS["winter"].copy()

        if any(w in p for w in ["festival", "diwali", "diya", "celebration", "sparkle", "festive", "party"]):
            return cls.THEME_PRESETS["festival"].copy()

        if any(w in p for w in ["sunset", "gold", "golden", "amber", "warm"]):
            return cls.THEME_PRESETS["sunset"].copy()

        return cls.THEME_PRESETS["default"].copy()

    @staticmethod
    def generate_sale_description(heading: str) -> str:
        """
        Dynamically generates a relevant sale description based on the sale heading/name.
        """
        if not heading:
            return "Unbeatable seasonal deals, hot promotional discounts, and exclusive storewide savings!"
        
        h = str(heading).lower()

        if "summer" in h:
            return "Hot summer discounts, sun-filled seasonal deals, and exclusive storewide savings across all categories!"
        elif any(w in h for w in ["independence", "republic", "freedom", "patriotic", "july 4", "august 15"]):
            return "Celebrate freedom with massive storewide deals, patriotic discounts, and special holiday savings!"
        elif any(w in h for w in ["christmas", "xmas", "santa", "holiday", "festive"]):
            return "Unwrap festive holiday discounts, seasonal gift specials, and magical storewide savings!"
        elif any(w in h for w in ["winter", "frost", "snow", "cold"]):
            return "Warm up your season with cool winter discounts, cozy deals, and special promotional savings!"
        elif any(w in h for w in ["diwali", "festival", "sparkle", "celebration"]):
            return "Brighten your celebrations with special festival discounts, festive offers, and grand savings!"
        elif any(w in h for w in ["black friday", "cyber", "flash", "mega", "clearance"]):
            return "Huge price drops, limited-time flash discounts, and mega storewide savings across our entire catalog!"
        else:
            return f"Exclusive promotional deals and special limited-time savings on {heading}!"
