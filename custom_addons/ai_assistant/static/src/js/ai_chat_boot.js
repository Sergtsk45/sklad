/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

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

    setup() {
        this.chatService = useService("ai_chat");
        this.state = useState({
            isOpen: false,
            messages: this.chatService.loadHistory(),
            inputText: "",
            isLoading: false,
            status: "online",
            hasAccess: false,
        });
        this.messagesEndRef = useRef("messagesEnd");
        this.textareaRef = useRef("textarea");
        onMounted(async () => {
            this._scrollToBottom();
            try {
                const result = await rpc("/ai_assistant/check_access", {});
                this.state.hasAccess = result && result.has_access === true;
            } catch {
                this.state.hasAccess = false;
            }
        });
    }

    get suggestedPrompts() {
        return SUGGESTED_PROMPTS;
    }

    get showSuggested() {
        return this.state.messages.length === 0 && !this.state.isLoading;
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

    clearSession() {
        this.state.messages = this.chatService.clearHistory();
        this.state.inputText = "";
        this.state.isLoading = false;
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

    _addMessage(role, content) {
        this.state.messages = this.chatService.addMessage(
            this.state.messages,
            role,
            content
        );
        setTimeout(() => this._scrollToBottom(), 20);
    }

    async _fetchAnswer(userMessage) {
        this.state.isLoading = true;
        try {
            const result = await this._callBackend(userMessage);
            this._addMessage("assistant", result.answer);
            this.state.status = "online";
        } catch (_err) {
            this._addMessage(
                "assistant",
                "Сервис временно недоступен. Попробуйте позже."
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
                    message,
                    context,
                    history: this._buildHistory(),
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
        return data.result;
    }

    _buildHistory() {
        return this.state.messages.slice(-10).map((m) => ({
            role: m.role,
            content: m.content,
        }));
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
