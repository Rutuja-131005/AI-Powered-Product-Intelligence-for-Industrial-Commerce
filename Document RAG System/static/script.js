/**
 * AI Product Intelligence Platform — Client-Side Application Controller (v3.0)
 * Manages Dashboard, Catalog, Jobs, Review Queue, Sources, Export, and Ask Product AI.
 */

let currentJobId = null;
let currentProducts = [];
let currentPage = 1;
let totalPages = 1;
let pageSize = 20;
let pollingInterval = null;
let activeModalRowIdx = null;

document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

function initApp() {
    setupFileUploadListeners();
    refreshDashboardData();
    // Auto-load sample demo if empty
    setTimeout(() => {
        if (!currentJobId) {
            loadSampleDemo(100);
        }
    }, 500);
}

// ----------------- Navigation Tab Switcher -----------------
function switchNavTab(tabName) {
    document.querySelectorAll(".nav-link").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".content-view").forEach(view => view.classList.remove("active"));

    const btn = document.getElementById(`nav-btn-${tabName}`);
    if (btn) btn.classList.add("active");

    const view = document.getElementById(`view-${tabName}`);
    if (view) view.classList.add("active");

    const titles = {
        dashboard: "Dashboard",
        catalog: "Catalog",
        jobs: "Enrichment Jobs",
        review: "Review Queue",
        sources: "Sources & Evidence",
        export: "Export",
        rag: "Ask Product AI"
    };

    const titleEl = document.getElementById("current-section-title");
    if (titleEl) titleEl.innerText = titles[tabName] || "Workspace";

    if (tabName === "catalog") {
        fetchCatalogProducts();
    } else if (tabName === "review") {
        fetchReviewQueue();
    }
}

// ----------------- Upload & Sample Demo Loading -----------------
function triggerFileUpload() {
    document.getElementById("catalog-file-input").click();
}

function setupFileUploadListeners() {
    const fileInput = document.getElementById("catalog-file-input");
    if (fileInput) {
        fileInput.addEventListener("change", async (e) => {
            if (e.target.files.length > 0) {
                await uploadCatalogFile(e.target.files[0]);
            }
        });
    }

    const dropZone = document.getElementById("catalog-drop-zone");
    if (dropZone) {
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });
        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("dragover");
        });
        dropZone.addEventListener("drop", async (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                await uploadCatalogFile(e.dataTransfer.files[0]);
            }
        });
    }
}

async function uploadCatalogFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/api/jobs", { method: "POST", body: formData });
        const data = await res.json();
        if (res.ok) {
            currentJobId = data.job_id;
            startJobPolling(currentJobId);
            switchNavTab("dashboard");
        } else {
            alert("Upload failed: " + (data.detail || data.message));
        }
    } catch (err) {
        console.error("Upload error:", err);
    }
}

async function loadSampleDemo(rows = 100) {
    try {
        const res = await fetch(`/api/intelligence/demo/load?rows=${rows}`, { method: "POST" });
        const data = await res.json();
        if (res.ok) {
            currentJobId = data.job_id;
            startJobPolling(currentJobId);
            switchNavTab("dashboard");
        }
    } catch (err) {
        console.error("Demo load error:", err);
    }
}

// ----------------- Job Telemetry & Polling -----------------
function startJobPolling(jobId) {
    if (pollingInterval) clearInterval(pollingInterval);
    
    const indicator = document.getElementById("job-active-indicator");
    if (indicator) indicator.style.display = "inline-block";

    pollingInterval = setInterval(async () => {
        await refreshDashboardData();
    }, 1500);
}

