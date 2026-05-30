/** @odoo-module **/

import { Component } from "@odoo/owl";

export class ConfirmationCard extends Component {
    static template = "ai_assistant.ConfirmationCard";
    static props = {
        plan: Object,
        pendingKey: String,
        onConfirm: Function,
        onCancel: Function,
    };

    onConfirmClick() {
        this.props.onConfirm(this.props.pendingKey);
    }

    onCancelClick() {
        this.props.onCancel(this.props.pendingKey);
    }
}

export class ResultCard extends Component {
    static template = "ai_assistant.ResultCard";
    static props = {
        status: String,
        record: { type: Object, optional: true },
        error: { type: Object, optional: true },
        nextHint: { type: String, optional: true },
        steps: { type: Array, optional: true },
    };

    get isSuccess() {
        return this.props.status === "success";
    }

    get recordUrl() {
        const record = this.props.record || {};
        if (record.url) {
            return record.url;
        }
        if (record.model && record.id) {
            return `/odoo/${record.model}/${record.id}`;
        }
        return "";
    }

    get errorMessage() {
        const error = this.props.error || {};
        return error.message || "Действие не выполнено.";
    }
}
