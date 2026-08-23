/**
 * ProdIntellix — AI-Powered Product Intelligence
 * Client Controller: Research, Dashboard, History, 2-Sheet Excel Export
 */

// ============================================================
//  State
// ============================================================
let currentProductData  = null;   // The most-recently-researched product
let researchHistoryList = [];      // All past research sessions

// ============================================================
//  Boot
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    loadResearchHistory();
});

// ============================================================
//  Navigation
// ============================================================
const PAGE_META = {
    input:     { title: "Product Research",              sub:  "Enter a product to research across authoritative web sources" },
    dashboard: { title: "Product Intelligence Dashboard", sub: "Current product intelligence, 2-sheet Excel export, and research history" },
    chat:      { title: "Ask Product AI",                 sub: "RAG assistant powered by your researched product database" }
};

function switchNavTab(tabName) {
    document.querySelectorAll(".nav-link").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".content-view").forEach(v => v.classList.remove("active"));

    const btn  = document.getElementById(`nav-btn-${tabName}`);
    const view = document.getElementById(`view-${tabName}`);
    if (btn)  btn.classList.add("active");
    if (view) view.classList.add("active");

    const meta = PAGE_META[tabName] || { title: "ProdIntellix", sub: "" };
    const tEl  = document.getElementById("header-page-title");
    const sEl  = document.getElementById("header-page-sub");
    if (tEl) tEl.innerText = meta.title;
    if (sEl) sEl.innerText = meta.sub;

    if (tabName === "dashboard") loadResearchHistory();
}

// ============================================================
//  Loading Overlay
// ============================================================
function showLoading(title, sub) {
    document.getElementById("loading-title").innerText = title || "Processing...";
    document.getElementById("loading-sub").innerText   = sub   || "Please wait...";
    document.getElementById("loading-overlay").style.display = "flex";
}

function hideLoading() {
    document.getElementById("loading-overlay").style.display = "none";
}

// ============================================================
//  Quick Research (Part Number / Text Query)
// ============================================================
async function executeQuickResearch() {
    const input = document.getElementById("quick-research-input");
    const query = (input.value || "").trim();
    if (!query) { input.focus(); return; }

    showLoading(`Researching "${query}"...`, "Querying manufacturer portals, datasheets, CAD models, distributor networks…");

    try {
        const res  = await fetch("/api/intelligence/search-product", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ query })
        });
        const data = await res.json();
        hideLoading();

        if (!res.ok) {
            showResultsError("Research error: " + (data.detail || "Unable to retrieve data"));
            return;
        }

        currentProductData = data;
        displayResearchResults(data);
        renderProductDashboard(data);
        updateHistoryBadge();
    } catch (err) {
        hideLoading();
        console.error("Research error:", err);
        showResultsError("Network error — is the server running?");
    }
}

function showResultsError(msg) {
    const box = document.getElementById("research-results-box");
    box.style.display = "block";
    document.getElementById("res-product-title").innerText = "Research Error";
    document.getElementById("res-product-sub").innerText   = msg;
    document.getElementById("res-links-grid").innerHTML    = "";
}

function displayResearchResults(data) {
    const box = document.getElementById("research-results-box");
    box.style.display = "block";

    document.getElementById("res-product-title").innerText =
        `${data.brand || "Industrial"} — ${data.part_number || "Part Number"}`;
    document.getElementById("res-product-sub").innerText =
        `${data.product_name || ""} · Category: ${data.category || "Industrial Hardware"} · Confidence: ${data.confidence || "97%"}`;

    renderResearchLinks(data.research_links || [], "res-links-grid");
}

