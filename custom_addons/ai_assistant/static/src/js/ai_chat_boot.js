/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationCard, ResultCard } from "./ai_chat_actions";
import {
    formatMessageContent,
    mergeMessageLinks,
} from "./ai_chat_format";

const SUGGESTED_PROMPTS = [
    "Как пользоваться этим разделом?",
    "Что можно делать на этой странице?",
    "Как добавить товар на склад?",
    "Как создать контрагента?",
    "Какие возможности есть в этом модуле?",
];

export class AiChatWidget extends Component {
    static template = "ai_assistant.AiChatWidget";
    static props = {};
    static components = { ConfirmationCard, ResultCard };

    setup() {
        this.chatService = useService("ai_chat");
        this.state = useState({
            isOpen: false,
            messages: this.chatService.loadHistory(),
            inputText: "",
            isLoading: false,
            isCapturing: false,   // идёт захват скриншота
            isUploading: false,   // AIA-056: идёт загрузка счёта
            extractionToken: null, // AIA-057: токен распознанного счёта
            awaitingPoWarehouse: false,
            status: "online",
            hasAccess: false,
            hasSupply: false,     // AIA-056: группа снабжение
        });
        this.messagesEndRef = useRef("messagesEnd");
        this.textareaRef = useRef("textarea");
        this.fileInputRef = useRef("fileInput");  // AIA-056
        onMounted(async () => {
            this._scrollToBottom();
            try {
                const result = await fetch("/ai_assistant/check_access", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: {},
                    }),
                });
                const data = await result.json();
                this.state.hasAccess =
                    data && data.result && data.result.has_access === true;
                this.state.hasSupply =
                    data && data.result && data.result.has_supply === true;
            } catch {
                this.state.hasAccess = false;
                this.state.hasSupply = false;
            }
        });
    }

    get suggestedPrompts() {
        return SUGGESTED_PROMPTS;
    }

    get showSuggested() {
        return this.state.messages.length === 0 && !this.state.isLoading;
    }

    get loadingLabel() {
        if (this.state.isUploading) {
            return "Распознаю счёт...";
        }
        return this.state.isCapturing
            ? "Делаю скриншот..."
            : "Думаю...";
    }

    cardKey(card, index) {
        if (card.pending_key) {
            return card.pending_key;
        }
        if (card.type === "result" && card.record?.id) {
            return `result-${card.record.model || "record"}-${card.record.id}`;
        }
        return `${card.type || "card"}-${index}`;
    }

    messageLinks(msg) {
        return mergeMessageLinks(msg.links, msg.content);
    }

    messageDisplayContent(msg) {
        return formatMessageContent(msg.content, this.messageLinks(msg));
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen) {
            setTimeout(() => this.textareaRef.el && this.textareaRef.el.focus(), 50);
        }
    }

    onSuggestedPrompt(prompt) {
        this.state.inputText = prompt;
        this._doSend();
    }

    onMessageSuggestion(suggestion) {
        if (!suggestion || this.state.isLoading) {
            return;
        }
        if (suggestion.action) {
            this._runInvoiceWorkflowAction(suggestion.action);
            return;
        }
        if (suggestion.label) {
            this.state.inputText = suggestion.label;
            this._doSend();
        }
    }

    onInputKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this._doSend();
        }
    }

    onInput(ev) {
        this.state.inputText = ev.target.value;
    }

    sendMessage() {
        this._doSend();
    }

    /** AIA-056: Клик по кнопке-скрепке — открываем файловый диалог. */
    onAttachClick() {
        const input = this.fileInputRef.el;
        if (input && !this.state.isLoading) {
            input.value = "";
            input.click();
        }
    }

    /** AIA-056: Файл выбран в input[type=file] — загружаем счёт. */
    async onFileSelected(ev) {
        const file = ev.target && ev.target.files && ev.target.files[0];
        if (!file) {
            return;
        }
        await this._uploadInvoice(file);
    }

    /** AIA-056: Загрузить счёт и показать сводку в чате. */
    async _uploadInvoice(file) {
        if (this.state.isLoading) {
            return;
        }
        this.state.isLoading = true;
        this.state.isUploading = true;
        this._addMessage("user", `📎 ${file.name}`);
        try {
            const result = await this.chatService.uploadInvoice(file);
            if (result && result.success) {
                this.state.extractionToken = result.extraction_token || null;
                this._addMessage("assistant", result.summary || "Счёт распознан.");
            } else {
                const errMsg = (result && result.error) || "Не удалось распознать счёт.";
                this._addMessage("assistant", `⚠ ${errMsg}`);
            }
            this.state.status = "online";
        } catch (_err) {
            this._addMessage("assistant", "Ошибка при загрузке файла. Попробуйте позже.");
            this.state.status = "error";
        } finally {
            this.state.isLoading = false;
            this.state.isUploading = false;
        }
    }

    clearSession() {
        this.state.messages = this.chatService.clearHistory();
        this.state.inputText = "";
        this.state.isLoading = false;
        this.state.isCapturing = false;
        this.state.extractionToken = null;
        this.state.awaitingPoWarehouse = false;
    }

    _doSend() {
        const text = this.state.inputText.trim();
        if (!text || this.state.isLoading) {
            return;
        }
        this._addMessage("user", text);
        this.state.inputText = "";
        this._fetchAnswer(text);
    }

    async onConfirmPending(pendingKey) {
        await this._confirmPending(pendingKey, "confirm");
    }

    async onCancelPending(pendingKey) {
        await this._confirmPending(pendingKey, "cancel");
    }

    _addMessage(role, content, extra = {}) {
        this.state.messages = this.chatService.addMessage(
            this.state.messages,
            role,
            content,
            extra
        );
        if (extra.meta && extra.meta.awaiting_po_warehouse) {
            this.state.awaitingPoWarehouse = true;
        } else if (extra.meta && extra.meta.awaiting_po_warehouse === false) {
            this.state.awaitingPoWarehouse = false;
        }
        setTimeout(() => this._scrollToBottom(), 20);
    }

    async _fetchAnswer(userMessage) {
        this.state.isLoading = true;
        this.state.isCapturing = false;
        try {
            const result = await this._callBackend(userMessage);
            await this._cancelActiveConfirmations(this._extractCards(result));
            this._applyResponseMeta(result);
            this._addMessage("assistant", result.answer || "", {
                cards: this._extractCards(result),
                links: this._extractLinks(result),
                suggestions: result.suggestions || [],
                meta: result.meta || {},
            });
            this.state.status = "online";
        } catch (_err) {
            this._addMessage(
                "assistant",
                "Сервис временно недоступен. Попробуйте позже."
            );
            this.state.status = "error";
        } finally {
            this.state.isLoading = false;
            this.state.isCapturing = false;
        }
    }

    async _confirmPending(pendingKey, decision) {
        if (!pendingKey || this.state.isLoading) {
            return;
        }
        this.state.isLoading = true;
        this.state.isCapturing = false;
        try {
            const result = await this.chatService.confirmAction(pendingKey, decision);
            this._markPendingCardResolved(
                pendingKey,
                decision,
                this._extractCards(result)
            );
            this._applyResponseMeta(result);
            // Карточка уже вставлена в старое сообщение через _markPendingCardResolved
            // Добавляем только текстовый ответ + suggestions
            const answer = result.answer || "";
            const suggestions = result.suggestions || [];
            if (answer || suggestions.length) {
                this._addMessage("assistant", answer, {
                    suggestions,
                    meta: result.meta || {},
                });
            }
            this.state.status = "online";
        } catch (_err) {
            this._addMessage(
                "assistant",
                "Не удалось выполнить действие. Попробуйте повторить запрос."
            );
            this.state.status = "error";
        } finally {
            this.state.isLoading = false;
        }
    }

    async _callBackend(message) {
        const context = this.chatService.collectContext
            ? this.chatService.collectContext()
            : {};

        // AIA-022/023: захват скриншота при триггерных фразах
        let screenshot = null;
        if (this.chatService.maybeCapture) {
            this.state.isCapturing = true;
            try {
                screenshot = await this.chatService.maybeCapture(message);
            } catch {
                // продолжаем без скриншота
            }
            this.state.isCapturing = false;
        }

        const params = {
            message,
            context,
            history: this._buildHistory(),
        };

        if (this.state.extractionToken) {
            params.extraction_token = this.state.extractionToken;
        }
        if (this.state.awaitingPoWarehouse) {
            params.awaiting_po_warehouse = true;
        }

        // Добавить скриншот в payload только если захват удался
        if (screenshot) {
            params.screenshot = screenshot;
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
        return data.result;
    }

    _extractCards(result) {
        return result && Array.isArray(result.cards) ? result.cards : [];
    }

    _extractLinks(result) {
        return result && Array.isArray(result.links) ? result.links : [];
    }

    async _cancelActiveConfirmations(incomingCards) {
        if (!this._hasConfirmationCard(incomingCards)) {
            return;
        }
        const pendingKeys = this._activePendingKeys();
        for (const pendingKey of pendingKeys) {
            try {
                await this.chatService.confirmAction(pendingKey, "cancel");
                this._markPendingCardResolved(pendingKey, "cancel");
            } catch {
                this._markPendingCardResolved(pendingKey, "cancel");
            }
        }
    }

    _hasConfirmationCard(cards) {
        return (cards || []).some((card) => {
            return card.type === "confirmation" && card.pending_key;
        });
    }

    _activePendingKeys() {
        const pendingKeys = [];
        for (const message of this.state.messages) {
            for (const card of message.cards || []) {
                if (
                    card.type === "confirmation" &&
                    card.pending_key &&
                    !(card.plan && card.plan.state)
                ) {
                    pendingKeys.push(card.pending_key);
                }
            }
        }
        return pendingKeys;
    }

    _markPendingCardResolved(pendingKey, decision, replacementCards = []) {
        const replacementCard = replacementCards.find((card) => {
            return card.type === "result";
        });
        const messages = this.state.messages.map((message) => {
            if (!Array.isArray(message.cards)) {
                return message;
            }
            const cards = message.cards.map((card) => {
                if (card.pending_key !== pendingKey) {
                    return card;
                }
                if (replacementCard) {
                    return replacementCard;
                }
                return {
                    ...card,
                    plan: {
                        ...card.plan,
                        state: decision === "confirm" ? "confirmed" : "cancelled",
                    },
                };
            });
            return { ...message, cards };
        });
        this.state.messages = this.chatService.saveHistory(messages);
    }

    _buildHistory() {
        // AIA-023: исключаем скриншоты из истории
        return this.state.messages.slice(-10).map((m) => ({
            role: m.role,
            content: m.content,
        }));
    }

    _applyResponseMeta(result) {
        const meta = (result && result.meta) || {};
        if (meta.awaiting_po_warehouse) {
            this.state.awaitingPoWarehouse = true;
        }
        if (meta.warehouse_id !== undefined) {
            this.state.awaitingPoWarehouse = false;
        }
    }

    async _runInvoiceWorkflowAction(action) {
        if (this.state.isLoading || !this.state.extractionToken) {
            return;
        }
        this.state.isLoading = true;
        this.state.isCapturing = false;
        try {
            const result = await this.chatService.workflowAction(
                this.state.extractionToken,
                action
            );
            await this._cancelActiveConfirmations(this._extractCards(result));
            this._applyResponseMeta(result);
            this._addMessage("assistant", result.answer || "", {
                cards: this._extractCards(result),
                suggestions: result.suggestions || [],
                meta: result.meta || {},
            });
            this.state.status = "online";
        } catch (_err) {
            this._addMessage(
                "assistant",
                "Не удалось выполнить действие. Попробуйте повторить запрос."
            );
            this.state.status = "error";
        } finally {
            this.state.isLoading = false;
        }
    }

    _scrollToBottom() {
        const el = this.messagesEndRef.el;
        if (el) {
            el.scrollIntoView({ behavior: "smooth" });
        }
    }
}

registry.category("main_components").add("ai_assistant.AiChatWidget", {
    Component: AiChatWidget,
    props: {},
});
