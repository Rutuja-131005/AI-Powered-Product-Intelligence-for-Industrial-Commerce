/**
 * Product Details Controller
 */
function renderProductDetail(productData) {
    const el = document.getElementById("product-detail-container");
    if (el && productData) {
        el.innerHTML = `<h4>${productData.BRAND_NAME} - ${productData.PART_NUMBER}</h4>`;
    }
}
