// AI Product Intelligence & Document RAG Platform Client Controller

let currentJobId = null;
let jobPollInterval = null;
let currentCatalogPage = 1;
let currentTotalPages = 1;
let currentProductData = null;
let currentModalRowIdx = null;

// Document RAG State
let chatHistory = [];
let currentChatId = null;

// ----------------- View Navigation -----------------
function switchView(viewName) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));

    if (viewName === 'intelligence') {
        document.getElementById('tab-btn-intelligence').classList.add('active');
        document.getElementById('view-intelligence').classList.add('active');
    } else {
        document.getElementById('tab-btn-rag').classList.add('active');
        document.getElementById('view-rag').classList.add('active');
        refreshRagState();
    }
}

// ----------------- Product Intelligence Studio -----------------

// File Upload & Drag-Drop Setup
const dropZone = document.getElementById('catalog-drop-zone');
const fileInput = document.getElementById('catalog-file-input');

if (dropZone && fileInput) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--accent-cyan)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--border-color)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border-color)';
        if (e.dataTransfer.files.length > 0) {
            uploadCatalogFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadCatalogFile(e.target.files[0]);
        }
    });
}

async function uploadCatalogFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/intelligence/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            startJobTracking(data.job_id, data.filename, data.total_rows);
        } else {
            alert('Upload error: ' + (data.error || 'Failed to process file'));
        }
    } catch (err) {
        alert('Network error uploading file: ' + err.message);
    }
}

async function loadSampleDemo(rowCount) {
    try {
        const response = await fetch(`/api/intelligence/demo/load?rows=${rowCount}`, {
            method: 'POST'
        });

        const data = await response.json();
        if (response.ok) {
            startJobTracking(data.job_id, data.filename, data.total_rows);
        } else {
            alert('Error loading sample dataset: ' + (data.error || 'Failed'));
        }
    } catch (err) {
        alert('Network error: ' + err.message);
    }
}

function startJobTracking(jobId, filename, totalRows) {
    currentJobId = jobId;
    currentCatalogPage = 1;

    // Show Progress Panel & Table Section
    document.getElementById('job-progress-panel').style.display = 'block';
    document.getElementById('catalog-table-section').style.display = 'block';

    document.getElementById('job-filename').textContent = filename;
    document.getElementById('job-id-display').textContent = `Job: #${jobId}`;
    document.getElementById('total-count').textContent = totalRows;
    document.getElementById('kpi-total').textContent = totalRows;

    if (jobPollInterval) clearInterval(jobPollInterval);
    jobPollInterval = setInterval(pollJobStatus, 800);
    pollJobStatus();
}

async function pollJobStatus() {
    if (!currentJobId) return;

    try {
        const res = await fetch(`/api/intelligence/status/${currentJobId}`);
        if (!res.ok) return;

        const data = await res.json();
        
        // Update Progress Bar
        const percent = data.progress_percent || 0;
        document.getElementById('progress-percent').textContent = `${percent}%`;
        document.getElementById('progress-fill').style.width = `${percent}%`;
        document.getElementById('processed-count').textContent = data.processed_rows;
        document.getElementById('total-count').textContent = data.total_rows;

        // Update KPIs
        document.getElementById('kpi-total').textContent = data.total_rows;
        document.getElementById('kpi-confidence').textContent = `${(data.avg_confidence * 100).toFixed(1)}%`;
        document.getElementById('kpi-verified').textContent = data.verified_count || 0;
        document.getElementById('kpi-review').textContent = data.needs_review_count || 0;

        const chip = document.getElementById('job-status-chip');
        chip.textContent = data.status;
        if (data.status === 'COMPLETED') {
            chip.style.background = 'var(--accent-emerald)';
            chip.style.color = '#fff';
            document.getElementById('btn-export-csv').disabled = false;
            document.getElementById('btn-export-xlsx').disabled = false;
            clearInterval(jobPollInterval);
        } else if (data.status === 'RUNNING') {
            chip.style.background = 'var(--accent-cyan)';
            chip.style.color = '#0b0f19';
            if (data.processed_rows > 0) {
                document.getElementById('btn-export-csv').disabled = false;
                document.getElementById('btn-export-xlsx').disabled = false;
            }
        }

        fetchCatalogProducts();
    } catch (err) {
        console.error('Error polling status:', err);
    }
}

