document.addEventListener("DOMContentLoaded", function () {
    const categorySelect = document.getElementById("category");
    const productDropdownField = document.getElementById("productDropdownField");
    const productDropdown = document.getElementById("productDropdown");
    const imeiField = document.getElementById("imeiField");
    const quantityField = document.getElementById("quantityField");
    const addProductBtn = document.getElementById("addProductBtn");
    const productList = document.getElementById("productList");
    const saleForm = document.getElementById("saleForm");

    let cart = [];

    categorySelect.addEventListener("change", function () {
        const categoryId = categorySelect.value;
        if (categoryId) {
            fetch(`/pos/fetch_products_by_category/${categoryId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.products.length > 0) {
                        productDropdown.innerHTML = "";
                        data.products.forEach(product => {
                            const option = document.createElement("option");
                            option.value = product.id;
                            option.textContent = product.name;
                            option.dataset.hasImei = product.has_imei ? "true" : "false";
                            productDropdown.appendChild(option);
                        });
                        productDropdownField.style.display = "block";
                        productDropdown.dispatchEvent(new Event("change"));
                    } else {
                        productDropdownField.style.display = "none";
                    }
                });
        } else {
            productDropdownField.style.display = "none";
        }
    });

    productDropdown.addEventListener("change", function () {
        const selectedOption = productDropdown.options[productDropdown.selectedIndex];
        const hasImei = selectedOption.dataset.hasImei === "true";
        if (hasImei) {
            imeiField.style.display = "block";
            quantityField.style.display = "none";
        } else {
            imeiField.style.display = "none";
            quantityField.style.display = "block";
        }
    });

    addProductBtn.addEventListener("click", function () {
        const selectedOption = productDropdown.options[productDropdown.selectedIndex];
        const productId = productDropdown.value;
        const productName = selectedOption.textContent;
        const hasImei = selectedOption.dataset.hasImei === "true";

        if (!productId) {
            alert("Please select a product.");
            return;
        }

        if (hasImei) {
            const imei = document.getElementById("imei").value.trim();
            if (!imei) {
                alert("Please enter the IMEI.");
                return;
            }
            // Check if serial product with this IMEI exists
            fetch(`/pos/fetch_product_by_imei/?imei=${imei}`)
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        alert(data.error);
                    } else {
                        cart.push({
                            productId: productId,
                            productName: productName,
                            imei: imei,
                            quantity: 1
                        });
                        updateCartUI();
                        document.getElementById("imei").value = "";
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("An error occurred while verifying the IMEI.");
                });
        } else {
            const quantity = parseInt(document.getElementById("quantity").value);
            if (!quantity || quantity <= 0) {
                alert("Please enter a valid quantity.");
                return;
            }
            // Check if sufficient stock is available
            fetch(`/pos/api/check-stock/?product_id=${productId}&quantity=${quantity}`)
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        alert(data.error);
                    } else {
                        cart.push({
                            productId: productId,
                            productName: productName,
                            quantity: quantity
                        });
                        updateCartUI();
                        document.getElementById("quantity").value = "";
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("An error occurred while checking product stock.");
                });
        }
    });

    function updateCartUI() {
        productList.innerHTML = "";
        if (cart.length === 0) {
            productList.innerHTML = "<p>No products added yet.</p>";
            return;
        }
        cart.forEach((item, index) => {
            const div = document.createElement("div");
            div.className = "cart-item";
            let details = item.productName;
            if (item.imei) {
                details += " (IMEI: " + item.imei + ")";
            } else {
                details += " (Qty: " + item.quantity + ")";
            }
            div.innerHTML = `
                <span>${details}</span>
                <button type="button" class="remove-btn" data-index="${index}">Remove</button>
            `;
            productList.appendChild(div);
        });
    }

    productList.addEventListener("click", function (e) {
        if (e.target.classList.contains("remove-btn")) {
            const index = e.target.getAttribute("data-index");
            cart.splice(index, 1);
            updateCartUI();
        }
    });

    saleForm.addEventListener("submit", function (e) {
        e.preventDefault();

        if (cart.length === 0) {
            alert("Please add products to the cart before submitting.");
            return;
        }

        const formData = new FormData(saleForm);
        formData.append("products", JSON.stringify(cart));

        fetch(saleForm.action, {
            method: "POST",
            body: formData
        }).then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                response.text().then(html => {
                    document.open();
                    document.write(html);
                    document.close();
                });
            }
        }).catch(error => {
            console.error("Error:", error);
            alert("An error occurred while submitting the sale.");
        });
    });
});