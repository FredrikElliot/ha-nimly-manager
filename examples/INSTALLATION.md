# Installation Guide

This guide will walk you through installing and configuring the Nimlykoder integration.

## Prerequisites

Before installing Nimlykoder, ensure you have:

1. **Home Assistant** (version 2023.1 or later)
2. **MQTT Integration** installed and configured
3. **Zigbee2MQTT** set up and connected to your Nimly lock
4. **HACS** (Home Assistant Community Store) installed (recommended method)

## Method 1: HACS Installation (Recommended)

### Step 1: Add Custom Repository

1. Open **HACS** in Home Assistant
2. Click on **Integrations**
3. Click the **three dots menu** (⋮) in the top right
4. Select **Custom repositories**
5. Add the repository:
   - **URL**: `https://github.com/FredrikElliot/ha-nimly-manager`
   - **Category**: Integration
6. Click **Add**

### Step 2: Install Integration

1. Search for "Nimlykoder" in HACS
2. Click on the integration
3. Click **Download**
4. Restart Home Assistant

### Step 3: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** (+ button in bottom right)
3. Search for "Nimlykoder"
4. Click on it to start configuration

### Step 4: Configure

Fill in the configuration form:

- **Friendly Name**: Leave as "Nimlykoder" or customize
- **MQTT Base Topic**: The MQTT topic for your Nimly lock
  - Find this in Zigbee2MQTT (usually `zigbee2mqtt/YOUR_DEVICE_NAME`)
  - Example: `zigbee2mqtt/nimly_lock`
- **Minimum Slot**: `0` (or your preferred minimum)
- **Maximum Slot**: `99` (or your preferred maximum)
- **Reserved Slots**: `1,2,3` (comma-separated, no spaces)
  - These slots won't be auto-assigned
- **Enable Auto Expire**: Check to enable automatic cleanup
- **Cleanup Time**: `03:00:00` (HH:MM:SS format, when to run daily cleanup)
- **Overwrite Protection**: Check to prevent accidental overwrites

Click **Submit** to complete setup.

## Method 2: Manual Installation

### Step 1: Download Files

1. Download the latest release from [GitHub Releases](https://github.com/FredrikElliot/ha-nimly-manager/releases)
2. Extract the archive

### Step 2: Copy Files

Copy the `custom_components/nimlykoder` folder to your Home Assistant's `custom_components` directory:

```bash
# If using SSH/terminal access
scp -r custom_components/nimlykoder user@homeassistant:/config/custom_components/

# Or using Samba/file share
# Copy to: /config/custom_components/nimlykoder
```

Your directory structure should look like:
```
config/
├── custom_components/
│   └── nimlykoder/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       └── ... (other files)
```

### Step 3: Restart Home Assistant

Restart Home Assistant to load the new integration.

### Step 4: Add Integration

Follow steps 3-4 from the HACS method above.

## Finding Your MQTT Topic

### Using Zigbee2MQTT Web Interface

1. Open Zigbee2MQTT web interface (usually `http://homeassistant:8099`)
2. Click on your Nimly lock device
3. Look for the **MQTT** topic at the top
4. Copy the base topic (without `/set` or `/get`)

### Using MQTT Explorer

1. Install an MQTT explorer tool (e.g., MQTT Explorer desktop app)
2. Connect to your MQTT broker
3. Look for topics starting with `zigbee2mqtt/`
4. Find your Nimly lock device
5. Use the base topic path

### Using Home Assistant MQTT Integration

1. Go to **Developer Tools** → **MQTT**
2. Click **Listen to a topic**
3. Enter: `zigbee2mqtt/#`
4. Click **Start Listening**
5. Interact with your lock to see messages
6. Note the topic path for your device

## Verifying Installation

### Check Integration Status

1. Go to **Settings** → **Devices & Services**
2. Find "Nimlykoder" in the list
3. Should show as "Configured" with no errors

### Check Sidebar Panel

1. Look for "Nimlykoder" in the sidebar (left menu)
2. Click it to open the management panel
3. Should see an empty table with "Add Code" button

### Test Service

1. Go to **Developer Tools** → **Services**
2. Select service: `nimlykoder.list_codes`
3. Click **Call Service**
4. Should return an empty list or existing codes

## Troubleshooting Installation

### Integration Not Found

**Problem**: Can't find Nimlykoder when adding integration

**Solutions**:
1. Verify files are in correct location
2. Check `custom_components/nimlykoder/manifest.json` exists
3. Restart Home Assistant
4. Clear browser cache (Ctrl+F5 or Cmd+Shift+R)

### MQTT Connection Issues

**Problem**: Can't connect to MQTT or codes not syncing to lock

**Solutions**:
1. Verify MQTT integration is installed and working
2. Test MQTT manually in Developer Tools
3. Check Zigbee2MQTT logs for errors
4. Verify MQTT topic is correct
5. Check MQTT broker is running

### Panel Not Showing

**Problem**: Sidebar panel doesn't appear

**Solutions**:
1. Restart Home Assistant
2. Clear browser cache
3. Check browser console for errors (F12)
4. Verify frontend files are in `custom_components/nimlykoder/frontend/dist/`

### Configuration Errors

**Problem**: Error when configuring integration

**Solutions**:
1. Check slot range (min must be < max)
2. Verify reserved slots are comma-separated numbers
3. Ensure cleanup time is in HH:MM:SS format
4. Check Home Assistant logs for detailed error

### Viewing Logs

To see detailed logs:

1. Go to **Settings** → **System** → **Logs**
2. Search for "nimlykoder"
3. Or check `config/home-assistant.log` file

Enable debug logging in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.nimlykoder: debug
```

## Post-Installation Steps

### 1. Add Your First Code

1. Open Nimlykoder panel from sidebar
2. Click **Add Code**
3. Fill in details:
   - Name: Your name or "Test Code"
   - PIN: 4-digit number (e.g., 1234)
   - Type: Permanent or Guest
   - Expiry: Only for guest codes
4. Click **Save**

### 2. Verify Lock

1. Go to your physical lock
2. Try the PIN code you just added
3. Should unlock the door

### 3. Set Up Automations

See [examples/automations.md](../examples/automations.md) for automation ideas.

### 4. Configure Options (Optional)

To change settings after installation:

1. Go to **Settings** → **Devices & Services**
2. Find Nimlykoder
3. Click **Configure** or **Options**
4. Update settings as needed
5. Click **Submit**

## Upgrading

### Via HACS

1. HACS will notify when updates are available
2. Click **Update** in HACS
3. Restart Home Assistant

### Manual Upgrade

1. Download new version
2. Replace files in `custom_components/nimlykoder/`
3. Restart Home Assistant

## Uninstalling

### Remove Integration

1. Go to **Settings** → **Devices & Services**
2. Find Nimlykoder
3. Click the three dots menu (⋮)
4. Select **Delete**
5. Confirm deletion

### Remove Files (Optional)

If not reinstalling:

1. Delete `custom_components/nimlykoder/` folder
2. Restart Home Assistant

**Note**: Removing the integration will delete all stored PIN code data.

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting section in README](../README.md#troubleshooting)
2. Review [GitHub Issues](https://github.com/FredrikElliot/ha-nimly-manager/issues)
3. Create a new issue with:
   - Home Assistant version
   - Integration version
   - Error messages from logs
   - Steps to reproduce

## Next Steps

- Read the [README](../README.md) for usage instructions
- Explore [example automations](automations.md)
- Check the [CHANGELOG](../CHANGELOG.md) for version history
