/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { ListRenderer } from "@web/views/list/list_renderer";
import { useEffect } from "@odoo/owl";

const STORAGE_PREFIX = "object_request.line_column_layout";
const OPTIONAL_PREFIX = "object_request.line_optional_fields";
const SUPPORTED_SCOPES = new Set([
    "request_form_lines",
    "request_action_lines",
    "request_problem_lines",
    "request_po_diagnostics",
]);

function readJson(key, fallback) {
    try {
        const value = browser.localStorage.getItem(key);
        return value ? JSON.parse(value) : fallback;
    } catch {
        return fallback;
    }
}

function writeJson(key, value) {
    browser.localStorage.setItem(key, JSON.stringify(value));
}

function fieldColumnNames(columns) {
    return columns.filter((col) => col.type === "field" && col.name).map((col) => col.name);
}

function columnSignature(columns) {
    return fieldColumnNames(columns).sort().join(".");
}

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.objectRequestColumnLayoutScope = this.getObjectRequestColumnLayoutScope();
        if (!this.objectRequestColumnLayoutScope) {
            return;
        }
        this.objectRequestColumnLayoutKey = this.makeObjectRequestColumnLayoutKey();
        this.keyOptionalFields = `${OPTIONAL_PREFIX},${this.objectRequestColumnLayoutKey}`;
        this.wrapObjectRequestColumnResize();
        useEffect(() => {
            this.applyObjectRequestColumnWidths();
            return this.bindObjectRequestColumnDrag();
        });
    },

    getObjectRequestColumnLayoutScope() {
        const context = this.props.list.context || {};
        const scope = context.object_request_column_layout_scope;
        if (SUPPORTED_SCOPES.has(scope) && this.props.list.resModel === "object.request.line") {
            return scope;
        }
        if (
            this.props.list.resModel === "object.request.line" &&
            this.props.nestedKeyOptionalFieldsData?.field === "line_ids"
        ) {
            return "request_form_lines";
        }
        return null;
    },

    makeObjectRequestColumnLayoutKey() {
        const viewId = this.env.config.viewId || "no_view";
        const relationField = this.props.nestedKeyOptionalFieldsData?.field || "root";
        const fields = columnSignature(this.props.archInfo.columns || []);
        return [
            STORAGE_PREFIX,
            `u${user.userId || "unknown"}`,
            this.objectRequestColumnLayoutScope,
            this.props.list.resModel,
            viewId,
            relationField,
            fields,
        ].join(",");
    },

    readObjectRequestColumnLayout() {
        return readJson(this.objectRequestColumnLayoutKey, {});
    },

    writeObjectRequestColumnLayout(layout) {
        writeJson(this.objectRequestColumnLayoutKey, layout);
    },

    wrapObjectRequestColumnResize() {
        const columnWidths = this.columnWidths;
        if (!columnWidths || columnWidths.objectRequestWrapped) {
            return;
        }
        const originalOnStartResize = columnWidths.onStartResize.bind(columnWidths);
        const originalResetWidths = columnWidths.resetWidths.bind(columnWidths);
        columnWidths.onStartResize = (ev) => {
            const saveAfterResize = () => {
                window.removeEventListener("pointerup", saveAfterResize, true);
                window.removeEventListener("keydown", saveAfterResize, true);
                browser.setTimeout(() => this.saveObjectRequestColumnWidths(), 0);
            };
            window.addEventListener("pointerup", saveAfterResize, true);
            window.addEventListener("keydown", saveAfterResize, true);
            originalOnStartResize(ev);
        };
        columnWidths.resetWidths = () => {
            const layout = this.readObjectRequestColumnLayout();
            delete layout.widths;
            this.writeObjectRequestColumnLayout(layout);
            originalResetWidths();
        };
        columnWidths.objectRequestWrapped = true;
    },

    getActiveColumns() {
        const columns = super.getActiveColumns();
        if (!this.objectRequestColumnLayoutScope) {
            return columns;
        }
        const layout = this.readObjectRequestColumnLayout();
        return this.applyObjectRequestColumnOrder(columns, layout.order || []);
    },

    applyObjectRequestColumnOrder(columns, savedOrder) {
        if (!savedOrder.length) {
            return columns;
        }
        const orderIndex = new Map(savedOrder.map((name, index) => [name, index]));
        const knownFieldColumns = [];
        const newFieldColumns = [];
        for (const column of columns) {
            if (column.type !== "field" || !column.name) {
                continue;
            }
            if (orderIndex.has(column.name)) {
                knownFieldColumns.push(column);
            } else {
                newFieldColumns.push(column);
            }
        }
        knownFieldColumns.sort((left, right) => orderIndex.get(left.name) - orderIndex.get(right.name));
        const reorderedFields = [...knownFieldColumns, ...newFieldColumns];
        let fieldIndex = 0;
        return columns.map((column) => {
            if (column.type !== "field" || !column.name) {
                return column;
            }
            return reorderedFields[fieldIndex++];
        });
    },

    /**
     * Builds the full known column order (visible and currently hidden optional
     * columns). Starting from the previously saved order, so that hidden columns
     * keep their relative position when a drag only involves visible columns.
     * Any field column missing from the saved order (new column, or first ever
     * drag) is appended at the end, following the original XML/allColumns order.
     */
    buildObjectRequestFullColumnOrder() {
        const savedOrder = this.readObjectRequestColumnLayout().order || [];
        const allFieldNames = fieldColumnNames(this.allColumns);
        const allFieldNamesSet = new Set(allFieldNames);
        const knownNames = new Set();
        const order = [];
        for (const name of savedOrder) {
            if (allFieldNamesSet.has(name) && !knownNames.has(name)) {
                order.push(name);
                knownNames.add(name);
            }
        }
        for (const name of allFieldNames) {
            if (!knownNames.has(name)) {
                order.push(name);
                knownNames.add(name);
            }
        }
        return order;
    },

    saveObjectRequestColumnOrder(order) {
        const layout = this.readObjectRequestColumnLayout();
        layout.order = order.filter((name) => this.allColumns.some((col) => col.name === name));
        this.writeObjectRequestColumnLayout(layout);
    },

    saveObjectRequestColumnWidths() {
        if (!this.tableRef.el) {
            return;
        }
        const widths = {};
        for (const th of this.tableRef.el.querySelectorAll("thead th[data-name]")) {
            const name = th.dataset.name;
            const width = Math.round(th.getBoundingClientRect().width);
            if (name && width > 0) {
                widths[name] = width;
            }
        }
        const layout = this.readObjectRequestColumnLayout();
        layout.widths = widths;
        this.writeObjectRequestColumnLayout(layout);
    },

    applyObjectRequestColumnWidths() {
        if (!this.tableRef.el) {
            return;
        }
        const widths = this.readObjectRequestColumnLayout().widths || {};
        if (!Object.keys(widths).length) {
            return;
        }
        for (const th of this.tableRef.el.querySelectorAll("thead th[data-name]")) {
            const width = widths[th.dataset.name];
            if (width) {
                th.style.width = `${width}px`;
            }
        }
    },

    bindObjectRequestColumnDrag() {
        const table = this.tableRef.el;
        if (!table) {
            return () => {};
        }
        const thead = table.querySelector("thead");
        if (!thead) {
            return () => {};
        }
        let dragState = null;

        const clearDragState = () => {
            if (dragState?.sourceTh) {
                dragState.sourceTh.classList.remove("o_object_request_column_drag_source");
            }
            table.classList.remove("o_object_request_column_dragging");
            for (const th of table.querySelectorAll(".o_object_request_column_drag_over")) {
                th.classList.remove("o_object_request_column_drag_over");
            }
            dragState = null;
        };

        const onPointerMove = (ev) => {
            if (!dragState) {
                return;
            }
            const distance = Math.abs(ev.clientX - dragState.startX) + Math.abs(ev.clientY - dragState.startY);
            if (!dragState.dragging && distance < 6) {
                return;
            }
            dragState.dragging = true;
            table.classList.add("o_object_request_column_dragging");
            ev.preventDefault();
            const targetTh = document.elementFromPoint(ev.clientX, ev.clientY)?.closest("th[data-name]");
            if (!targetTh || !thead.contains(targetTh) || targetTh === dragState.sourceTh) {
                return;
            }
            for (const th of table.querySelectorAll(".o_object_request_column_drag_over")) {
                th.classList.remove("o_object_request_column_drag_over");
            }
            targetTh.classList.add("o_object_request_column_drag_over");
            dragState.targetName = targetTh.dataset.name;
        };

        const onPointerUp = (ev) => {
            if (!dragState) {
                return;
            }
            const { dragging, sourceName, targetName } = dragState;
            clearDragState();
            if (!dragging || !targetName || sourceName === targetName) {
                return;
            }
            ev.preventDefault();
            ev.stopPropagation();
            const order = this.buildObjectRequestFullColumnOrder();
            const fromIndex = order.indexOf(sourceName);
            const toIndex = order.indexOf(targetName);
            if (fromIndex < 0 || toIndex < 0) {
                return;
            }
            order.splice(toIndex, 0, order.splice(fromIndex, 1)[0]);
            this.preventReorder = true;
            this.saveObjectRequestColumnOrder(order);
            this.render();
        };

        const onPointerDown = (ev) => {
            if (ev.button !== 0 || this.editedRecord || this.columnWidths.resizing) {
                return;
            }
            if (ev.target.closest(".o_resize, button, a, input, label, .dropdown")) {
                return;
            }
            const sourceTh = ev.target.closest("th[data-name]");
            if (!sourceTh || !thead.contains(sourceTh)) {
                return;
            }
            dragState = {
                sourceName: sourceTh.dataset.name,
                sourceTh,
                startX: ev.clientX,
                startY: ev.clientY,
                dragging: false,
                targetName: null,
            };
            sourceTh.classList.add("o_object_request_column_drag_source");
        };

        thead.addEventListener("pointerdown", onPointerDown);
        window.addEventListener("pointermove", onPointerMove);
        window.addEventListener("pointerup", onPointerUp, true);
        return () => {
            thead.removeEventListener("pointerdown", onPointerDown);
            window.removeEventListener("pointermove", onPointerMove);
            window.removeEventListener("pointerup", onPointerUp, true);
            clearDragState();
        };
    },
});
