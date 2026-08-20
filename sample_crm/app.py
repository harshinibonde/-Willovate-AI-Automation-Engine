from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
from io import BytesIO
import csv
from datetime import datetime
import os
import sys
from werkzeug.utils import secure_filename
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from willovate.banner_theme import BannerThemeManager

app = Flask(__name__)
app.secret_key = "willovate-crm-demo-key"

customers = [
    {"id": 1, "name": "Amit Sharma", "email": "amit.sharma@example.com", "phone": "9876543210", "company": "TechNova", "status": "Active"},
    {"id": 2, "name": "Priya Mehta", "email": "priya.mehta@example.com", "phone": "9823456712", "company": "BrightLabs", "status": "Active"},
    {"id": 3, "name": "Rahul Verma", "email": "rahul.verma@example.com", "phone": "9812345678", "company": "Vertex Solutions", "status": "Pending"},
    {"id": 4, "name": "Ananya Patel", "email": "ananya.patel@example.com", "phone": "9898765432", "company": "CloudPeak", "status": "Active"},
]

products = [
    {"id": 1, "name": "CRM Pro", "category": "Software", "price": 4999, "stock": 120, "status": "Available"},
    {"id": 2, "name": "Analytics Suite", "category": "Analytics", "price": 7999, "stock": 75, "status": "Available"},
    {"id": 3, "name": "Automation Pack", "category": "Automation", "price": 6499, "stock": 42, "status": "Low Stock"},
    {"id": 4, "name": "Enterprise CRM", "category": "Software", "price": 14999, "stock": 18, "status": "Low Stock"},
]

@app.context_processor
def inject_counts():
    return {
        "customer_count": len(customers),
        "product_count": len(products),
        "active_customers": sum(
            1 for customer in customers
            if customer["status"] == "Active"
        ),
    }

@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        homepage_settings=homepage_settings,
        offers=offers_list
    )

@app.route("/customers")
def customer_list():
    search = request.args.get("search", "").strip().lower()
    filtered_customers = customers

    if search:
        filtered_customers = [
            customer for customer in customers
            if search in customer["name"].lower()
            or search in customer["email"].lower()
            or search in customer["company"].lower()
            or search in customer["phone"]
        ]

    return render_template(
        "customers.html",
        customers=filtered_customers,
        search=search,
    )

@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form.get("customer_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone_number", "").strip()
        company = request.form.get("company", "").strip()
        status = request.form.get("status", "Active")

        if not name or not phone:
            flash(
                "Customer name and phone number are required.",
                "error",
            )
            return render_template("customer_form.html")

        new_customer = {
            "id": max(
                [customer["id"] for customer in customers],
                default=0,
            ) + 1,
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "status": status,
        }

        customers.append(new_customer)

        flash(
            f"{name} was added successfully.",
            "success",
        )

        return redirect(url_for("customer_list"))

    return render_template("customer_form.html")

@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
def edit_customer(customer_id):
    customer = next(
        (
            customer
            for customer in customers
            if customer["id"] == customer_id
        ),
        None,
    )

    if not customer:
        flash("Customer not found.", "error")
        return redirect(url_for("customer_list"))

    if request.method == "POST":
        customer["name"] = request.form.get(
            "customer_name",
            "",
        ).strip()

        customer["email"] = request.form.get(
            "email",
            "",
        ).strip()

        customer["phone"] = request.form.get(
            "phone_number",
            "",
        ).strip()

        customer["company"] = request.form.get(
            "company",
            "",
        ).strip()

        customer["status"] = request.form.get(
            "status",
            "Active",
        )

        flash(
            f"{customer['name']} was updated successfully.",
            "success",
        )

        return redirect(url_for("customer_list"))

    return render_template(
        "customer_form.html",
        customer=customer,
        edit_mode=True,
    )

@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
def delete_customer(customer_id):
    global customers

    customer = next(
        (
            customer
            for customer in customers
            if customer["id"] == customer_id
        ),
        None,
    )

    if not customer:
        return jsonify({
            "success": False,
            "message": "Customer not found.",
        }), 404

    customers = [
        item for item in customers
        if item["id"] != customer_id
    ]

    return jsonify({
        "success": True,
        "message": f"{customer['name']} was deleted successfully.",
    })

@app.route("/api/customers")
def api_customers():
    return jsonify({
        "customers": customers,
        "count": len(customers),
    })

# ---------------- PRODUCTS ----------------

@app.route("/products")
def product_list():
    search = request.args.get("search", "").strip().lower()
    filtered_products = products

    if search:
        filtered_products = [
            product for product in products
            if search in product["name"].lower()
            or search in product["category"].lower()
        ]

    return render_template(
        "products.html",
        products=filtered_products,
        search=search,
    )