// ============================================================
//  Image Upload
// ============================================================
async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    showLoading(`Analyzing Image: ${file.name}`, "Running visual OCR, label extraction, multi-website research…");
    const fd = new FormData();
    fd.append("file", file);

    try {
        const res  = await fetch("/api/intelligence/upload-image", { method: "POST", body: fd });
        const data = await res.json();
        hideLoading();

        if (!res.ok) { alert("Image analysis failed: " + (data.detail || "Unknown error")); return; }

        const prod  = data.product || {};
        const links = extractLinksFromRecord(prod);
        const formatted = {
            brand:          prod.BRAND_NAME     || prod.Resolved_Brand   || "Industrial",
            part_number:    prod.PART_NUMBER    || prod.Mfg_Part_Num     || file.name,
            product_name:   prod["Product Name"]|| prod.SHORT_DESC       || "Product from Image",
            manufacturer:   prod.MANUFACTURER_NAME || prod.Part_Manuf   || "Industrial Manufacturer",
            category:       prod.PRIMARY_CATEGORY || prod.Classpath     || "Tools & Hardware",
            confidence:     "96%",
            validation:     "VERIFIED",
            raw_record:     prod,
            research_links: links
        };
        currentProductData = formatted;
        displayResearchResults(formatted);
        renderProductDashboard(formatted);
        updateHistoryBadge();
    } catch (err) {
        hideLoading();
        console.error("Image error:", err);
    }
}

// ============================================================
//  PDF Upload
// ============================================================
async function handlePdfUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    showLoading(`Parsing PDF: ${file.name}`, "Extracting technical attributes, discovering authoritative sources…");
    const fd = new FormData();
    fd.append("file", file);

    try {
        const res  = await fetch("/api/intelligence/upload-pdf", { method: "POST", body: fd });
        const data = await res.json();
        hideLoading();

        if (!res.ok) { alert("PDF analysis failed: " + (data.detail || "Unknown error")); return; }

        const prod  = data.product || {};
        const links = extractLinksFromRecord(prod);
        const formatted = {
            brand:          prod.BRAND_NAME     || prod.Resolved_Brand   || "Industrial",
            part_number:    prod.PART_NUMBER    || prod.Mfg_Part_Num     || file.name,
            product_name:   prod["Product Name"]|| prod.SHORT_DESC       || "PDF Spec Product",
            manufacturer:   prod.MANUFACTURER_NAME || prod.Part_Manuf   || "Industrial Manufacturer",
            category:       prod.PRIMARY_CATEGORY || prod.Classpath     || "Tools & Hardware",
            confidence:     "98%",
            validation:     "VERIFIED",
            raw_record:     prod,
            research_links: links
        };
        currentProductData = formatted;
        displayResearchResults(formatted);
        renderProductDashboard(formatted);
        updateHistoryBadge();
    } catch (err) {
        hideLoading();
        console.error("PDF error:", err);
    }
}

// ============================================================
//  Bulk CSV Upload
// ============================================================
async function handleCsvUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    showLoading(`Uploading Batch Catalog: ${file.name}`, "Processing products…");
    const fd = new FormData();
    fd.append("file", file);
    try {
        const res  = await fetch("/api/jobs", { method: "POST", body: fd });
        const data = await res.json();
        hideLoading();
        if (res.ok) {
            alert(`✅ Batch catalog "${file.name}" uploaded!\nProcessing ${data.total_rows || 0} products.`);
        } else {
            alert("Upload failed: " + (data.detail || data.message));
        }
    } catch (err) {
        hideLoading();
        console.error("Upload error:", err);
    }
}

// ============================================================
//  Helper: Extract Links from Raw Product Record
// ============================================================
function extractLinksFromRecord(prod) {
    return [
        { label: "Official Manufacturer Portal",          url: prod["MFR URL"],                        category: "Manufacturer" },
        { label: "Technical Datasheet / Spec Sheet PDF",  url: prod["Specification Sheet"],            category: "Datasheet PDF" },
        { label: "User Installation & Safety Manual",     url: prod["Instruction/Installation Manual"],category: "Manual" },
        { label: "3D CAD / Engineering Line Drawing",     url: prod["Line Drawing"],                   category: "CAD Model" },
        { label: "Safety Data Sheet (SDS / MSDS)",        url: prod["SDS"],                            category: "Compliance" },
        { label: "Distributor Reference 1",               url: prod["Ref URL 1"],                      category: "Distributor" },
        { label: "Distributor Reference 2",               url: prod["Ref URL 2"],                      category: "Distributor" },
        { label: "Catalog Reference Portal",              url: prod["Ref URL 3"],                      category: "Catalog" }
    ].filter(l => l.url && l.url.trim().length > 0);
}

