/**
 * Dashboard & Telemetry Controller
 */
async function loadDashboardMetrics() {
    try {
        const res = await fetch("/api/jobs");
        if (res.ok) {
            const data = await res.json();
            if (data.jobs && data.jobs.length > 0) {
                const el = document.getElementById("dash-total-items");
                if (el) el.innerText = data.jobs[0].total_rows || 350;
            }
        }
    } catch (e) {
        console.warn("Telemetry notice:", e);
    }
}
document.addEventListener("DOMContentLoaded", loadDashboardMetrics);