@app.route("/products/add", methods=["POST"])
def add_product():
    name = request.form.get("product_name", "").strip()
    category = request.form.get("category", "").strip()
    price = request.form.get("price", "").strip()
    stock = request.form.get("stock", "").strip()
    status = request.form.get("status", "Available")

    if not name or not category or not price or not stock:
        flash(
            "Product name, category, price and stock are required.",
            "error",
        )
        return redirect(url_for("product_list"))

    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        flash(
            "Price must be a number and stock must be a whole number.",
            "error",
        )
        return redirect(url_for("product_list"))

    new_product = {
        "id": max(
            [product["id"] for product in products],
            default=0,
        ) + 1,
        "name": name,
        "category": category,
        "price": price,
        "stock": stock,
        "status": status,
    }

    products.append(new_product)

    flash(
        f"{name} was added successfully.",
        "success",
    )

    return redirect(url_for("product_list"))

@app.route("/products/<int:product_id>/edit", methods=["POST"])
def edit_product(product_id):
    product = next(
        (
            product
            for product in products
            if product["id"] == product_id
        ),
        None,
    )

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found.",
        }), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        product["name"] = data["name"].strip()

    if "category" in data:
        product["category"] = data["category"].strip()

    if "price" in data:
        product["price"] = float(data["price"])

    if "stock" in data:
        product["stock"] = int(data["stock"])

    if "status" in data:
        product["status"] = data["status"]

    return jsonify({
        "success": True,
        "message": f"{product['name']} was updated successfully.",
        "product": product,
    })

@app.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    global products

    product = next(
        (
            product
            for product in products
            if product["id"] == product_id
        ),
        None,
    )

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found.",
        }), 404

    products = [
        item for item in products
        if item["id"] != product_id
    ]

    return jsonify({
        "success": True,
        "message": f"{product['name']} was deleted successfully.",
    })

@app.route("/api/products")
def api_products():
    return jsonify({
        "products": products,
        "count": len(products),
    })

# ---------------- REPORTS ----------------

def create_csv(filename, headers, rows):
    output = BytesIO()
    text = []

    text.append(",".join(headers))

    for row in rows:
        text.append(
            ",".join(
                str(value).replace(",", " ")
                for value in row
            )
        )

    content = "\n".join(text)
    output.write(content.encode("utf-8"))
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename,
    )

@app.route("/reports")
def reports():
    return render_template("reports.html")

@app.route("/reports/daily")
def daily_report():
    today = datetime.now().strftime("%Y-%m-%d")

    headers = [
        "Customer",
        "Company",
        "Status",
    ]

    rows = [
        [
            customer["name"],
            customer["company"],
            customer["status"],
        ]
        for customer in customers
    ]

    return create_csv(
        f"daily_report_{today}.csv",
        headers,
        rows,
    )

@app.route("/reports/sales")
def sales_report():
    headers = [
        "Product",
        "Category",
        "Price",
        "Stock",
        "Estimated Value",
    ]

    rows = [
        [
            product["name"],
            product["category"],
            product["price"],
            product["stock"],
            product["price"] * product["stock"],
        ]
        for product in products
    ]

    return create_csv(
        "sales_report.csv",
        headers,
        rows,
    )

@app.route("/reports/monthly")
def monthly_report():
    headers = [
        "Metric",
        "Value",
    ]

    rows = [
        ["Total Customers", len(customers)],
        ["Active Customers", sum(
            1 for customer in customers
            if customer["status"] == "Active"
        )],
        ["Total Products", len(products)],
        ["Total Inventory Units", sum(
            product["stock"]
            for product in products
        )],
        ["Estimated Inventory Value", sum(
            product["price"] * product["stock"]
            for product in products
        )],
    ]

    return create_csv(
        "monthly_report.csv",
        headers,
        rows,
    )

