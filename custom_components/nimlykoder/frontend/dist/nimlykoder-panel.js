import { LitElement, html, css } from "https://cdn.jsdelivr.net/gh/lit/dist@2/core/lit-core.min.js";

class NimlykoderPanel extends LitElement {
    static get properties() {
        return {
            hass: { type: Object },
            narrow: { type: Boolean },
            route: { type: Object },
            panel: { type: Object },
            codes: { type: Array },
            loading: { type: Boolean },
            error: { type: String },
            showAddDialog: { type: Boolean },
            showEditDialog: { type: Boolean },
            showRemoveDialog: { type: Boolean },
            editingSlot: { type: Number },
            removingSlot: { type: Number },
        };
    }

    constructor() {
        super();
        this.codes = [];
        this.loading = true;
        this.error = null;
        this.showAddDialog = false;
        this.showEditDialog = false;
        this.showRemoveDialog = false;
        this.editingSlot = null;
        this.removingSlot = null;
    }

    static get styles() {
        return css`
            :host {
                display: block;
                padding: 16px;
                font-family: var(--paper-font-body1_-_font-family);
            }

            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }

            h1 {
                margin: 0;
                font-size: 24px;
                font-weight: 400;
            }

            ha-card {
                margin-bottom: 16px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th, td {
                text-align: left;
                padding: 12px;
                border-bottom: 1px solid var(--divider-color);
            }

            th {
                font-weight: 500;
                color: var(--secondary-text-color);
            }

            tr:hover {
                background: var(--paper-grey-100);
            }

            .status-badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
            }

            .status-active {
                background: var(--success-color, #4caf50);
                color: white;
            }

            .status-expired {
                background: var(--error-color, #f44336);
                color: white;
            }

            .status-reserved {
                background: var(--warning-color, #ff9800);
                color: white;
            }

            .actions {
                display: flex;
                gap: 8px;
            }

            .empty-state {
                text-align: center;
                padding: 40px;
                color: var(--secondary-text-color);
            }

            .error-message {
                background: var(--error-color);
                color: white;
                padding: 12px;
                border-radius: 4px;
                margin-bottom: 16px;
            }

            mwc-button {
                margin: 4px;
            }

            ha-dialog {
                --mdc-dialog-min-width: 500px;
            }

            .dialog-content {
                padding: 16px;
            }

            ha-textfield, ha-select {
                display: block;
                margin-bottom: 16px;
                width: 100%;
            }
        `;
    }

    connectedCallback() {
        super.connectedCallback();
        this.loadCodes();
    }

    async loadCodes() {
        try {
            this.loading = true;
            const result = await this.hass.callWS({
                type: "nimlykoder/list",
            });
            this.codes = result.codes || [];
            this.loading = false;
        } catch (err) {
            this.error = err.message;
            this.loading = false;
        }
    }

    async addCode(data) {
        try {
            await this.hass.callWS({
                type: "nimlykoder/add",
                ...data,
            });
            this.showAddDialog = false;
            await this.loadCodes();
        } catch (err) {
            this.error = err.message;
        }
    }

    async removeCode(slot) {
        try {
            await this.hass.callWS({
                type: "nimlykoder/remove",
                slot: slot,
            });
            this.showRemoveDialog = false;
            await this.loadCodes();
        } catch (err) {
            this.error = err.message;
        }
    }

    async updateExpiry(slot, expiry) {
        try {
            await this.hass.callWS({
                type: "nimlykoder/update_expiry",
                slot: slot,
                expiry: expiry,
            });
            this.showEditDialog = false;
            await this.loadCodes();
        } catch (err) {
            this.error = err.message;
        }
    }

    render() {
        return html`
            <div class="header">
                <h1>Nimlykoder</h1>
                <mwc-button raised @click=${() => (this.showAddDialog = true)}>
                    Add Code
                </mwc-button>
            </div>

            ${this.error
                ? html`
                      <div class="error-message">
                          ${this.error}
                          <mwc-icon-button
                              icon="mdi:close"
                              @click=${() => (this.error = null)}
                          ></mwc-icon-button>
                      </div>
                  `
                : ""}

            <ha-card>
                ${this.loading
                    ? html`<div style="padding: 40px; text-align: center;">Loading...</div>`
                    : this.codes.length === 0
                    ? html`
                          <div class="empty-state">
                              No codes configured. Click "Add Code" to get started.
                          </div>
                      `
                    : html`
                          <table>
                              <thead>
                                  <tr>
                                      <th>Slot</th>
                                      <th>Name</th>
                                      <th>Type</th>
                                      <th>Expiry</th>
                                      <th>Status</th>
                                      <th>Actions</th>
                                  </tr>
                              </thead>
                              <tbody>
                                  ${this.codes.map((code) => this.renderCodeRow(code))}
                              </tbody>
                          </table>
                      `}
            </ha-card>

            ${this.renderAddDialog()} ${this.renderEditDialog()} ${this.renderRemoveDialog()}
        `;
    }

