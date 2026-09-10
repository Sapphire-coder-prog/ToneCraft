// ==== SHARED UI / ANIMATION HELPERS ====
// Used by both index.html and rehearsal.html.

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ---- Cursor-reactive particle blob (hero background) ----
function initParticleField(containerId, count = 26) {
    const field = document.getElementById(containerId);
    if (!field || reducedMotion) return;

    const dots = [];
    for (let i = 0; i < count; i++) {
        const dot = document.createElement("span");
        dot.className = "particle-dot";
        field.appendChild(dot);
        dots.push(dot);
    }

    field.addEventListener("mousemove", (e) => {
        const rect = field.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        dots.forEach((dot, i) => {
            anime({
                targets: dot,
                translateX: x + Math.sin(i) * 40,
                translateY: y + Math.cos(i) * 40,
                opacity: [0.15, 0.7],
                duration: 900,
                delay: i * 12,
                easing: "easeOutElastic(1, .6)",
            });
        });
    });
}

// ---- Staggered heading entrance ----
function staggerReveal(selector) {
    if (reducedMotion) return;
    anime({
        targets: selector,
        translateY: [24, 0],
        opacity: [0, 1],
        delay: anime.stagger(80),
        duration: 900,
        easing: "easeOutExpo",
    });
}

// ---- Scroll-triggered reveals for any element with class "reveal" ----
function setupScrollReveals() {
    const targets = document.querySelectorAll(".reveal");
    if (!targets.length) return;

    if (reducedMotion) {
        targets.forEach((t) => t.classList.add("revealed"));
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("revealed");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15 }
    );

    targets.forEach((t) => observer.observe(t));
}

// ---- Waveform bars, used while audio is playing/recording ----
function startWaveform(containerEl) {
    const bars = containerEl.querySelectorAll(".wave-bar");
    if (reducedMotion) return () => { };

    const timeline = anime({
        targets: bars,
        scaleY: () => anime.random(3, 10) / 10,
        duration: 400,
        direction: "alternate",
        loop: true,
        delay: anime.stagger(60),
        easing: "easeInOutSine",
    });
    return () => timeline.pause();
}

// ---- Small toast for errors / success messages ----
function showToast(message, type = "error") {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = `toast toast-${type} show`;
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove("show"), 4000);
}

// ---- Button micro-interaction (scale + accent glow on press) ----
function attachButtonMicroInteractions() {
    if (reducedMotion) return;
    document.querySelectorAll("button").forEach((btn) => {
        btn.addEventListener("mousedown", () => {
            anime({ targets: btn, scale: 0.96, duration: 120, easing: "easeOutQuad" });
        });
        btn.addEventListener("mouseup", () => {
            anime({ targets: btn, scale: 1, duration: 220, easing: "easeOutElastic(1, .6)" });
        });
        btn.addEventListener("mouseleave", () => {
            anime({ targets: btn, scale: 1, duration: 220, easing: "easeOutElastic(1, .6)" });
        });
    });
}