async function fetchCatalogProducts() {
    if (!currentJobId) return;

    const search = document.getElementById('catalog-search').value.trim();
    const brand = document.getElementById('brand-filter').value;
    const status = document.getElementById('status-filter').value;

    const url = `/api/intelligence/products/${currentJobId}?page=${currentCatalogPage}&page_size=15&search=${encodeURIComponent(search)}&brand=${encodeURIComponent(brand)}&status=${encodeURIComponent(status)}`;

    try {
        const res = await fetch(url);
        if (!res.ok) return;

        const data = await res.json();
        renderCatalogTable(data);
    } catch (err) {
        console.error('Error fetching catalog products:', err);
    }
}

function renderCatalogTable(data) {
    const tbody = document.getElementById('catalog-table-body');
    tbody.innerHTML = '';

    const products = data.products || [];
    currentTotalPages = data.total_pages || 1;

    if (products.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 24px;">No products match current filters</td></tr>`;
        updatePaginationUI(0, 0, 0);
        return;
    }

    products.forEach((p, index) => {
        const rowIdx = p._row_idx !== undefined ? p._row_idx : ((data.page - 1) * data.page_size + index);
        const tr = document.createElement('tr');

        const score = parseFloat(p.Overall_Confidence_Score || 0);
        const scorePct = Math.round(score * 100);
        const status = p.Validation_Status || 'PENDING';
        const statusClass = status.toLowerCase();

        const volt = p.Voltage_Rating ? `${p.Voltage_Rating}V` : '';
        const curr = p.Current_Rating ? `${p.Current_Rating}A` : '';
        const specSummary = [volt, curr].filter(Boolean).join(' / ') || 'Standard';

        tr.innerHTML = `
            <td style="color: var(--text-muted);">${rowIdx + 1}</td>
            <td><strong>${escapeHtml(p.Mfg_Part_Num || 'N/A')}</strong></td>
            <td><span class="highlight-cyan">${escapeHtml(p.Resolved_Brand || 'Unknown')}</span></td>
            <td style="max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(p.Product_Title || '')}">${escapeHtml(p.Product_Title || p.Part_Desc || '')}</td>
            <td><span style="font-size: 11px; color: var(--text-secondary);">${escapeHtml(p.Primary_Category || 'Industrial')}</span></td>
            <td><span style="font-family: var(--font-mono); font-size: 11px;">${specSummary}</span></td>
            <td>
                <div class="score-meter">
                    <span style="color: ${score >= 0.85 ? 'var(--accent-emerald)' : score >= 0.7 ? 'var(--accent-amber)' : 'var(--accent-rose)'};">${scorePct}%</span>
                </div>
            </td>
            <td>
                <span class="status-badge ${statusClass}">${status}</span>
            </td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="openProductModal(${rowIdx})">
                    Inspect 🔍
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    const start = (data.page - 1) * data.page_size + 1;
    const end = Math.min(data.page * data.page_size, data.total);
    updatePaginationUI(start, end, data.total);
}

function updatePaginationUI(start, end, total) {
    document.getElementById('pagination-info').textContent = `Showing ${start} to ${end} of ${total} records`;
    document.getElementById('current-page-num').textContent = currentCatalogPage;
    document.getElementById('btn-prev-page').disabled = currentCatalogPage <= 1;
    document.getElementById('btn-next-page').disabled = currentCatalogPage >= currentTotalPages;
}

function changeCatalogPage(delta) {
    currentCatalogPage += delta;
    if (currentCatalogPage < 1) currentCatalogPage = 1;
    if (currentCatalogPage > currentTotalPages) currentCatalogPage = currentTotalPages;
    fetchCatalogProducts();
}

function onCatalogFilterChange() {
    currentCatalogPage = 1;
    fetchCatalogProducts();
}

function exportCatalog(format) {
    if (!currentJobId) return;
    window.location.href = `/api/intelligence/export/${currentJobId}/${format}`;
}

// ----------------- Product Inspection Modal -----------------

async function openProductModal(rowIdx) {
    if (!currentJobId) return;
    currentModalRowIdx = rowIdx;

    try {
        const res = await fetch(`/api/intelligence/product/${currentJobId}/${rowIdx}`);
        if (!res.ok) return;

        const p = await res.json();
        currentProductData = p;

        // Modal Headers
        document.getElementById('modal-status-chip').textContent = p.Validation_Status || 'VERIFIED';
        document.getElementById('modal-product-title').textContent = p.Product_Title || p.Part_Desc || 'Product Details';
        document.getElementById('modal-product-sub').textContent = `Mfg Part Number: ${p.Mfg_Part_Num || 'N/A'} | Canonical: ${p.Canonical_Part_Number || 'N/A'}`;
        document.getElementById('modal-review-status').textContent = p.Review_Status || 'PENDING';

        // Tab 1: Specs & Copy
        document.getElementById('spec-canonical-pn').textContent = p.Canonical_Part_Number || p.Mfg_Part_Num || '---';
        document.getElementById('spec-brand').textContent = p.Resolved_Brand || '---';
        document.getElementById('spec-category').textContent = p.Category_Path || p.Primary_Category || '---';
        document.getElementById('spec-unspsc').textContent = `${p.UNSPSC_Code || '---'} (${p.UNSPSC_Title || ''})`;
        document.getElementById('spec-lifecycle').textContent = p.Lifecycle_Status || 'Active';
        document.getElementById('spec-voltage').textContent = p.Voltage_Rating ? `${p.Voltage_Rating} ${p.Voltage_UOM || 'V'}` : '---';
        document.getElementById('spec-current').textContent = p.Current_Rating ? `${p.Current_Rating} ${p.Current_UOM || 'A'}` : '---';
        document.getElementById('spec-mounting').textContent = p.Mounting_Type || '---';
        document.getElementById('spec-dims').textContent = `${p.Length || '0'} x ${p.Width || '0'} x ${p.Height || '0'} ${p.Dimension_UOM || 'IN'}`;
        document.getElementById('spec-weight').textContent = `${p.Weight || '0'} ${p.Weight_UOM || 'LBS'}`;

        document.getElementById('edit-product-title').value = p.Product_Title || '';
        document.getElementById('edit-short-desc').value = p.Short_Description || '';

        // 10 Bullets
        const bulletsContainer = document.getElementById('modal-feature-bullets');
        bulletsContainer.innerHTML = '';
        const ul = document.createElement('ul');
        for (let i = 1; i <= 10; i++) {
            const bText = p[`Feature_Bullet_${i}`];
            if (bText) {
                const li = document.createElement('li');
                li.textContent = bText;
                ul.appendChild(li);
            }
        }
        bulletsContainer.appendChild(ul);

        // Tab 2: 50 Attribute Triplets Matrix
        const tripletsTbody = document.getElementById('modal-triplets-tbody');
        tripletsTbody.innerHTML = '';
        for (let i = 1; i <= 50; i++) {
            const name = p[`Attribute_Name_${i}`] || '';
            const val = p[`Attribute_Value_${i}`] || '';
            const uom = p[`Attribute_UOM_${i}`] || '';

            if (name || val || i <= 15) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="color: var(--text-muted);">${i}</td>
                    <td><strong>${escapeHtml(name || `Attribute ${i}`)}</strong></td>
                    <td><input type="text" class="form-input" id="triplet-val-${i}" value="${escapeHtml(val)}" style="padding: 4px 8px; font-size: 12px;"></td>
                    <td><input type="text" class="form-input" id="triplet-uom-${i}" value="${escapeHtml(uom)}" style="width: 80px; padding: 4px 8px; font-size: 12px;"></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="saveTripletField(${i})">Save</button>
                    </td>
                `;
                tripletsTbody.appendChild(tr);
            }
        }

        // Tab 3: Provenance & Evidence
        const linksContainer = document.getElementById('modal-discovered-links');
        linksContainer.innerHTML = '';
        const linkFields = [
            ['Manufacturer Portal', p.Manufacturer_Product_URL],
            ['Spec Sheet / Datasheet', p.Spec_Sheet_URL],
            ['User Manual', p.User_Manual_URL],
            ['3D CAD Model', p.CAD_Drawing_URL],
            ['SDS / MSDS', p.SDS_MSDS_URL],
            ['Grainger Catalog', p.Distributor_URL_1],
            ['Radwell Reference', p.Distributor_URL_2],
            ['GlobalSpec Reference', p.Reference_Source_URL]
        ];

        linkFields.forEach(([label, url]) => {
            if (url) {
                const a = document.createElement('a');
                a.className = 'link-chip';
                a.href = url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                a.innerHTML = `<span>🔗</span> ${label}`;
                linksContainer.appendChild(a);
            }
        });

        // RAG Evidence
        const ragContainer = document.getElementById('modal-rag-evidence-list');
        ragContainer.innerHTML = '';
        const ragEvidence = p._rag_evidence || [];
        if (ragEvidence.length > 0) {
            ragEvidence.forEach(e => {
                const div = document.createElement('div');
                div.style.marginBottom = '10px';
                div.innerHTML = `<strong>${escapeHtml(e.source_title)}:</strong> <span class="text-muted">${escapeHtml(e.content_snippet)}</span>`;
                ragContainer.appendChild(div);
            });
        } else {
            ragContainer.innerHTML = '<span class="text-muted">No uploaded PDF/manual chunk matched this part number. Evidence derived from manufacturer portal and industrial catalog knowledge base.</span>';
        }

        // JSON Provenance Log
        try {
            const provLog = p.Provenance_Log ? JSON.parse(p.Provenance_Log) : [];
            document.getElementById('modal-provenance-json').textContent = JSON.stringify(provLog, null, 2);
        } catch {
            document.getElementById('modal-provenance-json').textContent = p.Provenance_Log || '{}';
        }

        // Tab 4: Raw Inputs Preservation
        const rawGrid = document.getElementById('modal-raw-inputs-grid');
        rawGrid.innerHTML = `
            <div class="raw-item"><span>Mfg_Part_Num (Original)</span><strong>${escapeHtml(p.Mfg_Part_Num || '')}</strong></div>
            <div class="raw-item"><span>Part_Desc (Original)</span><strong>${escapeHtml(p.Part_Desc || '')}</strong></div>
            <div class="raw-item"><span>E1_Brand (Original)</span><strong>${escapeHtml(p.E1_Brand || '')}</strong></div>
            <div class="raw-item"><span>Unilog_Brand (Original)</span><strong>${escapeHtml(p.Unilog_Brand || '')}</strong></div>
            <div class="raw-item"><span>DIB_Brand (Original)</span><strong>${escapeHtml(p.DIB_Brand || '')}</strong></div>
            <div class="raw-item"><span>Part_Manuf (Original)</span><strong>${escapeHtml(p.Part_Manuf || '')}</strong></div>
        `;

        switchModalTab('tab-overview');
        document.getElementById('product-modal').style.display = 'flex';
    } catch (err) {
        console.error('Error opening product modal:', err);
    }
}

