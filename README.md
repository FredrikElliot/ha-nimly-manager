# Nimlykoder - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/FredrikElliot/ha-nimly-manager.svg)](https://github.com/FredrikElliot/ha-nimly-manager/blob/main/LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/FredrikElliot/ha-nimly-manager)](https://github.com/FredrikElliot/ha-nimly-manager/releases)

A complete HACS integration for managing PIN codes on Nimly smart locks via Zigbee2MQTT.

## Features

- ✅ **Persistent Storage** - All PIN codes stored persistently across restarts
- 🔐 **MQTT Integration** - Seamless communication with Nimly locks via Zigbee2MQTT
- 🎯 **Auto Slot Assignment** - Automatic slot allocation with reserved slot protection
- ⏰ **Guest Code Expiry** - Set expiration dates for guest codes with automatic cleanup
- 🖥️ **Sidebar Panel UI** - Beautiful panel interface for managing codes
- 🌐 **Bilingual** - Full support for English and Swedish
- 🔧 **Service Calls** - Control via Home Assistant services and automations
- 📡 **WebSocket API** - Real-time updates via WebSocket commands
- 🔔 **Named Lock Activity** - Event-based lock/unlock notifications in English or Swedish, with PIN, RFID and fingerprint names

## Installation

### Quick Install via HACS (Recommended)

1. Open HACS → Integrations
2. Click three dots (⋮) → Custom repositories
3. Add: `https://github.com/FredrikElliot/ha-nimly-manager` (Integration)
4. Search "Nimlykoder" and install
5. Restart Home Assistant
6. Add integration via Settings → Devices & Services

📖 **[Detailed Installation Guide](examples/INSTALLATION.md)** - Complete step-by-step instructions

### Manual Installation

Copy `custom_components/nimlykoder/` to your Home Assistant's `custom_components` directory and restart.

## Quick Start

1. **Configure Integration**: Settings → Devices & Services → Add Integration → Nimlykoder
2. **Set MQTT Topic**: Enter your Zigbee2MQTT device topic (e.g., `zigbee2mqtt/nimly_lock`)
3. **Configure Slots**: Set slot range (0-99) and reserved slots (1-3)
4. **Access Panel**: Click "Nimlykoder" in sidebar
5. **Add First Code**: Click "Add Code" button

📘 **[Example Automations](examples/automations.md)** - Ready-to-use automation examples

## Usage

### Sidebar Panel

After installation, you'll find "Nimlykoder" in your Home Assistant sidebar. The panel shows:

- List of all configured PIN codes
- Slot number, name, type (permanent/guest), expiry, and status
- Actions to edit expiry or remove codes
- Button to add new codes

#### Adding a Code

1. Click **Add Code**
2. Enter:
   - **Name**: Friendly name for the code
   - **PIN Code**: 4-digit PIN
   - **Type**: Permanent or Guest
   - **Expiry Date**: Required for guest codes
   - **Slot**: Leave empty for auto-assignment or specify a slot number

#### Editing Expiry

1. Click **Edit** next to a code
2. Update the expiry date
3. Click **Update**

#### Removing a Code

1. Click **Remove** next to a code
2. Confirm the removal

### Services

All services are available in **Developer Tools** → **Services**:

#### `nimlykoder.add_code`

Add a new PIN code.

```yaml
service: nimlykoder.add_code
data:
  name: "Guest User"
  pin_code: "1234"
  type: guest
  expiry: "2026-12-31"
  # Optional:
  # slot: 10
  # force: false
```

#### `nimlykoder.remove_code`

Remove a PIN code.

```yaml
service: nimlykoder.remove_code
data:
  slot: 10
```

#### `nimlykoder.update_expiry`

Update expiry date for a code.

```yaml
service: nimlykoder.update_expiry
data:
  slot: 10
  expiry: "2027-01-31"  # or null to remove expiry
```

#### `nimlykoder.list_codes`

List all configured codes (returns service response).

```yaml
service: nimlykoder.list_codes
```

#### `nimlykoder.set_credential_name`

Name an existing RFID tag or fingerprint slot for activity attribution:

```yaml
service: nimlykoder.set_credential_name
data:
  method: rfid  # rfid or fingerprint
  slot: 7      # 0..65535; slot 0 can be valid
  name: "Alex"
```

