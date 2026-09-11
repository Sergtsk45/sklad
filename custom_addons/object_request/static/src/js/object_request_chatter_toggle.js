/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { FormController } from "@web/views/form/form_controller";
import { useState } from "@odoo/owl";

const STORAGE_KEY = `object_request.form_chatter_visible,u${user.userId || "unknown"}`;

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.objectRequestChatterState = useState({
            visible: this.readObjectRequestChatterVisible(),
        });
    },

    get isObjectRequestChatterToggleEnabled() {
        return this.props.className
            ?.split(/\s+/)
            .includes("o_object_request_full_width_form");
    },

    readObjectRequestChatterVisible() {
        return browser.localStorage.getItem(STORAGE_KEY) === "1";
    },

    writeObjectRequestChatterVisible(visible) {
        browser.localStorage.setItem(STORAGE_KEY, visible ? "1" : "0");
    },

    toggleObjectRequestChatter() {
        const visible = !this.objectRequestChatterState.visible;
        this.objectRequestChatterState.visible = visible;
        this.writeObjectRequestChatterVisible(visible);
    },

    get objectRequestChatterToggleTitle() {
        return this.objectRequestChatterState.visible
            ? "Скрыть окно активности"
            : "Показать окно активности";
    },

    get className() {
        const result = super.className;
        if (this.isObjectRequestChatterToggleEnabled && !this.objectRequestChatterState.visible) {
            result.o_object_request_chatter_hidden = true;
        }
        return result;
    },
});
