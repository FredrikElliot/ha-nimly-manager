# Nimlykoder - Home Assistant Integration

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

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu and select "Custom repositories"
4. Add repository URL: `https://github.com/FredrikElliot/ha-nimly-manager`
5. Category: Integration
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/nimlykoder` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Nimlykoder**
4. Configure the integration:
   - **Friendly Name**: Name for your integration (default: Nimlykoder)
   - **MQTT Base Topic**: MQTT topic for your Nimly lock (default: `zigbee2mqtt/nimly_lock`)
   - **Minimum Slot**: Lowest slot number (default: 0)
   - **Maximum Slot**: Highest slot number (default: 99)
   - **Reserved Slots**: Comma-separated list of reserved slots (default: 1,2,3)
   - **Auto Expire**: Enable automatic cleanup of expired guest codes (default: enabled)
   - **Cleanup Time**: Daily time for cleanup in HH:MM:SS format (default: 03:00:00)
   - **Overwrite Protection**: Prevent accidental overwrite of occupied slots (default: enabled)

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

- **Storage**: Persistent storage using Home Assistant's built-in storage system
- **MQTT Adapter**: Publishes add/remove commands to Zigbee2MQTT
- **Services**: Home Assistant service calls for automation
- **WebSocket API**: Real-time communication with the frontend
- **Scheduler**: Daily cleanup of expired guest codes
- **Panel**: Custom sidebar panel for UI

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
│       └── index.html  # Panel UI
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