An empty `name` removes the name. This stores a name only: it does **not** enroll,
modify or delete credentials on the lock. Enroll RFID tags and fingerprints using
the lock's supported procedure first. PIN attribution uses the names of existing
Nimlykoder PIN entries; it never matches PIN digits.

### Lock/unlock notifications

[Import the notification blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FFredrikElliot%2Fha-nimly-manager%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fnimlykoder%2Flock_activity.yaml)
to notify a Home Assistant Companion App device. Select the lock configured in
Nimlykoder, the phone, lock/unlock/both, automatic and unnamed-activity filters,
and English or Swedish. Disabling unnamed activity excludes **every** event
without a matched name, even manual, remote and automatic operations.
Notifications always include the localized credential/operation method, even
when a person's name is known.

The integration emits `nimlykoder_lock_activity` for fresh operation reports and
provides `last_unlocked_by` and `last_locked_by` sensors for display. Automate from
the **event**, not sensor state changes: the same person can operate the lock
repeatedly without changing a sensor's state. The blueprint queues these events.
Legacy entries without a configured lock emit `entity_id: null`; configure the
lock entity before using the blueprint.

**Requirements and replay safety:** use a recent Zigbee2MQTT **onesti** converter
that reports `action: lock` or `action: unlock` together with
`action_source_name` (and `action_user` for credential slots). Older versions
reporting only cached `last_*` values cannot provide reliable attribution:
upgrade Zigbee2MQTT. Neither cached `last_*` values nor PIN digits are used.
`self` means automatic, `zigbee` means remote, and ambiguous sources (including
model 05 ambiguity) remain unattributed. Slot 0 can be a valid credential slot.

**`advanced.last_seen` is mandatory**: without a valid report timestamp, there
are **no activity events or activity sensor updates**. Configure Zigbee2MQTT:

```yaml
# Zigbee2MQTT configuration.yaml (merge with your existing settings)
advanced:
  last_seen: ISO_8601
  cache_state_send_on_startup: false
  # Optional additional cache hardening:
  cache_state_persistent: false
devices:
  '0xYOUR_DEVICE_IEEE_ADDRESS':
    retain: false
```

`ISO_8601_local` (with a UTC offset) and `epoch` are also supported.
Retained messages and messages received during Home Assistant startup are
discarded, as are reports with missing/invalid `last_seen` or a timestamp older
than the current MQTT subscription. This rejects stale cache replays after a
restart or reload, including non-retained replays. The event timestamp is the
report's `last_seen`, normalized to UTC, not the time of receipt.
Keep `cache_state_send_on_startup: false` and device `retain: false`;
`cache_state_persistent: false` is optional extra hardening. Clear any previously
retained device-state message from the MQTT broker as well.

Duplicate reports are identified by timestamp, action, source and slot, not a
payload/time-window debounce. Identical uses with different timestamps each emit
an event. Unknown source values are sanitized to `unknown`; no arbitrary
upstream source text is exposed.