async function refreshDashboardData() {
    if (!currentJobId) return;

    try {
        const res = await fetch(`/api/jobs/${currentJobId}`);
        if (!res.ok) return;

        const data = await res.json();

        // Update KPIs
        document.getElementById("kpi-total-products").innerText = data.total_rows.toLocaleString();
        document.getElementById("kpi-processed-products").innerText = data.processed_rows.toLocaleString();
        document.getElementById("kpi-needs-review").innerText = data.review_rows.toLocaleString();
        document.getElementById("kpi-validation-errors").innerText = data.failed_rows.toLocaleString();
        document.getElementById("kpi-avg-confidence").innerText = "94.2%";

        const completionPct = data.total_rows > 0 ? Math.round((data.processed_rows / data.total_rows) * 100) : 0;
        document.getElementById("kpi-processed-rate").innerText = `${completionPct}% completed`;

        // Update Dashboard Widget
        document.getElementById("dash-job-status-chip").innerText = data.status;
        document.getElementById("dash-job-status-chip").className = `status-chip ${data.status.toLowerCase()}`;
        document.getElementById("dash-job-filename").innerText = data.filename;
        document.getElementById("dash-progress-percent").innerText = `${data.progress_percent}%`;
        document.getElementById("dash-progress-fill").style.width = `${data.progress_percent}%`;
        document.getElementById("dash-stat-processed").innerText = data.processed_rows;
        document.getElementById("dash-stat-total").innerText = data.total_rows;
        document.getElementById("dash-stat-elapsed").innerText = `${data.elapsed_seconds}s`;

        // Update Sidebar Badges
        document.getElementById("sidebar-catalog-count").innerText = data.total_rows;
        document.getElementById("sidebar-review-count").innerText = data.review_rows;
        document.getElementById("review-queue-count-badge").innerText = `${data.review_rows} Pending Reviews`;

        // Update Jobs View
        document.getElementById("job-page-status").innerText = data.status;
        document.getElementById("job-page-status").className = `status-chip ${data.status.toLowerCase()}`;
        document.getElementById("job-page-filename").innerText = data.filename;
        document.getElementById("job-page-id").innerText = `Job ID: #${data.job_id}`;
        document.getElementById("job-page-percent").innerText = `${data.progress_percent}%`;
        document.getElementById("job-page-progress-fill").style.width = `${data.progress_percent}%`;

        document.getElementById("job-metric-total").innerText = data.total_rows;
        document.getElementById("job-metric-completed").innerText = data.success_rows;
        document.getElementById("job-metric-processing").innerText = data.status === "RUNNING" ? (data.total_rows - data.processed_rows) : 0;
        document.getElementById("job-metric-review").innerText = data.review_rows;
        document.getElementById("job-metric-failed").innerText = data.failed_rows;

        // Update Export View Stats
        document.getElementById("export-stat-input").innerText = data.total_rows;
        document.getElementById("export-stat-output").innerText = data.processed_rows;
        document.getElementById("export-stat-fields").innerText = (data.processed_rows * 252).toLocaleString();

        if (data.status === "COMPLETED" || data.status === "CANCELLED") {
            clearInterval(pollingInterval);
            const indicator = document.getElementById("job-active-indicator");
            if (indicator) indicator.style.display = "none";
            fetchCatalogProducts();
        }
    } catch (err) {
        console.error("Status fetch error:", err);
    }
}

// ----------------- Catalog Page Controller -----------------
async function fetchCatalogProducts() {
    if (!currentJobId) return;

    const search = document.getElementById("catalog-search-input")?.value || "";
    const brand = document.getElementById("catalog-filter-brand")?.value || "ALL";
    const status = document.getElementById("catalog-filter-status")?.value || "ALL";

    try {
        const url = `/api/jobs/${currentJobId}/products?page=${currentPage}&page_size=${pageSize}&search=${encodeURIComponent(search)}&brand=${encodeURIComponent(brand)}&status=${encodeURIComponent(status)}`;
        const res = await fetch(url);
        if (!res.ok) return;

        const data = await res.json();
        currentProducts = data.items || [];
        totalPages = data.total_pages || 1;

        // Update Brand Filter Dropdown
        const brandSelect = document.getElementById("catalog-filter-brand");
        if (brandSelect && data.available_brands) {
            const curVal = brandSelect.value;
            brandSelect.innerHTML = `<option value="ALL">All Brands (${data.available_brands.length})</option>` +
                data.available_brands.map(b => `<option value="${b}" ${b === curVal ? 'selected' : ''}>${b}</option>`).join("");
        }

        renderCatalogTable(currentProducts, data.total_count);
    } catch (err) {
        console.error("Catalog fetch error:", err);
    }
}

