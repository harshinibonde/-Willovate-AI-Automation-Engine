document.addEventListener("DOMContentLoaded", () => {
    const deleteModal = document.getElementById("delete-modal");
    const deleteName = document.getElementById("delete-customer-name");
    const confirmButton = document.getElementById("confirm-delete-btn");
    const cancelButton = document.getElementById("cancel-delete-btn");

    if (!deleteModal) {
        return;
    }

    let selectedCustomerId = null;

    document.querySelectorAll(
        ".action-button.delete[data-customer-id]"
    ).forEach((button) => {
        button.addEventListener("click", () => {
            selectedCustomerId = button.dataset.customerId;
            deleteName.textContent = button.dataset.customerName;

            deleteModal.hidden = false;
            confirmButton.focus();
        });
    });

    cancelButton.addEventListener("click", () => {
        closeDeleteModal();
    });

    deleteModal.addEventListener("click", (event) => {
        if (event.target === deleteModal) {
            closeDeleteModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            !deleteModal.hidden
        ) {
            closeDeleteModal();
        }
    });

    confirmButton.addEventListener("click", async () => {
        if (!selectedCustomerId) {
            return;
        }

        confirmButton.disabled = true;
        confirmButton.textContent = "Deleting...";

        const url = window.CUSTOMER_DELETE_URL.replace(
            "/0/delete",
            `/${selectedCustomerId}/delete`
        );

        try {
            const response = await fetch(url, {
                method: "POST"
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message || "Unable to delete customer."
                );
            }

            const row = document.getElementById(
                `customer-row-${selectedCustomerId}`
            );

            if (row) {
                row.remove();
            }

            closeDeleteModal();

            showCustomerNotification(
                result.message,
                "success"
            );
        } catch (error) {
            showCustomerNotification(
                error.message,
                "error"
            );
        } finally {
            confirmButton.disabled = false;
            confirmButton.textContent = "Delete Customer";
        }
    });

    function closeDeleteModal() {
        deleteModal.hidden = true;
        selectedCustomerId = null;
    }

    function showCustomerNotification(message, type) {
        const pageContainer = document.querySelector(
            ".page-container"
        );

        if (!pageContainer) {
            return;
        }

        const container = document.createElement("div");

        container.className = "flash-container";

        container.innerHTML = `
            <div class="flash-message ${type}">
                <span>${type === "success" ? "✓" : "!"}</span>
                <span>${message}</span>
            </div>
        `;

        pageContainer.prepend(container);

        setTimeout(() => {
            container.remove();
        }, 4000);
    }
});