function switchModalTab(tabId) {
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.modal-tab-content').forEach(c => c.classList.remove('active'));

    const tabBtn = Array.from(document.querySelectorAll('.modal-tab')).find(b => b.getAttribute('onclick')?.includes(tabId));
    if (tabBtn) tabBtn.classList.add('active');

    const content = document.getElementById(tabId);
    if (content) content.classList.add('active');
}

function closeProductModal() {
    document.getElementById('product-modal').style.display = 'none';
    currentModalRowIdx = null;
    currentProductData = null;
}

async function saveEditedField(fieldName, elementId) {
    if (!currentJobId || currentModalRowIdx === null) return;
    const newVal = document.getElementById(elementId).value;

    try {
        const res = await fetch(`/api/intelligence/product/${currentJobId}/${currentModalRowIdx}/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ field_name: fieldName, new_value: newVal })
        });

        if (res.ok) {
            document.getElementById('modal-review-status').textContent = 'EDITED';
            fetchCatalogProducts();
            alert(`Updated ${fieldName}!`);
        }
    } catch (err) {
        alert('Error updating field: ' + err.message);
    }
}

async function saveTripletField(tripletIdx) {
    if (!currentJobId || currentModalRowIdx === null) return;
    const val = document.getElementById(`triplet-val-${tripletIdx}`).value;
    const uom = document.getElementById(`triplet-uom-${tripletIdx}`).value;

    await fetch(`/api/intelligence/product/${currentJobId}/${currentModalRowIdx}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_name: `Attribute_Value_${tripletIdx}`, new_value: val })
    });

    await fetch(`/api/intelligence/product/${currentJobId}/${currentModalRowIdx}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_name: `Attribute_UOM_${tripletIdx}`, new_value: uom })
    });

    document.getElementById('modal-review-status').textContent = 'EDITED';
    fetchCatalogProducts();
    alert(`Updated Attribute Triplet #${tripletIdx}!`);
}