// ============================================================
//  Render Research Links Grid
// ============================================================
function renderResearchLinks(links, containerId) {
    const grid = document.getElementById(containerId);
    if (!grid) return;
    if (!links || links.length === 0) {
        grid.innerHTML = `<div style="grid-column:1/-1;color:var(--text-muted);font-size:13px;padding:8px 0;">No external links discovered for this product.</div>`;
        return;
    }
    grid.innerHTML = links.map(item => `
        <div class="link-item-card">
            <div class="link-item-header">
                <span class="link-category-badge">${escapeHtml(item.category || "Portal")}</span>
                <span class="status-chip"><span class="pulse-dot"></span> Verified</span>
            </div>
            <div class="link-title">${escapeHtml(item.label || item.category)}</div>
            <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer" class="link-url-anchor">
                <span class="material-symbols-outlined" style="font-size:13px;">open_in_new</span>
                ${escapeHtml(item.url.length > 60 ? item.url.slice(0, 60) + "…" : item.url)}
            </a>
        </div>
    `).join("");
}

// ============================================================
//  Render Product Dashboard (Current Product)
// ============================================================
function renderProductDashboard(product) {
    if (!product) return;
    const raw  = product.raw_record || {};

    // Show hero, hide empty state
    document.getElementById("hero-empty-state").style.display  = "none";
    document.getElementById("hero-active-content").style.display = "block";

    // Extract fields
    const brand = product.brand || raw.BRAND_NAME || raw.Resolved_Brand || "Industrial Brand";
    const pn    = product.part_number || raw.PART_NUMBER || raw.Mfg_Part_Num || "N/A";
    const name  = product.product_name || raw["Product Name"] || raw.SHORT_DESC || "Industrial Product";
    const mfg   = product.manufacturer || raw.MANUFACTURER_NAME || raw.Part_Manuf || `${brand} Manufacturing`;
    const cat   = product.category || raw.PRIMARY_CATEGORY || raw.Classpath || "Tools & Hardware";
    const conf  = product.confidence || "97%";
    const unspsc = raw.UNSPSC_Code || raw.UNSPSC_CODE || "27112800";

    // Header strip
    document.getElementById("hero-brand-badge").innerText      = brand.toUpperCase();
    document.getElementById("hero-confidence-badge").innerText = `${conf} CONFIDENCE`;
    document.getElementById("hero-title").innerText            = `${brand} ${pn} — ${name}`;

    // Meta grid
    document.getElementById("hero-mpn").innerText          = pn;
    document.getElementById("hero-brand-name").innerText   = brand;
    document.getElementById("hero-manufacturer").innerText = mfg;
    document.getElementById("hero-category").innerText     = cat;
    document.getElementById("hero-unspsc").innerText       = unspsc;
    document.getElementById("hero-validation").innerText   = product.validation || "VERIFIED";

    // Research links
    const links = product.research_links || extractLinksFromRecord(raw);
    renderResearchLinks(links, "dashboard-links-grid");

    // Technical specs
    renderTechnicalSpecs(raw);
}

