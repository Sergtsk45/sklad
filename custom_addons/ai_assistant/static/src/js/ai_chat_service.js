/** @odoo-module **/

import { registry } from "@web/core/registry";
import { needsScreenshot } from "./screenshot_trigger";

const SESSION_KEY = "odoo_ai_assistant_session_v1";
const SCHEMA_VERSION = 3;
const MAX_MESSAGES = 50;
const MAX_BYTES = 100 * 1024; // 100 KB (без скриншотов — они не сохраняются)
const MAX_SCREENSHOT_BYTES = 500 * 1024; // 500 KB base64

export const aiChatService = {
    start(env) {
        function _readSession() {
            try {
                const raw = sessionStorage.getItem(SESSION_KEY);
                if (!raw) {
                    return {};
                }
                const data = JSON.parse(raw);
                const version = Number(data && data.version ? data.version : 1);
                if (
                    !data ||
                    !Array.isArray(data.messages) ||
                    version < 1 ||
                    version > SCHEMA_VERSION
                ) {
                    sessionStorage.removeItem(SESSION_KEY);
                    return {};
                }
                return data;
            } catch {
                sessionStorage.removeItem(SESSION_KEY);
                return {};
            }
        }

        function loadSession() {
            const data = _readSession();
            return {
                messages: data.messages || [],
                extractionToken: data.extraction_token || null,
                awaitingPoWarehouse: data.awaiting_po_warehouse === true,
                purchaseFlow: data.purchase_flow || null,
                activeReplenishmentToken:
                    data.active_replenishment_token || null,
            };
        }

        function loadHistory() {
            return loadSession().messages;
        }

        function saveHistory(messages, state = {}) {
            try {
                const previous = loadSession();
                // Никогда не сохраняем скриншоты в историю
                const clean = messages.map((m) => {
                    const msg = {
                        role: m.role,
                        content: m.content,
                        timestamp: m.timestamp,
                    };
                    if (Array.isArray(m.cards) && m.cards.length) {
                        msg.cards = m.cards;
                    }
                    if (Array.isArray(m.links) && m.links.length) {
                        msg.links = m.links;
                    }
                    if (Array.isArray(m.suggestions) && m.suggestions.length) {
                        msg.suggestions = m.suggestions;
                    }
                    return msg;
                });

                let trimmed =
                    clean.length > MAX_MESSAGES
                        ? clean.slice(-MAX_MESSAGES)
                        : clean;

                let serialized = JSON.stringify({
                    version: SCHEMA_VERSION,
                    messages: trimmed,
                    extraction_token:
                        state.extractionToken !== undefined
                            ? state.extractionToken
                            : previous.extractionToken,
                    awaiting_po_warehouse:
                        state.awaitingPoWarehouse !== undefined
                            ? state.awaitingPoWarehouse
                            : previous.awaitingPoWarehouse,
                    purchase_flow:
                        state.purchaseFlow !== undefined
                            ? state.purchaseFlow
                            : previous.purchaseFlow,
                    active_replenishment_token:
                        state.activeReplenishmentToken !== undefined
                            ? state.activeReplenishmentToken
                            : previous.activeReplenishmentToken,
                });

                while (trimmed.length > 1 && serialized.length > MAX_BYTES) {
                    trimmed = trimmed.slice(1);
                    serialized = JSON.stringify({
                        version: SCHEMA_VERSION,
                        messages: trimmed,
                        extraction_token:
                            state.extractionToken !== undefined
                                ? state.extractionToken
                                : previous.extractionToken,
                        awaiting_po_warehouse:
                            state.awaitingPoWarehouse !== undefined
                                ? state.awaitingPoWarehouse
                                : previous.awaitingPoWarehouse,
                        purchase_flow:
                            state.purchaseFlow !== undefined
                                ? state.purchaseFlow
                                : previous.purchaseFlow,
                        active_replenishment_token:
                            state.activeReplenishmentToken !== undefined
                                ? state.activeReplenishmentToken
                                : previous.activeReplenishmentToken,
                    });
                }

                sessionStorage.setItem(SESSION_KEY, serialized);
                return trimmed;
            } catch {
                // QuotaExceededError или другие — silent fail
                return messages;
            }
        }

        function saveSessionState(state = {}) {
            return saveHistory(loadHistory(), state);
        }

        function addMessage(messages, role, content, extra = {}) {
            const newMsg = {
                role,
                content,
                timestamp: new Date().toISOString(),
            };
            if (Array.isArray(extra.cards) && extra.cards.length) {
                newMsg.cards = extra.cards;
            }
            if (Array.isArray(extra.links) && extra.links.length) {
                newMsg.links = extra.links;
            }
            if (Array.isArray(extra.suggestions) && extra.suggestions.length) {
                newMsg.suggestions = extra.suggestions;
            }
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

        /**
         * AIA-022: Захватить скриншот DOM → JPEG base64.
         * Скрывает виджет чата перед захватом, восстанавливает в finally.
         * @returns {Promise<string|null>} data URL или null при ошибке
         */
        async function captureScreen() {
            // html2canvas должен быть загружен через assets
            if (typeof window.html2canvas !== 'function') {
                console.warn('[AI Assistant] html2canvas не загружен');
                return null;
            }

            // Скрыть виджет чата перед захватом
            const chatPanel = document.querySelector('.o_ai_chat_panel');
            const chatFab = document.querySelector('.o_ai_chat_fab');
            const hidden = [];
            for (const el of [chatPanel, chatFab]) {
                if (el) {
                    el.style.setProperty('display', 'none', 'important');
                    hidden.push(el);
                }
            }

            try {
                const canvas = await window.html2canvas(document.body, {
                    scale: 0.7,
                    useCORS: true,
                    logging: false,
                    width: window.innerWidth,
                    height: window.innerHeight,
                    windowWidth: window.innerWidth,
                    windowHeight: window.innerHeight,
                });

                const dataUrl = canvas.toDataURL('image/jpeg', 0.8);

                // Проверяем размер: base64 после заголовка
                const b64 = dataUrl.split(',')[1] || '';
                if (b64.length > MAX_SCREENSHOT_BYTES) {
                    console.warn('[AI Assistant] Скриншот слишком большой, пропускаем');
                    return null;
                }

                return dataUrl;
            } catch (err) {
                console.warn('[AI Assistant] captureScreen failed:', err);
                return null;
            } finally {
                // Восстановить видимость
                for (const el of hidden) {
                    el.style.removeProperty('display');
                }
            }
        }

        /**
         * AIA-021/022/023: Определить, нужен ли скриншот, и захватить его.
         * @param {string} message
         * @returns {Promise<string|null>}
         */
        async function maybeCapture(message) {
            if (!needsScreenshot(message)) {
                return null;
            }
            return captureScreen();
        }

        /**
         * AIA-056: Загрузить файл счёта на /ai_assistant/upload_invoice.
         * @param {File} file
         * @returns {Promise<{success, extraction_token, summary, meta}>}
         */
        async function uploadInvoice(file) {
            const formData = new FormData();
            formData.append("file", file, file.name);
            const response = await fetch("/ai_assistant/upload_invoice", {
                method: "POST",
                headers: { "X-Requested-With": "XMLHttpRequest" },
                body: formData,
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        }

        async function workflowAction(extractionToken, action, payload = {}) {
            const params = {
                message: "",
                history: [],
                extraction_token: extractionToken,
                invoice_workflow_action: action,
                invoice_workflow_payload: payload || {},
            };
            if (payload && (payload.warehouse_query || payload.warehouse_name)) {
                params.invoice_po_warehouse =
                    payload.warehouse_query || payload.warehouse_name;
            }
            const response = await fetch("/ai_assistant/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params,
                }),
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error.message || "Backend error");
            }
            const result = data.result || {};
            if (result.error || result.ok === false) {
                throw new Error(result.error || "Invoice workflow failed");
            }
            return result;
        }

        async function replenishmentWorkflowAction(
            replenishmentToken,
            action,
            payload = {}
        ) {
            const response = await fetch("/ai_assistant/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {
                        message: "",
                        history: [],
                        replenishment_token: replenishmentToken,
                        replenishment_action: action,
                        replenishment_payload: payload || {},
                    },
                }),
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error.message || "Backend error");
            }
            const result = data.result || {};
            if (result.error || result.ok === false) {
                throw new Error(result.error || "Replenishment workflow failed");
            }
            return result;
        }

        async function callPoAction(replenishmentToken, action, poId) {
            const response = await fetch("/ai_assistant/po_action", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {
                        replenishment_token: replenishmentToken,
                        action,
                        po_id: poId,
                    },
                }),
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error.message || "Backend error");
            }
            const result = data.result || {};
            if (result.error || result.ok === false) {
                throw new Error(result.error || "Purchase order action failed");
            }
            return result;
        }

        async function confirmAction(pendingKey, decision) {
            const response = await fetch("/ai_assistant/confirm", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {
                        pending_key: pendingKey,
                        decision,
                    },
                }),
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error.message || "Backend error");
            }
            return data.result || {};
        }

        return {
            loadSession,
            loadHistory,
            saveHistory,
            saveSessionState,
            addMessage,
            clearHistory,
            collectContext,
            captureScreen,
            maybeCapture,
            confirmAction,
            workflowAction,
            replenishmentWorkflowAction,
            callPoAction,
            uploadInvoice,
            needsScreenshot,
        };
    },
};

registry.category("services").add("ai_chat", aiChatService);
