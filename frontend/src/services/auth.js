import { apiRequest } from "./api";

export async function login(username, password) {
    return apiRequest("/auth/login/", {
        method: "POST",
        body: JSON.stringify({
            username,
            password,
        }),
    });
}

export function saveAuthData(data) {
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
}

export function getAccessToken() {
    return localStorage.getItem("access_token");
}

export function isAuthenticated() {
    return Boolean(getAccessToken());
}

export function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
}