async function approveProductRecord() {
    if (!currentJobId || currentModalRowIdx === null) return;

    await fetch(`/api/intelligence/product/${currentJobId}/${currentModalRowIdx}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_name: 'Review_Status', new_value: 'APPROVED' })
    });

    await fetch(`/api/intelligence/product/${currentJobId}/${currentModalRowIdx}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_name: 'Validation_Status', new_value: 'VERIFIED' })
    });

    document.getElementById('modal-review-status').textContent = 'APPROVED';
    document.getElementById('modal-status-chip').textContent = 'VERIFIED';
    fetchCatalogProducts();
    setTimeout(closeProductModal, 400);
}

// ----------------- Document RAG Assistant Functions -----------------

const ragFileInput = document.getElementById('rag-file-input');
if (ragFileInput) {
    ragFileInput.addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append('file', file);

            const msgElem = document.getElementById('rag-upload-msg');
            msgElem.textContent = `Uploading & chunking ${file.name}...`;

            try {
                const res = await fetch('/upload', { method: 'POST', body: formData });
                const data = await res.json();
                msgElem.textContent = data.message || 'File uploaded!';
                setTimeout(refreshRagState, 1500);
            } catch (err) {
                msgElem.textContent = 'Upload error: ' + err.message;
            }
        }
    });
}

