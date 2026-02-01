"""Constants for the Nimlykoder integration."""

DOMAIN = "nimlykoder"

# Configuration keys
CONF_MQTT_TOPIC = "mqtt_topic"
CONF_SLOT_MIN = "slot_min"
CONF_SLOT_MAX = "slot_max"
CONF_RESERVED_SLOTS = "reserved_slots"
CONF_AUTO_EXPIRE = "auto_expire"
CONF_CLEANUP_TIME = "cleanup_time"
CONF_OVERWRITE_PROTECTION = "overwrite_protection"

# Defaults
DEFAULT_SLOT_MIN = 0
DEFAULT_SLOT_MAX = 99
DEFAULT_RESERVED_SLOTS = [1, 2, 3]
DEFAULT_AUTO_EXPIRE = True
DEFAULT_CLEANUP_TIME = "03:00:00"
DEFAULT_OVERWRITE_PROTECTION = True
DEFAULT_MQTT_TOPIC = "zigbee2mqtt/nimly_lock"

# Storage
STORAGE_VERSION = 1
STORAGE_KEY = "nimlykoder_codes"

# Entry types
TYPE_PERMANENT = "permanent"
TYPE_GUEST = "guest"

# Services
SERVICE_ADD_CODE = "add_code"
SERVICE_REMOVE_CODE = "remove_code"
SERVICE_UPDATE_EXPIRY = "update_expiry"
SERVICE_LIST_CODES = "list_codes"

# WebSocket commands
WS_TYPE_LIST = "nimlykoder/list"
WS_TYPE_ADD = "nimlykoder/add"
WS_TYPE_REMOVE = "nimlykoder/remove"
WS_TYPE_UPDATE_EXPIRY = "nimlykoder/update_expiry"
WS_TYPE_SUGGEST_SLOTS = "nimlykoder/suggest_slots"
WS_TYPE_CONFIG = "nimlykoder/config"

# Panel
PANEL_NAME = "nimlykoder"
PANEL_TITLE = "Nimlykoder"
PANEL_ICON = "mdi:door-closed-lock"
PANEL_URL = "/api/panel_custom/nimlykoder"