    renderCodeRow(code) {
        const isExpired =
            code.type === "guest" &&
            code.expiry &&
            new Date(code.expiry) < new Date();
        const status = isExpired ? "expired" : "active";
        const statusLabel = isExpired ? "Expired" : "Active";

        return html`
            <tr>
                <td>${code.slot}</td>
                <td>${code.name}</td>
                <td>${code.type}</td>
                <td>${code.expiry || "-"}</td>
                <td>
                    <span class="status-badge status-${status}">${statusLabel}</span>
                </td>
                <td>
                    <div class="actions">
                        <mwc-button
                            outlined
                            @click=${() => {
                                this.editingSlot = code.slot;
                                this.showEditDialog = true;
                            }}
                        >
                            Edit
                        </mwc-button>
                        <mwc-button
                            outlined
                            @click=${() => {
                                this.removingSlot = code.slot;
                                this.showRemoveDialog = true;
                            }}
                        >
                            Remove
                        </mwc-button>
                    </div>
                </td>
            </tr>
        `;
    }

    renderAddDialog() {
        if (!this.showAddDialog) return "";

        return html`
            <ha-dialog
                open
                @closed=${() => (this.showAddDialog = false)}
                .heading=${"Add New Code"}
            >
                <div class="dialog-content">
                    <ha-textfield
                        id="add-name"
                        label="Name"
                        required
                    ></ha-textfield>
                    <ha-textfield
                        id="add-pin"
                        label="PIN Code (4 digits)"
                        type="password"
                        pattern="[0-9]{4}"
                        maxlength="4"
                        required
                    ></ha-textfield>
                    <ha-select id="add-type" label="Type" required>
                        <mwc-list-item value="permanent">Permanent</mwc-list-item>
                        <mwc-list-item value="guest" selected>Guest</mwc-list-item>
                    </ha-select>
                    <ha-textfield
                        id="add-expiry"
                        label="Expiry Date (YYYY-MM-DD)"
                        type="date"
                    ></ha-textfield>
                    <ha-textfield
                        id="add-slot"
                        label="Slot (leave empty for auto-assign)"
                        type="number"
                        min="0"
                        max="99"
                    ></ha-textfield>
                </div>
                <mwc-button slot="primaryAction" @click=${this._handleAddSubmit}>
                    Save
                </mwc-button>
                <mwc-button slot="secondaryAction" dialogAction="cancel">
                    Cancel
                </mwc-button>
            </ha-dialog>
        `;
    }

    renderEditDialog() {
        if (!this.showEditDialog) return "";

        const code = this.codes.find((c) => c.slot === this.editingSlot);
        if (!code) return "";

        return html`
            <ha-dialog
                open
                @closed=${() => (this.showEditDialog = false)}
                .heading=${"Edit Expiry"}
            >
                <div class="dialog-content">
                    <ha-textfield
                        id="edit-expiry"
                        label="Expiry Date (YYYY-MM-DD)"
                        type="date"
                        .value=${code.expiry || ""}
                    ></ha-textfield>
                </div>
                <mwc-button slot="primaryAction" @click=${this._handleEditSubmit}>
                    Update
                </mwc-button>
                <mwc-button slot="secondaryAction" dialogAction="cancel">
                    Cancel
                </mwc-button>
            </ha-dialog>
        `;
    }

    renderRemoveDialog() {
        if (!this.showRemoveDialog) return "";

        return html`
            <ha-dialog
                open
                @closed=${() => (this.showRemoveDialog = false)}
                .heading=${"Remove Code"}
            >
                <div class="dialog-content">
                    <p>Are you sure you want to remove this code?</p>
                </div>
                <mwc-button
                    slot="primaryAction"
                    @click=${() => this.removeCode(this.removingSlot)}
                >
                    Remove
                </mwc-button>
                <mwc-button slot="secondaryAction" dialogAction="cancel">
                    Cancel
                </mwc-button>
            </ha-dialog>
        `;
    }

    _handleAddSubmit() {
        const name = this.shadowRoot.getElementById("add-name").value;
        const pinCode = this.shadowRoot.getElementById("add-pin").value;
        const codeType = this.shadowRoot.getElementById("add-type").value;
        const expiry = this.shadowRoot.getElementById("add-expiry").value;
        const slot = this.shadowRoot.getElementById("add-slot").value;

        const data = {
            name: name,
            pin_code: pinCode,
            code_type: codeType,
        };

        if (expiry) {
            data.expiry = expiry;
        }

        if (slot) {
            data.slot = parseInt(slot);
        }

        this.addCode(data);
    }

    _handleEditSubmit() {
        const expiry = this.shadowRoot.getElementById("edit-expiry").value;
        this.updateExpiry(this.editingSlot, expiry || null);
    }
}

customElements.define("nimlykoder-panel", NimlykoderPanel);