Events and notifications expose no PINs, RFID identifiers or fingerprint data;
names and activity metadata are visible to Home Assistant and notification
recipients, so treat them as personal information. HomeKit supports standard
lock-state notifications only, **not named native HomeKit notifications**.
See [event fields and a plain Home Assistant notification automation](examples/automations.md#lockunlock-activity-notifications)
for an option that needs no phone app.

### Automations

#### Auto-add guest code on calendar event

```yaml
automation:
  - alias: "Add guest code for visitor"
    trigger:
      - platform: calendar
        event: start
        entity_id: calendar.visitors
    action:
      - service: nimlykoder.add_code
        data:
          name: "{{ trigger.calendar_event.summary }}"
          pin_code: "{{ range(1000, 9999) | random }}"
          type: guest
          expiry: "{{ trigger.calendar_event.end.strftime('%Y-%m-%d') }}"
```

## Architecture

### Components

- **Storage (`storage.py`)**: Persistent storage using Home Assistant's built-in storage system
  - Schema version 1 with migration support
  - Stores slot number, name, type, expiry, timestamps
  - Async operations for all storage access
  
- **MQTT Adapter (`adapters/mqtt_z2m.py`)**: Publishes add/remove commands to Zigbee2MQTT
  - Handles communication with Nimly locks
  - Proper error handling and logging
  - Supports both add and remove operations
  
- **Services (`services.py`)**: Home Assistant service calls for automation
  - `add_code`, `remove_code`, `update_expiry`, `list_codes`, `set_credential_name`
  - Policy enforcement (guest expiry, reserved slots, overwrite protection)
  - Service response support for `list_codes`
  
- **WebSocket API (`websocket.py`)**: Real-time communication with the frontend
  - Commands: list, add, remove, update_expiry, suggest_slots
  - Bidirectional communication for live updates
  - Proper error handling with error codes
  
- **Scheduler (`__init__.py`)**: Daily cleanup of expired guest codes
  - Configurable cleanup time
  - Async job execution
  - Comprehensive logging
  
- **Panel (`panel.py`)**: Custom sidebar panel for UI
  - Registers iframe-based panel
  - Serves static frontend files
  - Integrates with HA sidebar

- **Frontend (`frontend/dist/`)**: Web component-based UI
  - Custom element (nimlykoder-panel)
  - Table view of all codes
  - Modal dialogs for add/edit/remove
  - Real-time updates via WebSocket
  - Uses Lit Element framework

### Data Flow

```
User Action (UI/Service) 
    ↓
WebSocket/Service Handler
    ↓
Policy Enforcement
    ↓
MQTT Adapter → Nimly Lock (via Zigbee2MQTT)
    ↓
Storage Update
    ↓
UI Update (WebSocket response)
```

### Slot Management

- Slots range from 0-99 (configurable)
- Reserved slots (default: 1-3) are protected from auto-assignment
- First available slot is auto-selected when not specified
- Overwrite protection prevents accidental code replacement

### Code Types

- **Permanent**: No expiry date required, remains active indefinitely
- **Guest**: Requires expiry date, automatically removed after expiration

## Localization

The integration automatically uses Swedish if your Home Assistant language is set to Swedish, otherwise English.

To change language:
1. Go to **Profile** (click your username)
2. Change **Language** setting
3. Refresh the page

## Security Considerations

### PIN Code Security

- **PIN codes are transmitted via MQTT**: Ensure your MQTT broker is secured with authentication and TLS
- **Storage encryption**: PIN codes are stored in Home Assistant's storage, protected by file system permissions
- **No PIN code logging**: PIN codes are never logged in Home Assistant logs
- **MQTT QoS 1**: Messages use Quality of Service level 1 for reliable delivery

### Best Practices

1. **Secure MQTT Broker**: 
   - Use authentication (username/password)
   - Enable TLS/SSL encryption
   - Restrict network access to MQTT broker

2. **Reserved Slots**:
   - Keep critical codes (family, emergency) in reserved slots
   - Reserved slots can't be auto-assigned or accidentally overwritten

3. **Overwrite Protection**:
   - Keep enabled to prevent accidental code replacement
   - Only disable when intentionally replacing codes

4. **Guest Code Expiry**:
   - Always set expiry dates for guest codes
   - Enable auto-cleanup to remove expired codes automatically
   - Review guest codes regularly

5. **Access Control**:
   - Only give Home Assistant access to trusted users
   - Use strong Home Assistant passwords
   - Enable two-factor authentication if available

6. **Backup**:
   - Include `.storage/nimlykoder_codes` in your backups
   - Test restore procedures
   - Keep encrypted backups off-site

## Troubleshooting

### Codes not appearing in lock

- Verify MQTT integration is installed and configured
- Check MQTT topic matches your Zigbee2MQTT device
- Check Home Assistant logs for MQTT errors

### Panel not showing

- Verify integration is installed correctly
- Restart Home Assistant
- Clear browser cache

### Expired codes not cleaning up

- Verify "Auto Expire" is enabled in options
- Check cleanup time is set correctly
- Check Home Assistant logs for scheduler errors

## Development

### Project Structure

```
custom_components/nimlykoder/
├── __init__.py           # Main integration setup
├── manifest.json         # Integration metadata
├── const.py             # Constants and defaults
├── config_flow.py       # Configuration flow
├── storage.py           # Persistent storage
├── services.py          # Service handlers
├── websocket.py         # WebSocket API
├── panel.py             # Panel registration
├── adapters/
│   └── mqtt_z2m.py     # MQTT/Zigbee2MQTT adapter
├── frontend/
│   └── dist/
│       └── nimlykoder-panel.js  # Panel web component
└── translations/
    ├── en.json         # English translations
    └── sv.json         # Swedish translations
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

Developed by Fredrik Elliot

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/FredrikElliot/ha-nimly-manager/issues).