async function refreshRagState() {
    try {
        // Status & Chunks
        const statusRes = await fetch('/status');
        if (statusRes.ok) {
            const s = await statusRes.json();
            document.getElementById('rag-chunk-count').textContent = s.chunk_count || 0;
        }

        // Ingested Files
        const filesRes = await fetch('/files');
        if (filesRes.ok) {
            const files = await filesRes.json();
            const filesContainer = document.getElementById('rag-files-list');
            filesContainer.innerHTML = '';
            files.forEach(f => {
                const div = document.createElement('div');
                div.className = 'file-item';
                div.innerHTML = `<span>📄 ${escapeHtml(f)}</span>`;
                filesContainer.appendChild(div);
            });
        }

        // History
        const histRes = await fetch('/history');
        if (histRes.ok) {
            const chats = await histRes.json();
            const histContainer = document.getElementById('rag-history-list');
            histContainer.innerHTML = '';
            chats.forEach(c => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.textContent = c.title || 'Chat';
                div.onclick = () => loadChatHistory(c.id);
                histContainer.appendChild(div);
            });
        }
    } catch (err) {
        console.error('Error refreshing RAG state:', err);
    }
}

function startNewChat() {
    chatHistory = [];
    currentChatId = 'chat_' + Date.now();
    document.getElementById('rag-chat-messages').innerHTML = `
        <div class="empty-welcome">
            <div class="welcome-icon">💬</div>
            <h3>Product Knowledge Assistant</h3>
            <p class="text-muted">Ask questions about spec sheets, catalogs, wiring diagrams, and cross-references grounded in ChromaDB embeddings.</p>
        </div>
    `;
}

async function sendRagMessage() {
    const input = document.getElementById('rag-query-input');
    const query = input.value.trim();
    if (!query) return;

    input.value = '';
    const messagesContainer = document.getElementById('rag-chat-messages');

    // Remove empty welcome if present
    const empty = messagesContainer.querySelector('.empty-welcome');
    if (empty) empty.remove();

    // Append User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'chat-msg user';
    userDiv.textContent = query;
    messagesContainer.appendChild(userDiv);
    chatHistory.push({ role: 'user', content: query });

    // Assistant Loading
    const assistDiv = document.createElement('div');
    assistDiv.className = 'chat-msg assistant';
    assistDiv.textContent = 'Searching vector index and synthesizing answer...';
    messagesContainer.appendChild(assistDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const res = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, history: chatHistory })
        });

        const data = await res.json();
        assistDiv.innerHTML = escapeHtml(data.answer || 'No response found.');

        if (data.sources && data.sources.length > 0) {
            const srcDiv = document.createElement('div');
            srcDiv.style.marginTop = '8px';
            srcDiv.style.fontSize = '11px';
            srcDiv.style.color = 'var(--accent-cyan)';
            srcDiv.innerHTML = '<strong>Grounding Sources:</strong><br>' + 
                data.sources.map(s => `• ${escapeHtml(s.source)} (Chunk ${s.chunk_id})`).join('<br>');
            assistDiv.appendChild(srcDiv);
        }

        chatHistory.push({ role: 'assistant', content: data.answer || '' });

        // Save Chat
        if (!currentChatId) currentChatId = 'chat_' + Date.now();
        await fetch('/history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: currentChatId,
                title: query.slice(0, 30),
                messages: chatHistory
            })
        });
        refreshRagState();

    } catch (err) {
        assistDiv.textContent = 'Error querying RAG: ' + err.message;
    }
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function loadChatHistory(chatId) {
    try {
        const res = await fetch(`/history/${chatId}`);
        if (!res.ok) return;
        const chat = await res.json();
        currentChatId = chat.id;
        chatHistory = chat.messages || [];

        const container = document.getElementById('rag-chat-messages');
        container.innerHTML = '';

        chatHistory.forEach(msg => {
            const div = document.createElement('div');
            div.className = `chat-msg ${msg.role}`;
            div.textContent = msg.content;
            container.appendChild(div);
        });
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        console.error('Error loading chat:', err);
    }
}

// Utility
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Global Enter key handler for RAG query input
document.addEventListener('DOMContentLoaded', () => {
    const qInput = document.getElementById('rag-query-input');
    if (qInput) {
        qInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendRagMessage();
            }
        });
    }
});
