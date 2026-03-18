/** @odoo-module **/

import { registry } from "@web/core/registry";

const SESSION_KEY = "odoo_ai_assistant_session_v1";
const SCHEMA_VERSION = 1;
const MAX_MESSAGES = 50;
const MAX_BYTES = 100 * 1024; // 100 KB

export const aiChatService = {
    start(env) {
        function loadHistory() {
            try {
                const raw = sessionStorage.getItem(SESSION_KEY);
                if (!raw) {
                    return [];
                }
                const data = JSON.parse(raw);
                if (
                    !data ||
                    data.version !== SCHEMA_VERSION ||
                    !Array.isArray(data.messages)
                ) {
                    sessionStorage.removeItem(SESSION_KEY);
                    return [];
                }
                return data.messages;
            } catch {
                sessionStorage.removeItem(SESSION_KEY);
                return [];
            }
        }

        function saveHistory(messages) {
            try {
                let trimmed =
                    messages.length > MAX_MESSAGES
                        ? messages.slice(-MAX_MESSAGES)
                        : messages;

                let serialized = JSON.stringify({
                    version: SCHEMA_VERSION,
                    messages: trimmed,
                });

                while (trimmed.length > 1 && serialized.length > MAX_BYTES) {
                    trimmed = trimmed.slice(1);
                    serialized = JSON.stringify({
                        version: SCHEMA_VERSION,
                        messages: trimmed,
                    });
                }

                sessionStorage.setItem(SESSION_KEY, serialized);
                return trimmed;
            } catch {
                // QuotaExceededError или другие — silent fail
                return messages;
            }
        }

        function addMessage(messages, role, content) {
            const newMsg = {
                role,
                content,
                timestamp: new Date().toISOString(),
            };
            const updated = [...messages, newMsg];
            return saveHistory(updated);
        }

        function clearHistory() {
            sessionStorage.removeItem(SESSION_KEY);
            return [];
        }

        env.bus.addEventListener("LOGOUT", clearHistory);

        function collectContext() {
            try {
                const ctx = {};
                const hash = window.location.hash || "";
                ctx.url = hash.substring(0, 256);

                const actionMatch = hash.match(/action=([^&]+)/);
                if (actionMatch) {
                    ctx.action = decodeURIComponent(actionMatch[1]).substring(0, 128);
                }

                const viewMatch = hash.match(/view_type=([^&]+)/);
                if (viewMatch) {
                    ctx.view_type = decodeURIComponent(viewMatch[1]);
                }

                const modelMatch = hash.match(/model=([^&]+)/);
                if (modelMatch) {
                    ctx.model = decodeURIComponent(modelMatch[1]).substring(0, 128);
                }

                const menuApp = document.querySelector(
                    ".o_menu_brand, .o_home_menu .o_app.o_active .o_caption"
                );
                if (menuApp && menuApp.textContent) {
                    ctx.action = ctx.action || menuApp.textContent.trim().substring(0, 128);
                }

                const activeApp = document.querySelector(
                    ".o_navbar_apps_menu .o_app.o_active, .o_home_menu .o_app.o_active"
                );
                if (activeApp) {
                    const appName = activeApp.getAttribute("data-app-xmlid") ||
                        activeApp.getAttribute("data-module") || "";
                    ctx.module = appName.replace(/^base\.|^web\./, "").substring(0, 64);
                }

                const viewTypeEl = document.querySelector(
                    ".o_switch_view.active, .o_view_controller[class*='active']"
                );
                if (viewTypeEl && !ctx.view_type) {
                    const cls = viewTypeEl.className;
                    const types = ["list", "form", "kanban", "dashboard", "pivot", "graph"];
                    for (const t of types) {
                        if (cls.includes(`o_${t}`)) {
                            ctx.view_type = t;
                            break;
                        }
                    }
                }

                return ctx;
            } catch {
                return {};
            }
        }

        return { loadHistory, saveHistory, addMessage, clearHistory, collectContext };
    },
};

registry.category("services").add("ai_chat", aiChatService);