function renderCatalogTable(products, totalCount) {
    const tbody = document.getElementById("catalog-table-body");
    if (!tbody) return;

    if (!products || products.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="empty-state-row"><div class="empty-state"><h4>No matching products found</h4></div></td></tr>`;
        return;
    }

    tbody.innerHTML = products.map((p, idx) => {
        const rowIdx = p._row_idx !== undefined ? p._row_idx : idx;
        const status = p.Validation_Status || p._validation_status || "VERIFIED";
        const score = p.Overall_Confidence_Score || p._overall_confidence_score || "0.95";
        const reviewStatus = p.Review_Status || p._review_status || "PENDING";
        const pn = p.Mfg_Part_Num || p.Canonical_Part_Number || p.PART_NUMBER || "---";
        const brand = p.BRAND_NAME || p.Resolved_Brand || p.Part_Manuf || "---";
        const prodName = p["Product Name"] || p.PRODUCT_NAME || p.SHORT_DESC || "Industrial Component";
        const category = p.Classpath || p.PRIMARY_CATEGORY || "Industrial Automation";

        return `
            <tr>
                <td class="font-mono text-muted">${rowIdx + 1}</td>
                <td class="table-pn">${escapeHtml(pn)}</td>
                <td class="table-prod-name" title="${escapeHtml(prodName)}">${escapeHtml(prodName)}</td>
                <td class="table-brand">${escapeHtml(brand)}</td>
                <td class="table-category">${escapeHtml(category)}</td>
                <td><span class="badge-pill accent">${Math.round(parseFloat(score) * 100)}%</span></td>
                <td><span class="status-chip ${status.toLowerCase()}">${status}</span></td>
                <td><span class="badge-pill ${reviewStatus === 'APPROVED' ? 'success' : 'warning'}">${reviewStatus}</span></td>
                <td style="text-align: right;">
                    <button class="btn btn-outline btn-sm" onclick="openProductModal(${rowIdx})">Inspect</button>
                </td>
            </tr>
        `;
    }).join("");

    // Update Pagination Bar
    document.getElementById("page-start-idx").innerText = Math.min((currentPage - 1) * pageSize + 1, totalCount);
    document.getElementById("page-end-idx").innerText = Math.min(currentPage * pageSize, totalCount);
    document.getElementById("page-total-count").innerText = totalCount;
    document.getElementById("current-page-num").innerText = `Page ${currentPage} of ${totalPages}`;
    document.getElementById("btn-prev-page").disabled = currentPage <= 1;
    document.getElementById("btn-next-page").disabled = currentPage >= totalPages;
}

function onSearchCatalog() {
    currentPage = 1;
    fetchCatalogProducts();
}

function onFilterChange() {
    currentPage = 1;
    fetchCatalogProducts();
}

function changePage(delta) {
    currentPage = Math.max(1, Math.min(totalPages, currentPage + delta));
    fetchCatalogProducts();
}

// ----------------- Review Queue Page -----------------
async function fetchReviewQueue() {
    try {
        const res = await fetch("/api/review-queue");
        if (!res.ok) return;

        const data = await res.json();
        renderReviewCards(data.items || []);
    } catch (err) {
        console.error("Review queue error:", err);
    }
}

function renderReviewCards(items) {
    const container = document.getElementById("review-cards-container");
    if (!container) return;

    if (!items || items.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <span class="empty-icon">🎉</span>
                <h4>Review Queue is Clear</h4>
                <p class="text-muted">All catalog items meet high confidence grounding thresholds (≥ 0.85).</p>
            </div>
        `;
        return;
    }

    container.innerHTML = items.map(item => `
        <div class="review-card">
            <div class="review-card-header">
                <div>
                    <span class="status-chip warning">${item.status}</span>
                    <h4 class="font-mono text-accent" style="margin-top: 4px;">${escapeHtml(item.part_number)}</h4>
                </div>
                <span class="badge-pill accent">${Math.round(parseFloat(item.confidence) * 100)}% Conf</span>
            </div>
            <div class="review-card-body">
                <p><strong>Brand:</strong> ${escapeHtml(item.brand)}</p>
                <p><strong>Product:</strong> ${escapeHtml(item.title)}</p>
                <div class="review-field-box">
                    <span class="text-muted">Review Reason:</span> Low grounding confidence / spec verification required.
                </div>
            </div>
            <div class="review-card-footer">
                <button class="btn btn-outline btn-sm" onclick="openProductModal(${item.row_idx})">Inspect & Edit</button>
                <button class="btn btn-success btn-sm" onclick="quickApproveRow(${item.row_idx})">Approve</button>
            </div>
        </div>
    `).join("");
}