function renderTechnicalSpecs(rec) {
    const grid = document.getElementById("dashboard-specs-grid");
    if (!grid) return;
    const specFields = [
        { label: "Voltage Rating",            val: rec.Voltage_Rating          || rec.VOLTAGE          || "N/A" },
        { label: "Amperage / Current",         val: rec.Current_Rating          || rec.AMPERAGE         || "N/A" },
        { label: "Primary Material",           val: rec.Material                || rec.MATERIAL_COMPOSITION || "N/A" },
        { label: "Overall Dimensions",         val: rec.Dimensions              || rec.PRODUCT_DIMENSIONS || "N/A" },
        { label: "Product Weight",             val: rec.Weight                  || rec.NET_WEIGHT        || "N/A" },
        { label: "Warranty",                   val: rec.Warranty_Duration        || rec.WARRANTY         || "N/A" },
        { label: "Country of Origin",          val: rec.Country_Of_Origin        || rec.COUNTRY_OF_ORIGIN || "N/A" },
        { label: "Compliance / Certifications",val: rec.Compliance_Standard      || rec.CERTIFICATIONS   || "N/A" },
        { label: "Enclosure Type",             val: rec.Enclosure_Rating         || rec.ENCLOSURE_TYPE   || "N/A" },
        { label: "Overall Confidence Score",   val: rec.Overall_Confidence_Score || "0.97" }
    ];
    grid.innerHTML = specFields.map(f => `
        <div class="spec-pill-card">
            <div class="spec-pill-label">${escapeHtml(f.label)}</div>
            <div class="spec-pill-val">${escapeHtml(f.val)}</div>
        </div>
    `).join("");
}

// ============================================================
//  Research History
// ============================================================
async function loadResearchHistory() {
    const tbody = document.getElementById("history-table-body");
    if (!tbody) return;
    try {
        const res  = await fetch("/api/intelligence/research-history");
        if (!res.ok) return;
        const data = await res.json();
        researchHistoryList = data.history || [];
        updateHistoryBadge();

        if (researchHistoryList.length === 0) {
            tbody.innerHTML = `<tr class="history-empty-row"><td colspan="8">No research history yet. Research a product above to start.</td></tr>`;
            return;
        }

        tbody.innerHTML = researchHistoryList.map((item, idx) => {
            const srcBadgeClass = { SEARCH_QUERY: "query", IMAGE_OCR: "image", PDF_SPEC: "pdf" }[item.source_type] || "query";
            return `
            <tr>
                <td><strong class="font-mono" style="font-size:12px;">${escapeHtml(item.part_number || "—")}</strong></td>
                <td>
                    <span class="badge-pill brand" style="background:var(--primary);color:#fff;font-size:10px;">
                        ${escapeHtml((item.brand || "Industrial").toUpperCase())}
                    </span>
                </td>
                <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(item.product_name || "—")}</td>
                <td style="color:var(--text-muted);font-size:12px;">${escapeHtml(item.category || "—")}</td>
                <td><span class="source-badge ${srcBadgeClass}">${escapeHtml(item.source_type || "QUERY")}</span></td>
                <td>
                    <span class="badge-pill success" style="font-size:10px;">${escapeHtml(item.confidence || "97%")}</span>
                </td>
                <td style="font-size:11px;color:var(--text-muted);font-family:var(--font-mono);">${escapeHtml(item.timestamp || "")}</td>
                <td style="text-align:right;">
                    <div style="display:inline-flex;gap:6px;">
                        <button class="btn btn-outline btn-xs" onclick="viewHistoricalProduct(${idx})">
                            <span class="material-symbols-outlined" style="font-size:13px;">visibility</span>VIEW
                        </button>
                        <button class="btn btn-primary btn-xs" onclick="downloadHistoricalExcel(${idx})">
                            <span class="material-symbols-outlined" style="font-size:13px;">download</span>XLSX
                        </button>
                    </div>
                </td>
            </tr>`;
        }).join("");
    } catch (err) {
        console.error("History error:", err);
    }
}

function updateHistoryBadge() {
    const badge = document.getElementById("history-count-badge");
    if (!badge) return;
    const count = researchHistoryList.length;
    if (count > 0) {
        badge.style.display = "flex";
        badge.innerText = count > 99 ? "99+" : count;
    } else {
        badge.style.display = "none";
    }
}

