// ==== API COMMUNICATION ====
// Every function here talks to the FastAPI backend.
// Nothing in this file touches the DOM.

async function authHeaders(extra = {}) {
    const token = await getAuthToken();
    if (!token) throw new Error("You need to be signed in to do that.");
    return { Authorization: `Bearer ${token}`, ...extra };
}

async function handleResponse(res) {
    if (!res.ok) {
        let detail = res.statusText;
        try {
            const body = await res.json();
            detail = body.detail || detail;
        } catch (e) { }
        throw new Error(detail);
    }
    return res.json();
}

const api = {
    // GET /status
    async getStatus() {
        const res = await fetch(`${CONFIG.BACKEND_URL}/status`);
        return handleResponse(res);
    },

    // POST /scripts  -> { script_id, lines: [{line_id, text}] }
    async createScript(text) {
        const headers = await authHeaders({ "Content-Type": "application/json" });
        const res = await fetch(`${CONFIG.BACKEND_URL}/scripts`, {
            method: "POST",
            headers,
            body: JSON.stringify({ text }),
        });
        return handleResponse(res);
    },

    // POST /lines/{line_id}/tone -> { line_id, tone }
    async setTone(lineId, tone) {
        const headers = await authHeaders({ "Content-Type": "application/json" });
        const res = await fetch(`${CONFIG.BACKEND_URL}/lines/${lineId}/tone`, {
            method: "POST",
            headers,
            body: JSON.stringify({ tone }),
        });
        return handleResponse(res);
    },

    // POST /lines/{line_id}/generate -> { line_id, audio_url, prompt_used }
    async generateReference(lineId) {
        const headers = await authHeaders();
        const res = await fetch(`${CONFIG.BACKEND_URL}/lines/${lineId}/generate`, {
            method: "POST",
            headers,
        });
        return handleResponse(res);
    },

    // POST /lines/{line_id}/recording (multipart) -> { line_id, recording_url }
    async uploadRecording(lineId, blob) {
        const headers = await authHeaders(); // don't set Content-Type manually for FormData
        const formData = new FormData();
        formData.append("file", blob, "recording.webm");
        const res = await fetch(`${CONFIG.BACKEND_URL}/lines/${lineId}/recording`, {
            method: "POST",
            headers,
            body: formData,
        });
        return handleResponse(res);
    },

    // GET /lines/{line_id}/compare -> { line_id, tone, reference, user, comparison }
    async compare(lineId) {
        const headers = await authHeaders();
        const res = await fetch(`${CONFIG.BACKEND_URL}/lines/${lineId}/compare`, {
            headers,
        });
        return handleResponse(res);
    },

    // Turns "/audio/xxx.mp3" into a full playable URL.
    audioUrl(relativeUrl) {
        return `${CONFIG.BACKEND_URL}${relativeUrl}`;
    },
};

// ---- local cache of rehearsals, since the backend has no "list scripts" endpoint ----
const rehearsalCache = {
    save(scriptId, title, lines) {
        const all = rehearsalCache.getAll();
        all[scriptId] = { scriptId, title, lines, savedAt: Date.now() };
        localStorage.setItem("tonecraft_rehearsals", JSON.stringify(all));
    },
    getAll() {
        try {
            return JSON.parse(localStorage.getItem("tonecraft_rehearsals")) || {};
        } catch (e) {
            return {};
        }
    },
    get(scriptId) {
        return rehearsalCache.getAll()[scriptId] || null;
    },
};