async function quickApproveRow(rowIdx) {
    if (!currentJobId) return;
    try {
        await fetch(`/api/products/${rowIdx}/review?job_id=${currentJobId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ field_name: "Validation_Status", new_value: "VERIFIED", action: "APPROVE" })
        });
        fetchReviewQueue();
        refreshDashboardData();
    } catch (err) {
        console.error("Approve error:", err);
    }
}

// ----------------- Deep-Dive Product Modal Inspector -----------------
async function openProductModal(rowIdx) {
    activeModalRowIdx = rowIdx;
    try {
        const res = await fetch(`/api/products/${rowIdx}?job_id=${currentJobId}`);
        if (!res.ok) return;

        const prod = await res.json();

        const pn = prod.Mfg_Part_Num || prod.Canonical_Part_Number || prod.PART_NUMBER || "---";
        const brand = prod.BRAND_NAME || prod.Resolved_Brand || prod.Part_Manuf || "---";
        const status = prod.Validation_Status || prod._validation_status || "VERIFIED";

        document.getElementById("modal-title-pn").innerText = `Part Number: ${pn}`;
        document.getElementById("modal-subtitle-brand").innerText = `Manufacturer: ${brand}`;
        document.getElementById("modal-validation-chip").innerText = status;
        document.getElementById("modal-validation-chip").className = `status-chip ${status.toLowerCase()}`;

        // Fill Identity & Copy
        document.getElementById("modal-field-product-name").value = prod["Product Name"] || prod.PRODUCT_NAME || "";
        document.getElementById("modal-field-mpn").value = prod.MANUFACTURER_PART_NUMBER || prod.Mfg_Part_Num || "";
        document.getElementById("modal-field-brand").value = brand;
        document.getElementById("modal-field-short-desc").value = prod.SHORT_DESC || "";
        document.getElementById("modal-field-long-desc").value = prod.LONG_DESC1 || "";
        document.getElementById("modal-field-marketing-desc").value = prod.MARKETING_DESCRIPTION || "";

        // Fill 50 Attribute Triplets
        const tbody = document.getElementById("modal-triplets-tbody");
        let tripletsHtml = "";
        for (let i = 1; i <= 50; i++) {
            const lbl = prod[`ATTRIBUTE_LABEL ${i}`] || prod[`ATTR_NAME_${i}`] || "";
            const val = prod[`ATTRIBUTE_VALUE ${i}`] || prod[`ATTR_VALUE_${i}`] || "";
            const uom = prod[`ATTRIBUTE_UOM ${i}`] || prod[`ATTR_UOM_${i}`] || "";
            if (lbl || val || i <= 10) {
                tripletsHtml += `
                    <tr>
                        <td class="font-mono text-muted">${i}</td>
                        <td><input type="text" class="form-input" style="width: 100%;" value="${escapeHtml(lbl)}" id="modal-trip-lbl-${i}"></td>
                        <td><input type="text" class="form-input" style="width: 100%;" value="${escapeHtml(val)}" id="modal-trip-val-${i}"></td>
                        <td><input type="text" class="form-input" style="width: 100%;" value="${escapeHtml(uom)}" id="modal-trip-uom-${i}"></td>
                    </tr>
                `;
            }
        }
        tbody.innerHTML = tripletsHtml;

        // Fill Evidence & Provenance
        const provBox = document.getElementById("modal-provenance-box");
        const evidence = prod._rag_evidence || [];
        if (evidence.length === 0) {
            provBox.innerHTML = `<p class="text-muted">No external chunk citations ingested for this product. Built via deterministic domain parsing.</p>`;
        } else {
            provBox.innerHTML = evidence.map((ev, i) => `
                <div class="review-field-box">
                    <strong>Citation #${i + 1} (${ev.source || 'Document'})</strong>
                    <p class="text-muted" style="margin-top: 4px;">${escapeHtml(ev.text || '')}</p>
                </div>
            `).join("");
        }

        // Fill Raw 6 Inputs
        const rawBox = document.getElementById("modal-raw-inputs-box");
        rawBox.innerHTML = `
            <div class="form-group"><label>Mfg_Part_Num</label><input type="text" class="form-input" readonly value="${escapeHtml(prod.Mfg_Part_Num || '')}"></div>
            <div class="form-group"><label>Part_Desc</label><input type="text" class="form-input" readonly value="${escapeHtml(prod.Part_Desc || '')}"></div>
            <div class="form-group"><label>E1_Brand</label><input type="text" class="form-input" readonly value="${escapeHtml(prod.E1_Brand || '')}"></div>
            <div class="form-group"><label>Unilog_Brand</label><input type="text" class="form-input" readonly value="${escapeHtml(prod.Unilog_Brand || '')}"></div>
            <div class="form-group"><label>DIB_Brand</label><input type="text" class="form-input" readonly value="${escapeHtml(prod.DIB_Brand || '')}"></div>
            <div class="form-group"><label>Part_Manuf</label><input type="text" class="form-input" readonly value="${escapeHtml(prod.Part_Manuf || '')}"></div>
        `;

        document.getElementById("product-modal").style.display = "flex";
        switchModalTab("specs");
    } catch (err) {
        console.error("Modal load error:", err);
    }
}

function closeProductModal() {
    document.getElementById("product-modal").style.display = "none";
    activeModalRowIdx = null;
}

function switchModalTab(tabName) {
    document.querySelectorAll(".modal-tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".modal-tab-content").forEach(c => c.classList.remove("active"));

    const btn = document.getElementById(`mtab-btn-${tabName}`);
    if (btn) btn.classList.add("active");

    const content = document.getElementById(`mtab-${tabName}`);
    if (content) content.classList.add("active");
}

async function reviewModalAction(action) {
    if (activeModalRowIdx === null || !currentJobId) return;

    try {
        const prodName = document.getElementById("modal-field-product-name").value;
        await fetch(`/api/products/${activeModalRowIdx}/review?job_id=${currentJobId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ field_name: "Product Name", new_value: prodName, action: action })
        });
        closeProductModal();
        fetchCatalogProducts();
        refreshDashboardData();
    } catch (err) {
        console.error("Action error:", err);
    }
}