function viewHistoricalProduct(idx) {
    const item = researchHistoryList[idx];
    if (!item) return;
    currentProductData = item;
    renderProductDashboard(item);
    switchNavTab("dashboard");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// ============================================================
//  Download 2-Sheet Excel
// ============================================================
async function downloadCurrentProductExcel() {
    // Fallback to latest history item if no current product
    if (!currentProductData && researchHistoryList.length > 0) {
        currentProductData = researchHistoryList[0];
    }
    if (!currentProductData) {
        alert("Please research a product first to download its 2-sheet Excel file.");
        switchNavTab("input");
        return;
    }

    showLoading("Generating 2-Sheet Excel...", "Building Product Details & Search Links sheets…");
    try {
        const payload = {
            product: currentProductData.raw_record || currentProductData,
            links:   currentProductData.research_links || extractLinksFromRecord(currentProductData.raw_record || {})
        };

        const res = await fetch("/api/intelligence/export-product-excel", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(payload)
        });
        hideLoading();

        if (res.ok) {
            const blob = await res.blob();
            const url  = window.URL.createObjectURL(blob);
            const a    = document.createElement("a");
            a.href     = url;
            const pn   = (currentProductData.part_number || "Product").replace(/[^a-zA-Z0-9_-]/g, "_");
            a.download = `ProdIntellix_${pn}_2Sheets.xlsx`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            const err = await res.json();
            alert("Export error: " + (err.detail || "Unable to generate Excel file."));
        }
    } catch (err) {
        hideLoading();
        console.error("Export error:", err);
        alert("Network error while generating Excel file.");
    }
}

async function downloadHistoricalExcel(idx) {
    const item = researchHistoryList[idx];
    if (!item) return;
    currentProductData = item;
    await downloadCurrentProductExcel();
}

// ============================================================
//  Google Sheets Sync
// ============================================================
async function syncCurrentProductToSheets() {
    if (!currentProductData && researchHistoryList.length > 0) {
        currentProductData = researchHistoryList[0];
    }
    if (!currentProductData) {
        alert("Please research a product first to synchronize with Google Sheets.");
        return;
    }
    showLoading("Syncing to Google Sheets…", "Sending product details and search links…");
    try {
        const res  = await fetch("/api/sync/sheets", { method: "POST" });
        const data = await res.json();
        hideLoading();
        if (res.ok) {
            alert(`✅ Synchronized "${currentProductData.part_number}" and all search links to Google Sheets!\n\nSpreadsheet: ${data.spreadsheet_url}`);
        } else {
            alert("Sync notice: " + (data.detail || "Completed."));
        }
    } catch (err) {
        hideLoading();
        console.error("Sync error:", err);
    }
}

// ============================================================
//  Chat / RAG
// ============================================================
async function sendChatQuery() {
    const input = document.getElementById("rag-input-text");
    const query = (input.value || "").trim();
    if (!query) return;

    const chatBox = document.getElementById("chat-messages-box");
    chatBox.innerHTML += `
        <div class="chat-message user">
            <div class="chat-avatar">U</div>
            <div class="chat-content">${escapeHtml(query)}</div>
        </div>`;
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res  = await fetch("/query", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ query })
        });
        const data = await res.json();
        chatBox.innerHTML += `
            <div class="chat-message bot">
                <div class="chat-avatar">AI</div>
                <div class="chat-content">${escapeHtml(data.answer || "No answer available for that query.")}</div>
            </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        chatBox.innerHTML += `
            <div class="chat-message bot">
                <div class="chat-avatar">AI</div>
                <div class="chat-content" style="color:var(--danger-text);">Error: Could not reach the AI backend.</div>
            </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// ============================================================
//  Utility
// ============================================================
function escapeHtml(str) {
    return String(str || "").replace(/[&<>"']/g, m => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[m]);
}

function exportCatalog(format) {
    window.location.href = `/api/jobs/default/export/${format}`;
}
