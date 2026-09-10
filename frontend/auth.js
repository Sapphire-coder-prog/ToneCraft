// ==== AUTH (Clerk) ====

let clerkReady = false;

async function initAuth() {
    if (clerkReady) return;

    // Load Clerk UI bundle
    await new Promise((resolve, reject) => {
        const uiScript = document.createElement("script");

        uiScript.src =
            `https://${CONFIG.CLERK_FRONTEND_API}/npm/@clerk/ui@1/dist/ui.browser.js`;

        uiScript.async = true;
        uiScript.crossOrigin = "anonymous";

        uiScript.onload = resolve;
        uiScript.onerror = () =>
            reject(new Error("Could not load Clerk UI. Check CLERK_FRONTEND_API."));

        document.head.appendChild(uiScript);
    });

    // Load ClerkJS
    await new Promise((resolve, reject) => {
        const clerkScript = document.createElement("script");

        clerkScript.src =
            `https://${CONFIG.CLERK_FRONTEND_API}/npm/@clerk/clerk-js@6/dist/clerk.browser.js`;

        clerkScript.async = true;
        clerkScript.crossOrigin = "anonymous";
        clerkScript.setAttribute(
            "data-clerk-publishable-key",
            CONFIG.CLERK_PUBLISHABLE_KEY
        );

        clerkScript.onload = resolve;
        clerkScript.onerror = () =>
            reject(new Error("Could not load ClerkJS. Check config.js."));

        document.head.appendChild(clerkScript);
    });

    // Initialize Clerk
    await window.Clerk.load({
        ui: {
            ClerkUI: window.__internal_ClerkUICtor,
        },
    });

    clerkReady = true;
}

function isSignedIn() {
    return !!(window.Clerk && window.Clerk.isSignedIn);
}

async function getAuthToken() {
    if (!isSignedIn()) return null;

    return await window.Clerk.session.getToken();
}

function mountSignIn(elementId) {
    window.Clerk.mountSignIn(
        document.getElementById(elementId)
    );
}

function mountUserButton(elementId) {
    window.Clerk.mountUserButton(
        document.getElementById(elementId)
    );
}

function requireAuthOrRedirect() {
    if (!isSignedIn()) {
        window.location.href = "index.html";
    }
}
