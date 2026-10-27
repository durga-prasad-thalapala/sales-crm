const API_BASE_URL = "http://127.0.0.1:8000/api";

let refreshPromise = null;

async function refreshAccessToken() {
    const refreshToken = localStorage.getItem("refresh_token");

    if (!refreshToken) {
        throw new Error("Session expired. Please log in again.");
    }

    const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            refresh: refreshToken,
        }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || !data.access) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        throw new Error("Session expired. Please log in again.");
    }

    localStorage.setItem("access_token", data.access);

    if (data.refresh) {
        localStorage.setItem("refresh_token", data.refresh);
    }

    return data.access;
}

export async function apiRequest(endpoint, options = {}) {
    const sendRequest = async (token) => {
        return fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {}),
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
        });
    };

    let token = localStorage.getItem("access_token");
    let response = await sendRequest(token);

    if (response.status === 401 && token) {
        try {
            if (!refreshPromise) {
                refreshPromise = refreshAccessToken().finally(() => {
                    refreshPromise = null;
                });
            }

            token = await refreshPromise;
            response = await sendRequest(token);
        } catch {
            throw new Error("Session expired. Please log in again.");
        }
    }

    const text = await response.text();
    let data = null;

    if (text) {
        try {
            data = JSON.parse(text);
            } catch {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");

            if (window.location.pathname !== "/login") {
                window.location.href = "/login";
            }

            throw new Error("Session expired. Please log in again.");
        }
    }

    if (!response.ok) {
        throw new Error(
            data?.detail ||
            data?.message ||
            `Request failed with status ${response.status}`
        );
    }

    return data;
}