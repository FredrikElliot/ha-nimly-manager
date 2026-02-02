import {
    LitElement,
    html,
    css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

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
            searchQuery: { type: String },
            showAddDialog: { type: Boolean },
            showEditDialog: { type: Boolean },
            showRemoveDialog: { type: Boolean },
            editingCode: { type: Object },
            removingCode: { type: Object },
            config: { type: Object },
            showExpiredInfo: { type: Boolean },
            suggestedSlot: { type: Number },
            translations: { type: Object },
        };
    }

    constructor() {
        super();
        this.codes = [];
        this.loading = true;
        this.error = null;
        this.searchQuery = "";
        this.showAddDialog = false;
        this.showEditDialog = false;
        this.showRemoveDialog = false;
        this.editingCode = null;
        this.removingCode = null;
        this.config = { auto_expire: true, cleanup_time: "03:00:00" };
        this.showExpiredInfo = false;
        this.suggestedSlot = null;
        this.translations = this._defaultTranslations();
    }

    // Default English translations (fallback)
    _defaultTranslations() {
        return {
            title: "Nimlykoder",
            subtitle: "Manage PIN codes for your Nimly lock",
            add_code: "Add Code",
            search_placeholder: "Search by name, slot, or type...",
            stats: {
                total: "Total Codes",
                permanent: "Permanent",
                guest: "Guest",
                expired: "Expired",
            },
            status: {
                active: "Active",
                expired: "Expired",
                reserved: "Reserved",
            },
            type: {
                permanent: "Permanent",
                guest: "Guest",
            },
            dialog: {
                add_title: "Add New Person",
                edit_title: "Edit",
                remove_title: "Remove Person",
                confirm_remove: "Are you sure you want to remove",
                remove_description: "This will delete the PIN code from slot {slot} and remove it from the lock.",
                name: "Name",
                name_placeholder: "e.g., John Doe",
                pin_code: "PIN Code",
                pin_placeholder: "6 digits",
                pin_hint: "Enter a 6 digit PIN code",
                type: "Type",
                expiry: "Expiry Date",
                expiry_hint: "Leave empty for no expiry (permanent access)",
                slot: "Slot",
                next_available: "Next available",
                cancel: "Cancel",
                save: "Save Changes",
                add: "Add Person",
                remove: "Remove",
            },
            empty: {
                title: "No PIN codes yet",
                description: "Add your first person to get started with Nimlykoder",
                add_first: "Add First Person",
            },
            no_results: {
                title: "No results found",
                description: "Try a different search term",
            },
            loading: "Loading codes...",
            retry: "Retry",
            expires: "Expires",
            expired_on: "Expired",
            slot_label: "Slot",
            expired_info: {
                title: "Expired Codes",
                description: "Expired codes have passed their set expiry date and are no longer valid for entry.",
                auto_cleanup: "Auto-cleanup is enabled. Expired codes will be automatically removed at {time}.",
                manual_cleanup: "Auto-cleanup is disabled. Remove expired codes manually.",
            },
        };
    }

    static get styles() {
        return css`
            :host {
                display: block;
                --primary-color: var(--ha-primary-color, #03a9f4);
                --text-primary: var(--primary-text-color, #212121);
                --text-secondary: var(--secondary-text-color, #727272);
                --divider: var(--divider-color, #e0e0e0);
                --card-bg: var(--card-background-color, #fff);
                --bg: var(--primary-background-color, #fafafa);
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 16px;
            }

            /* Header */
            .header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 24px;
                flex-wrap: wrap;
                gap: 16px;
            }

            .header-left {
                display: flex;
                align-items: center;
                gap: 16px;
            }

            .header-icon {
                width: 48px;
                height: 48px;
                border-radius: 50%;
                background: var(--primary-color);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }

            .header-icon svg {
                width: 28px;
                height: 28px;
            }

            .header-title h1 {
                margin: 0;
                font-size: 24px;
                font-weight: 500;
                color: var(--text-primary);
            }

            .header-title p {
                margin: 4px 0 0 0;
                font-size: 14px;
                color: var(--text-secondary);
            }

            /* Search and Actions Bar */
            .toolbar {
                display: flex;
                gap: 12px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }

            .search-container {
                flex: 1;
                min-width: 200px;
                position: relative;
            }

            .search-input {
                width: 100%;
                padding: 12px 16px 12px 44px;
                border: 1px solid var(--divider);
                border-radius: 28px;
                font-size: 16px;
                background: var(--card-bg);
                color: var(--text-primary);
                outline: none;
                transition: border-color 0.2s, box-shadow 0.2s;
                box-sizing: border-box;
            }

            .search-input:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 1px var(--primary-color);
            }

            .search-input::placeholder {
                color: var(--text-secondary);
            }

            .search-icon {
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                color: var(--text-secondary);
                pointer-events: none;
            }

            /* Buttons */
            .btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 12px 24px;
                border: none;
                border-radius: 28px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .btn-primary {
                background: var(--primary-color);
                color: var(--text-primary-color, white);
                box-shadow: 0 2px 8px rgba(var(--rgb-primary-color, 3, 169, 244), 0.4);
            }

            .btn-primary:hover {
                filter: brightness(1.1);
                box-shadow: 0 4px 16px rgba(var(--rgb-primary-color, 3, 169, 244), 0.5);
                transform: translateY(-1px);
            }

            .btn-secondary {
                background: var(--card-bg);
                color: var(--text-primary);
                border: 1px solid var(--divider);
            }

            .btn-secondary:hover {
                background: var(--bg);
            }

            .btn-danger {
                background: #f44336;
                color: white;
            }

            .btn-danger:hover {
                background: #d32f2f;
            }

            .btn-text {
                background: transparent;
                color: var(--primary-color);
                padding: 8px 16px;
            }

            .btn-text:hover {
                background: rgba(3, 169, 244, 0.1);
            }

            .btn-icon {
                width: 40px;
                height: 40px;
                padding: 0;
                border-radius: 50%;
                justify-content: center;
            }

            .btn svg {
                width: 20px;
                height: 20px;
                flex-shrink: 0;
            }

            /* Stats Cards */
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 16px;
                margin-bottom: 24px;
            }

            .stat-card {
                background: var(--card-bg);
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }

            .stat-value {
                font-size: 32px;
                font-weight: 600;
                color: var(--text-primary);
            }

            .stat-label {
                font-size: 13px;
                color: var(--text-secondary);
                margin-top: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .stat-header {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }

            .info-icon {
                width: 20px;
                height: 20px;
                color: var(--text-secondary);
                cursor: pointer;
                transition: color 0.2s;
            }

            .info-icon:hover {
                color: var(--primary-color);
            }

            .stat-card.expired {
                position: relative;
            }

            /* Info Tooltip */
            .info-tooltip {
                position: absolute;
                bottom: calc(100% + 12px);
                left: 50%;
                transform: translateX(-50%);
                background: var(--card-bg);
                border: 1px solid var(--divider);
                border-radius: 12px;
                padding: 16px;
                width: 280px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                z-index: 100;
                text-align: left;
            }

            .info-tooltip::after {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                border: 8px solid transparent;
                border-top-color: var(--card-bg);
            }

            .info-tooltip::before {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                border: 9px solid transparent;
                border-top-color: var(--divider);
            }

            .info-tooltip h4 {
                margin: 0 0 8px 0;
                font-size: 14px;
                font-weight: 600;
                color: var(--text-primary);
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .info-tooltip h4 svg {
                width: 18px;
                height: 18px;
                color: #f44336;
            }

            .info-tooltip p {
                margin: 0;
                font-size: 13px;
                color: var(--text-secondary);
                line-height: 1.5;
            }

            .info-tooltip .highlight {
                color: var(--primary-color);
                font-weight: 500;
            }

            .stat-card.permanent .stat-value { color: #4caf50; }
            .stat-card.guest .stat-value { color: #2196f3; }
            .stat-card.expired .stat-value { color: #f44336; }

            /* Person List */
            .person-list {
                display: grid;
                gap: 12px;
            }

            .person-card {
                background: var(--card-bg);
                border-radius: 16px;
                padding: 16px 20px;
                display: flex;
                align-items: center;
                gap: 16px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                transition: box-shadow 0.2s, transform 0.2s;
            }

            .person-card:hover {
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }

            .person-avatar {
                width: 52px;
                height: 52px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                font-weight: 600;
                color: white;
                flex-shrink: 0;
            }

            .avatar-permanent {
                background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
            }

            .avatar-guest {
                background: linear-gradient(135deg, #2196f3 0%, #1565c0 100%);
            }

            .avatar-expired {
                background: linear-gradient(135deg, #9e9e9e 0%, #616161 100%);
            }

            .person-info {
                flex: 1;
                min-width: 0;
            }

            .person-name {
                font-size: 16px;
                font-weight: 500;
                color: var(--text-primary);
                margin: 0 0 4px 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .person-details {
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
            }

            .person-detail {
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 13px;
                color: var(--text-secondary);
            }

            .person-detail svg {
                width: 16px;
                height: 16px;
                opacity: 0.7;
            }

            .badge {
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .badge-permanent {
                background: #e8f5e9;
                color: #2e7d32;
            }

            .badge-guest {
                background: #e3f2fd;
                color: #1565c0;
            }

            .badge-expired {
                background: #ffebee;
                color: #c62828;
            }

            .person-actions {
                display: flex;
                gap: 8px;
            }

            /* Empty State */
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                background: var(--card-bg);
                border-radius: 16px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            }

            .empty-icon {
                width: 80px;
                height: 80px;
                margin: 0 auto 20px;
                background: var(--primary-color);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }

            .empty-icon svg {
                width: 40px;
                height: 40px;
            }

            .empty-state h2 {
                margin: 0 0 8px 0;
                font-size: 20px;
                font-weight: 500;
                color: var(--text-primary);
            }

            .empty-state p {
                margin: 0 0 24px 0;
                color: var(--text-secondary);
            }

            /* Loading */
            .loading-container {
                text-align: center;
                padding: 60px 20px;
            }

            .spinner {
                width: 48px;
                height: 48px;
                border: 3px solid var(--divider);
                border-top-color: var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 16px;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Error */
            .error-banner {
                background: #ffebee;
                color: #c62828;
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .error-banner svg {
                width: 24px;
                height: 24px;
                flex-shrink: 0;
            }

            .error-banner span {
                flex: 1;
            }

            /* Dialog Overlay */
            .dialog-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                padding: 16px;
            }

            .dialog {
                background: var(--card-bg);
                border-radius: 16px;
                width: 100%;
                max-width: 480px;
                max-height: 90vh;
                overflow: auto;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }

            .dialog-header {
                padding: 20px 24px;
                border-bottom: 1px solid var(--divider);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .dialog-header h2 {
                margin: 0;
                font-size: 20px;
                font-weight: 500;
            }

            .dialog-content {
                padding: 24px;
            }

            .dialog-actions {
                padding: 16px 24px;
                border-top: 1px solid var(--divider);
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }

            /* Form */
            .form-group {
                margin-bottom: 20px;
            }

            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-size: 14px;
                font-weight: 500;
                color: var(--text-primary);
            }

            .form-group input,
            .form-group select {
                width: 100%;
                padding: 12px 16px;
                border: 1px solid var(--divider);
                border-radius: 8px;
                font-size: 16px;
                background: var(--bg);
                color: var(--text-primary);
                outline: none;
                transition: border-color 0.2s;
                box-sizing: border-box;
            }

            .form-group input:focus,
            .form-group select:focus {
                border-color: var(--primary-color);
            }

            .form-group small {
                display: block;
                margin-top: 6px;
                font-size: 12px;
                color: var(--text-secondary);
            }

            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }

            /* Responsive */
            @media (max-width: 600px) {
                .header {
                    flex-direction: column;
                    align-items: flex-start;
                }

                .toolbar {
                    flex-direction: column;
                }

                .search-container {
                    width: 100%;
                }

                .person-card {
                    flex-wrap: wrap;
                }

                .person-actions {
                    width: 100%;
                    justify-content: flex-end;
                    margin-top: 8px;
                    padding-top: 12px;
                    border-top: 1px solid var(--divider);
                }

                .form-row {
                    grid-template-columns: 1fr;
                }

                .stats {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        `;
    }

    connectedCallback() {
        super.connectedCallback();
        this.loadTranslations();
        this.loadCodes();
        this.loadConfig();
    }

    async loadCodes() {
        try {
            this.loading = true;
            this.error = null;
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

    async loadConfig() {
        try {
            const result = await this.hass.callWS({
                type: "nimlykoder/config",
            });
            this.config = result;
        } catch (err) {
            console.error("Failed to load config:", err);
        }
    }

    async loadTranslations() {
        try {
            const result = await this.hass.callWS({
                type: "nimlykoder/translations",
            });
            if (result && result.translations) {
                // Deep merge with defaults
                this.translations = this._mergeTranslations(this._defaultTranslations(), result.translations);
            }
        } catch (err) {
            console.error("Failed to load translations:", err);
            // Keep default translations
        }
    }

    _mergeTranslations(defaults, loaded) {
        const result = { ...defaults };
        for (const key of Object.keys(loaded)) {
            if (typeof loaded[key] === 'object' && loaded[key] !== null && !Array.isArray(loaded[key])) {
                result[key] = this._mergeTranslations(defaults[key] || {}, loaded[key]);
            } else {
                result[key] = loaded[key];
            }
        }
        return result;
    }

    // Translation helper: t("dialog.cancel") -> this.translations.dialog.cancel
    t(path, replacements = {}) {
        const keys = path.split('.');
        let value = this.translations;
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return path; // Return the path as fallback
            }
        }
        // Apply replacements like {slot} -> actual value
        if (typeof value === 'string') {
            for (const [k, v] of Object.entries(replacements)) {
                value = value.replace(`{${k}}`, v);
            }
        }
        return value;
    }

    get cleanupTimeFormatted() {
        const time = this.config?.cleanup_time || "03:00:00";
        const [hours, minutes] = time.split(":");
        const hour = parseInt(hours);
        const min = minutes || "00";
        if (hour === 0) return `12:${min} AM`;
        if (hour < 12) return `${hour}:${min} AM`;
        if (hour === 12) return `12:${min} PM`;
        return `${hour - 12}:${min} PM`;
    }

    get filteredCodes() {
        if (!this.searchQuery) return this.codes;
        const query = this.searchQuery.toLowerCase();
        return this.codes.filter(
            (code) =>
                code.name.toLowerCase().includes(query) ||
                code.slot.toString().includes(query) ||
                code.type.toLowerCase().includes(query)
        );
    }

    get stats() {
        const total = this.codes.length;
        const permanent = this.codes.filter((c) => c.type === "permanent").length;
        const guest = this.codes.filter((c) => c.type === "guest").length;
        const expired = this.codes.filter(
            (c) => c.expiry && new Date(c.expiry) < new Date()
        ).length;
        return { total, permanent, guest, expired };
    }

    getInitials(name) {
        return name
            .split(" ")
            .map((n) => n[0])
            .join("")
            .toUpperCase()
            .slice(0, 2);
    }

    isExpired(code) {
        return code.expiry && new Date(code.expiry) < new Date();
    }

    getAvatarClass(code) {
        if (this.isExpired(code)) return "avatar-expired";
        return code.type === "permanent" ? "avatar-permanent" : "avatar-guest";
    }

    getBadgeClass(code) {
        if (this.isExpired(code)) return "badge-expired";
        return code.type === "permanent" ? "badge-permanent" : "badge-guest";
    }

    getBadgeText(code) {
        if (this.isExpired(code)) return this.t('status.expired');
        return code.type === "permanent" ? this.t('type.permanent') : this.t('type.guest');
    }

    formatDate(dateStr) {
        if (!dateStr) return "—";
        const date = new Date(dateStr);
        return date.toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    }

    render() {
        return html`
            <div class="container">
                ${this._renderHeader()}
                ${this.error ? this._renderError() : ""}
                ${this.loading
                    ? this._renderLoading()
                    : html`
                          ${this._renderStats()}
                          ${this._renderToolbar()}
                          ${this._renderPersonList()}
                      `}
                ${this.showAddDialog ? this._renderAddDialog() : ""}
                ${this.showEditDialog ? this._renderEditDialog() : ""}
                ${this.showRemoveDialog ? this._renderRemoveDialog() : ""}
            </div>
        `;
    }

    _renderHeader() {
        return html`
            <div class="header">
                <div class="header-left">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
                        </svg>
                    </div>
                    <div class="header-title">
                        <h1>${this.t('title')}</h1>
                        <p>${this.t('subtitle')}</p>
                    </div>
                </div>
            </div>
        `;
    }

    _renderStats() {
        const { total, permanent, guest, expired } = this.stats;
        const autoExpireEnabled = this.config?.auto_expire !== false;
        
        return html`
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">${total}</div>
                    <div class="stat-label">${this.t('stats.total')}</div>
                </div>
                <div class="stat-card permanent">
                    <div class="stat-value">${permanent}</div>
                    <div class="stat-label">${this.t('stats.permanent')}</div>
                </div>
                <div class="stat-card guest">
                    <div class="stat-value">${guest}</div>
                    <div class="stat-label">${this.t('stats.guest')}</div>
                </div>
                <div class="stat-card expired">
                    <div class="stat-header">
                        <div class="stat-value">${expired}</div>
                        <svg 
                            class="info-icon" 
                            viewBox="0 0 24 24" 
                            fill="currentColor"
                            @click=${(e) => { e.stopPropagation(); this.showExpiredInfo = !this.showExpiredInfo; }}
                            @mouseenter=${() => this.showExpiredInfo = true}
                            @mouseleave=${() => this.showExpiredInfo = false}
                        >
                            <path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
                        </svg>
                    </div>
                    <div class="stat-label">${this.t('stats.expired')}</div>
                    ${this.showExpiredInfo ? html`
                        <div class="info-tooltip">
                            <h4>
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z"/>
                                </svg>
                                ${this.t('expired_info.title')}
                            </h4>
                            <p>
                                ${this.t('expired_info.description')}
                                ${autoExpireEnabled 
                                    ? html`<br><br>${this.t('expired_info.auto_cleanup', { time: this.cleanupTimeFormatted })}`
                                    : html`<br><br>${this.t('expired_info.manual_cleanup')}`
                                }
                            </p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    _renderToolbar() {
        return html`
            <div class="toolbar">
                <div class="search-container">
                    <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z"/>
                    </svg>
                    <input
                        type="text"
                        class="search-input"
                        placeholder="${this.t('search_placeholder')}"
                        .value=${this.searchQuery}
                        @input=${(e) => (this.searchQuery = e.target.value)}
                    />
                </div>
                <button class="btn btn-primary" @click=${() => this._openAddDialog()}>
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
                    </svg>
                    ${this.t('add_code')}
                </button>
            </div>
        `;
    }

    _renderPersonList() {
        const codes = this.filteredCodes;

        if (this.codes.length === 0) {
            return this._renderEmptyState();
        }

        if (codes.length === 0) {
            return html`
                <div class="empty-state">
                    <h2>${this.t('no_results.title')}</h2>
                    <p>${this.t('no_results.description')}</p>
                </div>
            `;
        }

        return html`
            <div class="person-list">
                ${codes.map((code) => this._renderPersonCard(code))}
            </div>
        `;
    }

    _renderPersonCard(code) {
        return html`
            <div class="person-card">
                <div class="person-avatar ${this.getAvatarClass(code)}">
                    ${this.getInitials(code.name)}
                </div>
                <div class="person-info">
                    <h3 class="person-name">${code.name}</h3>
                    <div class="person-details">
                        <span class="person-detail">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,5A3,3 0 0,1 15,8A3,3 0 0,1 12,11A3,3 0 0,1 9,8A3,3 0 0,1 12,5M17.13,17C15.92,18.85 14.11,20.24 12,20.92C9.89,20.24 8.08,18.85 6.87,17C6.53,16.5 6.24,16 6,15.47C6,13.82 8.71,12.47 12,12.47C15.29,12.47 18,13.79 18,15.47C17.76,16 17.47,16.5 17.13,17Z"/>
                            </svg>
                            ${this.t('slot_label')} ${code.slot}
                        </span>
                        ${code.expiry
                            ? html`
                                  <span class="person-detail">
                                      <svg viewBox="0 0 24 24" fill="currentColor">
                                          <path d="M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z"/>
                                      </svg>
                                      ${this.isExpired(code) ? this.t('expired_on') : this.t('expires')} ${this.formatDate(code.expiry)}
                                  </span>
                              `
                            : ""}
                    </div>
                </div>
                <span class="badge ${this.getBadgeClass(code)}">${this.getBadgeText(code)}</span>
                <div class="person-actions">
                    <button
                        class="btn btn-icon btn-secondary"
                        @click=${() => {
                            this.editingCode = code;
                            this.showEditDialog = true;
                        }}
                        title="${this.t('dialog.edit_title')}"
                    >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z"/>
                        </svg>
                    </button>
                    <button
                        class="btn btn-icon btn-secondary"
                        @click=${() => {
                            this.removingCode = code;
                            this.showRemoveDialog = true;
                        }}
                        title="${this.t('dialog.remove')}"
                    >
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }

    _renderEmptyState() {
        return html`
            <div class="empty-state">
                <div class="empty-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
                    </svg>
                </div>
                <h2>${this.t('empty.title')}</h2>
                <p>${this.t('empty.description')}</p>
                <button class="btn btn-primary" @click=${() => this._openAddDialog()}>
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
                    </svg>
                    ${this.t('empty.add_first')}
                </button>
            </div>
        `;
    }

    _renderLoading() {
        return html`
            <div class="loading-container">
                <div class="spinner"></div>
                <p>${this.t('loading')}</p>
            </div>
        `;
    }

    _renderError() {
        return html`
            <div class="error-banner">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
                </svg>
                <span>${this.error}</span>
                <button class="btn btn-text" @click=${() => this.loadCodes()}>${this.t('retry')}</button>
            </div>
        `;
    }

    _renderAddDialog() {
        return html`
            <div class="dialog-overlay" @click=${this._closeAddDialog}>
                <div class="dialog" @click=${(e) => e.stopPropagation()}>
                    <div class="dialog-header">
                        <h2>${this.t('dialog.add_title')}</h2>
                        <button class="btn btn-icon btn-text" @click=${this._closeAddDialog}>
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="dialog-content" @click=${(e) => e.stopPropagation()}>
                        <div class="form-group">
                            <label for="add-name">${this.t('dialog.name')} *</label>
                            <input type="text" id="add-name" placeholder="${this.t('dialog.name_placeholder')}" required />
                        </div>
                        <div class="form-group">
                            <label for="add-pin">${this.t('dialog.pin_code')} *</label>
                            <input type="password" id="add-pin" placeholder="${this.t('dialog.pin_placeholder')}" pattern="[0-9]{6}" maxlength="6" required />
                            <small>${this.t('dialog.pin_hint')}</small>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="add-type">${this.t('dialog.type')} *</label>
                                <select id="add-type" @change=${this._onTypeChange} @click=${(e) => e.stopPropagation()}>
                                    <option value="permanent">${this.t('type.permanent')}</option>
                                    <option value="guest">${this.t('type.guest')}</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="add-slot">${this.t('dialog.slot')}</label>
                                <input type="number" id="add-slot" min="0" max="99" .value=${this.suggestedSlot !== null ? String(this.suggestedSlot) : ""} />
                                <small>${this.t('dialog.next_available')}: ${this.suggestedSlot !== null ? this.suggestedSlot : "..."}</small>
                            </div>
                        </div>
                        <div class="form-group" id="expiry-group" style="display: none;">
                            <label for="add-expiry">${this.t('dialog.expiry')}</label>
                            <input type="date" id="add-expiry" />
                        </div>
                    </div>
                    <div class="dialog-actions">
                        <button class="btn btn-secondary" @click=${this._closeAddDialog}>${this.t('dialog.cancel')}</button>
                        <button class="btn btn-primary" @click=${this._handleAddSubmit}>${this.t('dialog.add')}</button>
                    </div>
                </div>
            </div>
        `;
    }

    _renderEditDialog() {
        if (!this.editingCode) return "";
        return html`
            <div class="dialog-overlay" @click=${this._closeEditDialog}>
                <div class="dialog" @click=${(e) => e.stopPropagation()}>
                    <div class="dialog-header">
                        <h2>${this.t('dialog.edit_title')} ${this.editingCode.name}</h2>
                        <button class="btn btn-icon btn-text" @click=${this._closeEditDialog}>
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="dialog-content">
                        <div class="form-group">
                            <label for="edit-expiry">${this.t('dialog.expiry')}</label>
                            <input type="date" id="edit-expiry" .value=${this.editingCode.expiry || ""} />
                            <small>${this.t('dialog.expiry_hint')}</small>
                        </div>
                    </div>
                    <div class="dialog-actions">
                        <button class="btn btn-secondary" @click=${this._closeEditDialog}>${this.t('dialog.cancel')}</button>
                        <button class="btn btn-primary" @click=${this._handleEditSubmit}>${this.t('dialog.save')}</button>
                    </div>
                </div>
            </div>
        `;
    }

    _renderRemoveDialog() {
        if (!this.removingCode) return "";
        return html`
            <div class="dialog-overlay" @click=${this._closeRemoveDialog}>
                <div class="dialog" @click=${(e) => e.stopPropagation()}>
                    <div class="dialog-header">
                        <h2>${this.t('dialog.remove_title')}</h2>
                        <button class="btn btn-icon btn-text" @click=${this._closeRemoveDialog}>
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="dialog-content">
                        <p>${this.t('dialog.confirm_remove')} <strong>${this.removingCode.name}</strong>?</p>
                        <p style="margin-top: 12px; color: var(--text-secondary); font-size: 14px;">
                            ${this.t('dialog.remove_description', { slot: this.removingCode.slot })}
                        </p>
                    </div>
                    <div class="dialog-actions">
                        <button class="btn btn-secondary" @click=${this._closeRemoveDialog}>${this.t('dialog.cancel')}</button>
                        <button class="btn btn-danger" @click=${this._handleRemove}>${this.t('dialog.remove')}</button>
                    </div>
                </div>
            </div>
        `;
    }

    _onTypeChange(e) {
        const expiryGroup = this.shadowRoot.getElementById("expiry-group");
        if (expiryGroup) {
            expiryGroup.style.display = e.target.value === "guest" ? "block" : "none";
        }
    }

    async _openAddDialog() {
        // Fetch the next available slot
        try {
            const result = await this.hass.callWS({
                type: "nimlykoder/suggest_slots",
                count: 1,
            });
            this.suggestedSlot = result.slots && result.slots.length > 0 ? result.slots[0] : null;
        } catch (err) {
            console.error("Failed to fetch suggested slot:", err);
            this.suggestedSlot = null;
        }
        this.showAddDialog = true;
    }

    _closeAddDialog() {
        this.showAddDialog = false;
        this.suggestedSlot = null;
    }

    _closeEditDialog() {
        this.showEditDialog = false;
        this.editingCode = null;
    }

    _closeRemoveDialog() {
        this.showRemoveDialog = false;
        this.removingCode = null;
    }

    async _handleAddSubmit() {
        const name = this.shadowRoot.getElementById("add-name").value;
        const pinCode = this.shadowRoot.getElementById("add-pin").value;
        const codeType = this.shadowRoot.getElementById("add-type").value;
        const expiry = this.shadowRoot.getElementById("add-expiry").value;
        const slot = this.shadowRoot.getElementById("add-slot").value;

        if (!name || !pinCode) {
            this.error = "Please fill in all required fields";
            return;
        }

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

    async _handleEditSubmit() {
        const expiry = this.shadowRoot.getElementById("edit-expiry").value;

        try {
            await this.hass.callWS({
                type: "nimlykoder/update_expiry",
                slot: this.editingCode.slot,
                expiry: expiry || null,
            });
            this.showEditDialog = false;
            this.editingCode = null;
            await this.loadCodes();
        } catch (err) {
            this.error = err.message;
        }
    }

    async _handleRemove() {
        try {
            await this.hass.callWS({
                type: "nimlykoder/remove",
                slot: this.removingCode.slot,
            });
            this.showRemoveDialog = false;
            this.removingCode = null;
            await this.loadCodes();
        } catch (err) {
            this.error = err.message;
        }
    }
}

customElements.define("nimlykoder-panel", NimlykoderPanel);