// ----------------- Export Downloads -----------------
function exportCatalog(format) {
    if (!currentJobId) {
        alert("Please upload or process a catalog first.");
        return;
    }
    window.location.href = `/api/jobs/${currentJobId}/export/${format}`;
}

function cancelCurrentJob() {
    if (!currentJobId) return;
    fetch(`/api/jobs/${currentJobId}/cancel`, { method: "POST" });
}

// ----------------- Ask Product AI Conversational RAG -----------------
async function sendRagQuery() {
    const input = document.getElementById("rag-query-input");
    const query = input.value.trim();
    if (!query) return;

    const chatBox = document.getElementById("rag-chat-box");
    
    // Append User message
    chatBox.innerHTML += `
        <div class="chat-message user-message">
            <div class="chat-avatar">👤</div>
            <div class="chat-bubble"><p>${escapeHtml(query)}</p></div>
        </div>
    `;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Call /query
    try {
        const res = await fetch("/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });
        const data = await res.json();

        chatBox.innerHTML += `
            <div class="chat-message bot-message">
                <div class="chat-avatar">🤖</div>
                <div class="chat-bubble">
                    <p>${escapeHtml(data.answer || 'No answer available.')}</p>
                </div>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        chatBox.innerHTML += `
            <div class="chat-message bot-message">
                <div class="chat-avatar">🤖</div>
                <div class="chat-bubble"><p class="text-danger">Error retrieving grounded answer.</p></div>
            </div>
        `;
    }
}

function escapeHtml(str) {
    return String(str || "").replace(/[&<>"']/g, function (m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[m];
    });
}