@app.route("/email", methods=["GET", "POST"])
def email():
    if request.method == "POST":
        recipient = request.form.get("recipient", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()

        if not recipient or not subject or not body:
            return {
                "success": False,
                "message": "Recipient, subject and body are required."
            }, 400

        print("\nEMAIL SENT")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")

        return {
            "success": True,
            "message": "Email sent successfully."
        }

    return render_template("email.html")

@app.route("/files", methods=["GET", "POST"])
def files():
    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if not uploaded_file or not uploaded_file.filename:
            return jsonify({
                "success": False,
                "message": "No file selected."
            }), 400

        filename = secure_filename(uploaded_file.filename)

        upload_dir = os.path.join(
            app.root_path,
            "uploads"
        )

        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(
            upload_dir,
            filename
        )

        uploaded_file.save(filepath)

        print(f"\nFILE UPLOADED: {filename}")

        return jsonify({
            "success": True,
            "filename": filename,
            "message": "File uploaded successfully."
        })

    return render_template("files.html")


homepage_settings = {
    "heading": "Mega Summer Sale",
    "subtitle": "Hot summer discounts, sun-filled seasonal deals, and exclusive storewide savings across all categories!",
    "banner_text": "",
    "announcement": "⚡ Special Announcement: Free Shipping on Orders Over $50",
    "contact_number": "+1 (800) 555-0199",
    "logo_url": None,
    "banner_url": None,
    "banner_style": "radial-gradient(circle at 80% 50%, rgba(255, 255, 255, 0.85) 0%, transparent 60%), linear-gradient(135deg, #e0f2fe 0%, #f3e8ff 50%, #e0f7fa 100%)",
    "banner_theme": "default",
    "announcement_bg": "#e0f2fe",
    "announcement_color": "#0284c7",
    "heading_color": "#1e3a8a",
    "banner_text_color": "#0369a1",
    "badge_text": "",
}

offers_list = [
    {
        "id": 1,
        "offer_name": "Summer Special",
        "discount": "20% OFF",
        "category": "Software",
        "end_date": "2026-09-01",
        "description": "Exclusive discount on all software licenses.",
    }
]


@app.context_processor
def inject_homepage_settings():
    if not homepage_settings.get("subtitle") or "Empowering your business" in homepage_settings["subtitle"]:
        homepage_settings["subtitle"] = BannerThemeManager.generate_sale_description(homepage_settings.get("heading", ""))
    return dict(
        homepage_settings=homepage_settings,
        offers=offers_list,
        get_sale_description=BannerThemeManager.generate_sale_description
    )


@app.route("/homepage", methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        upload_dir = os.path.join(app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        logo_file = request.files.get("logo_file")
        if logo_file and logo_file.filename:
            filename = secure_filename(logo_file.filename)
            logo_file.save(os.path.join(upload_dir, filename))
            homepage_settings["logo_url"] = f"/static/uploads/{filename}"

        banner_file = request.files.get("banner_file")
        if banner_file and banner_file.filename:
            filename = secure_filename(banner_file.filename)
            banner_file.save(os.path.join(upload_dir, filename))
            homepage_settings["banner_url"] = f"/static/uploads/{filename}"

        if request.form.get("heading"):
            new_heading = request.form.get("heading").strip()
            homepage_settings["heading"] = new_heading
            
            sub = request.form.get("subtitle", "").strip()
            if not sub or "Empowering your business" in sub:
                homepage_settings["subtitle"] = BannerThemeManager.generate_sale_description(new_heading)
            else:
                homepage_settings["subtitle"] = sub

        if request.form.get("banner_text"):
            homepage_settings["banner_text"] = request.form.get("banner_text")
        if request.form.get("announcement"):
            homepage_settings["announcement"] = request.form.get("announcement")
        if request.form.get("contact_number"):
            homepage_settings["contact_number"] = request.form.get("contact_number")
        if request.form.get("banner_style"):
            homepage_settings["banner_style"] = request.form.get("banner_style")
        if request.form.get("banner_theme"):
            homepage_settings["banner_theme"] = request.form.get("banner_theme")
        if request.form.get("announcement_bg"):
            homepage_settings["announcement_bg"] = request.form.get("announcement_bg")
        if request.form.get("announcement_color"):
            homepage_settings["announcement_color"] = request.form.get("announcement_color")
        if request.form.get("heading_color"):
            homepage_settings["heading_color"] = request.form.get("heading_color")
        if request.form.get("banner_text_color"):
            homepage_settings["banner_text_color"] = request.form.get("banner_text_color")

        return render_template(
            "homepage.html", homepage_settings=homepage_settings
        )

    return render_template(
        "homepage.html", homepage_settings=homepage_settings
    )


@app.route("/offers", methods=["GET"])
def offers():
    return render_template("offers.html", offers=offers_list)


@app.route("/offers/add", methods=["POST"])
def add_offer():
    offer_name = request.form.get("offer_name")
    discount = request.form.get("discount")
    category = request.form.get("category", "All Categories")
    end_date = request.form.get("end_date")
    description = request.form.get("description")

    if not offer_name or not discount:
        return jsonify({
            "success": False,
            "message": "Offer name and discount are required."
        }), 400

    new_offer = {
        "id": len(offers_list) + 1,
        "offer_name": offer_name,
        "discount": discount,
        "category": category,
        "end_date": end_date,
        "description": description,
    }
    offers_list.append(new_offer)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "offer": new_offer,
            "message": f"Offer '{offer_name}' created successfully."
        })

    return redirect(url_for("offers"))


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )