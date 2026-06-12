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

    get toolName() {
        return this.props.plan.tool_name || "";
    }

    get title() {
        return this.props.plan.title || "Подтвердите действие";
    }

    get fields() {
        const fields = this.props.plan.fields || [];
        if (![
            "create_partner_draft",
            "update_partner_draft",
            "add_partner_bank_draft",
            "add_partner_contact_draft",
        ].includes(this.toolName)) {
            return fields;
        }
        const labels = {
            partner_id: "Контрагент",
            name: "Название",
            ref: "Сокращение",
            vat: "ИНН",
            category: "Категория",
            is_company: "Тип",
            street: "Адрес",
            city: "Город",
            state_name: "Регион",
            zip: "Индекс",
            phone: "Телефон",
            email: "Email",
            comment: "Комментарий",
            acc_number: "Расчётный счёт",
            bic: "БИК",
            bank_name: "Банк",
            acc_holder_name: "Получатель",
            note: "Примечание",
            function: "Должность",
        };
        const order = [
            "partner_id",
            "name",
            "ref",
            "vat",
            "category",
            "is_company",
            "street",
            "city",
            "state_name",
            "zip",
            "phone",
            "email",
            "function",
            "acc_number",
            "bic",
            "bank_name",
            "acc_holder_name",
            "note",
            "comment",
        ];
        return [...fields]
            .sort((left, right) => {
                const leftIndex = order.indexOf(left.label);
                const rightIndex = order.indexOf(right.label);
                return (
                    (leftIndex === -1 ? order.length : leftIndex) -
                    (rightIndex === -1 ? order.length : rightIndex)
                );
            })
            .map((field) => ({
                ...field,
                label: labels[field.label] || field.label,
                value: this._displayValue(field),
            }));
    }

    _displayValue(field) {
        if (field.label !== "is_company") {
            return field.value;
        }
        if (field.value === true || field.value === "True" || field.value === "true") {
            return "Юрлицо";
        }
        if (field.value === false || field.value === "False" || field.value === "false") {
            return "ИП / физлицо";
        }
        return "";
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
        details: { type: Array, optional: true },
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

    get title() {
        const record = this.props.record || {};
        if (this.isSuccess && record.model === "res.partner") {
            return "Контрагент готов";
        }
        return this.isSuccess ? "Черновик создан" : "Действие не выполнено";
    }
}
