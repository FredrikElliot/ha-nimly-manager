# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-01

### Added
- Initial release of Nimlykoder integration
- Persistent storage for PIN codes (slots 0-99)
- MQTT adapter for Nimly locks via Zigbee2MQTT
- Sidebar panel UI for managing codes
- Guest codes with expiry dates
- Automatic slot allocation with reserved slot protection
- Daily cleanup scheduler for expired guest codes
- Service calls: add_code, remove_code, update_expiry, list_codes
- WebSocket API for real-time UI updates
- Full English and Swedish translations
- HACS compatibility
- Configuration flow with options
- Overwrite protection for occupied slots
- Auto-assignment of free slots
- Expired code highlighting in UI

### Features
- **Storage**: Persistent storage using Home Assistant's storage system
- **MQTT**: Seamless integration with Zigbee2MQTT for Nimly locks
- **UI**: Beautiful sidebar panel with table view and modal dialogs
- **Automation**: Full service call support for automations
- **Localization**: Automatic language selection (Swedish/English)
- **Scheduler**: Configurable daily cleanup time
- **Policy**: Reserved slots, overwrite protection, guest expiry enforcement
- **WebSocket**: Real-time bidirectional communication
