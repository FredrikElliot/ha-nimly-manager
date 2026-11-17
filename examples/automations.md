# Example Automations for Nimlykoder

This file contains example automations to help you get started with the Nimlykoder integration.

## Add Guest Code on Calendar Event

Automatically add a guest code when a calendar event starts:

```yaml
automation:
  - alias: "Add guest code for visitor"
    description: "Automatically add guest code when visitor event starts"
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

## Notify on Guest Code Added

Send notification when a guest code is added:

```yaml
automation:
  - alias: "Notify on guest code added"
    description: "Send notification when new guest code is added"
    trigger:
      - platform: event
        event_type: service_executed
        event_data:
          domain: nimlykoder
          service: add_code
    action:
      - service: notify.mobile_app
        data:
          title: "Guest Code Added"
          message: "New guest code '{{ trigger.event.data.service_data.name }}' added to slot {{ trigger.event.data.service_data.slot | default('auto') }}"
```

## Auto-Remove Expired Codes (Manual)

While the integration has automatic cleanup, you can also manually trigger it:

```yaml
automation:
  - alias: "Manual expired code cleanup"
    description: "Check and remove expired codes daily"
    trigger:
      - platform: time
        at: "04:00:00"
    action:
      - service: nimlykoder.list_codes
        response_variable: codes
      - repeat:
          for_each: "{{ codes.codes | selectattr('type', 'equalto', 'guest') | selectattr('expiry', 'defined') | list }}"
          sequence:
            - condition: template
              value_template: "{{ as_timestamp(repeat.item.expiry) < as_timestamp(now()) }}"
            - service: nimlykoder.remove_code
              data:
                slot: "{{ repeat.item.slot }}"
```

## Add Permanent Family Code

Add a permanent code for family members:

```yaml
automation:
  - alias: "Add family member code"
    description: "Add permanent code for family member"
    trigger:
      - platform: state
        entity_id: input_boolean.add_family_code
        to: "on"
    action:
      - service: nimlykoder.add_code
        data:
          name: "{{ states('input_text.family_member_name') }}"
          pin_code: "{{ states('input_text.family_member_pin') }}"
          type: permanent
      - service: input_boolean.turn_off
        entity_id: input_boolean.add_family_code
```

## Weekly Code Rotation

Rotate a temporary code weekly:

```yaml
automation:
  - alias: "Weekly code rotation"
    description: "Rotate cleaning crew code every Monday"
    trigger:
      - platform: time
        at: "06:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      # Remove old code
      - service: nimlykoder.remove_code
        data:
          slot: 10
      # Add new code
      - service: nimlykoder.add_code
        data:
          name: "Cleaning Crew"
          pin_code: "{{ range(1000, 9999) | random }}"
          type: guest
          expiry: "{{ (now() + timedelta(days=7)).strftime('%Y-%m-%d') }}"
          slot: 10
          force: true
      # Notify
      - service: notify.cleaning_crew
        data:
          title: "New Access Code"
          message: "Your new access code is {{ range(1000, 9999) | random }}, valid until next Monday"
```

## Extend Guest Code Expiry

Extend the expiry of a guest code:

```yaml
automation:
  - alias: "Extend guest code"
    description: "Extend guest code expiry by 7 days"
    trigger:
      - platform: state
        entity_id: input_boolean.extend_guest_code
        to: "on"
    action:
      - service: nimlykoder.update_expiry
        data:
          slot: "{{ states('input_number.guest_code_slot') | int }}"
          expiry: "{{ (now() + timedelta(days=7)).strftime('%Y-%m-%d') }}"
      - service: input_boolean.turn_off
        entity_id: input_boolean.extend_guest_code
```

## Vacation Mode - Add Temporary Code

Add a temporary code when vacation mode is activated:

```yaml
automation:
  - alias: "Vacation mode code"
    description: "Add temporary code for house sitter"
    trigger:
      - platform: state
        entity_id: input_boolean.vacation_mode
        to: "on"
    action:
      - service: nimlykoder.add_code
        data:
          name: "House Sitter"
          pin_code: "{{ states('input_text.sitter_pin') }}"
          type: guest
          expiry: "{{ states('input_datetime.vacation_end') }}"
          
  - alias: "Remove vacation code"
    description: "Remove house sitter code when vacation ends"
    trigger:
      - platform: state
        entity_id: input_boolean.vacation_mode
        to: "off"
    action:
      - service: nimlykoder.list_codes
        response_variable: codes
      - repeat:
          for_each: "{{ codes.codes | selectattr('name', 'equalto', 'House Sitter') | list }}"
          sequence:
            - service: nimlykoder.remove_code
              data:
                slot: "{{ repeat.item.slot }}"
```

## Emergency Code Removal

Quickly remove all guest codes in an emergency:

```yaml
automation:
  - alias: "Emergency remove all guest codes"
    description: "Remove all guest codes immediately"
    trigger:
      - platform: state
        entity_id: input_boolean.emergency_lockdown
        to: "on"
    action:
      - service: nimlykoder.list_codes
        response_variable: codes
      - repeat:
          for_each: "{{ codes.codes | selectattr('type', 'equalto', 'guest') | list }}"
          sequence:
            - service: nimlykoder.remove_code
              data:
                slot: "{{ repeat.item.slot }}"
      - service: notify.mobile_app
        data:
          title: "Emergency Lockdown"
          message: "All guest codes have been removed"
```

## Smart Slot Assignment

Use a script to find and assign a slot intelligently:

```yaml
script:
  add_smart_guest_code:
    alias: "Add Smart Guest Code"
    description: "Add guest code with smart slot selection"
    fields:
      guest_name:
        description: "Name of the guest"
        example: "John Doe"
      pin_code:
        description: "4-digit PIN"
        example: "1234"
      days:
        description: "Number of days valid"
        example: 7
    sequence:
      - service: nimlykoder.add_code
        data:
          name: "{{ guest_name }}"
          pin_code: "{{ pin_code }}"
          type: guest
          expiry: "{{ (now() + timedelta(days=days)).strftime('%Y-%m-%d') }}"
        response_variable: result
      - service: persistent_notification.create
        data:
          title: "Guest Code Added"
          message: "Code for {{ guest_name }} added to slot {{ result.entry.slot }}"
```

## Lock/unlock Activity Notifications

### Companion App blueprint

[Import the Nimlykoder lock activity blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FFredrikElliot%2Fha-nimly-manager%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fnimlykoder%2Flock_activity.yaml).
Choose the configured lock entity, a Companion App device, lock/unlock/both,
whether to include automatic operations and operations without a matched name,
and English or Swedish. All notification text, method labels and unnamed-activity
fallbacks are translated. Disabling unnamed activity excludes all events with no name,
including manual, remote and automatic events; an unnamed automatic operation
requires both toggles to be enabled.

The source blueprint is
[`blueprints/automation/nimlykoder/lock_activity.yaml`](../blueprints/automation/nimlykoder/lock_activity.yaml).
The trigger is the event bus, and execution is queued: repeated operations by the
same person still notify. Do not trigger notifications from `last_unlocked_by` or
`last_locked_by` sensor transitions; those sensors are for displaying the latest
activity, and their state may not change when the same person operates again.

### Event contract and names

Listen for `nimlykoder_lock_activity` in Developer Tools → Events:

| Field | Value |
| --- | --- |
| `entity_id` | Configured `lock.*` entity; `null` for a legacy entry without one |
| `action` | `lock` or `unlock` |
| `name` | Matched friendly name, or `null` |
| `method` | `pin`, `rfid`, `fingerprint`, `manual`, `remote`, `automatic`, `unattributed` or `unknown` |
| `source` | Sanitized source enum, not arbitrary upstream text |
| `slot` | Integer credential slot, or `null`; slot 0 can be valid |
| `timestamp` | Report `last_seen`, normalized to a UTC ISO timestamp |

Configure a lock entity in Nimlykoder before using entity-filtered automations
or the blueprint; events with `entity_id: null` will not match a selected lock.
PIN names come from existing Nimlykoder PIN entries, not PIN digits. To name an
already-enrolled RFID tag or fingerprint:

```yaml
service: nimlykoder.set_credential_name
data:
  method: fingerprint  # rfid or fingerprint
  slot: 0             # 0..65535, including valid credential slot 0
  name: "Alex"        # "" removes the stored name
```

This service records names only. It does not enroll or remove tags/fingerprints
or change hardware credentials. Unmatched credentials keep `name: null`;
manual, remote and automatic operations must not be attributed to the last user.

Only current operation reports with `action: lock` or `action: unlock` and
`action_source_name` from a recent Zigbee2MQTT **onesti** converter are used;
`action_user` supplies the credential slot when available. `self` is automatic,
`zigbee` is remote, and ambiguous sources, including the model 05 ambiguity,
remain unattributed. Cached `last_*` fields are not evidence of a new operation.
If an older Zigbee2MQTT version exposes only those fields, upgrade it. Unknown
source values are sanitized to `unknown` rather than exposing upstream text.

**Mandatory replay protection:** in Zigbee2MQTT's `configuration.yaml`, set
`advanced.last_seen: ISO_8601` (`ISO_8601_local` with a UTC offset and `epoch` also work).
Without it, reports have no usable freshness timestamp: **no activity events or
activity sensor updates are produced**. The integration discards retained
messages, messages received during Home Assistant startup, missing/invalid
timestamps and reports older than the current MQTT subscription. Timestamp
freshness rejects stale cached reports after restart/reload, even when replayed
without the retained flag. The event timestamp comes from `last_seen`, not receipt
time.

Also set `advanced.cache_state_send_on_startup: false` and `retain: false` for
the lock device. `advanced.cache_state_persistent: false` is optional extra
hardening. See the [complete configuration example](../README.md#lockunlock-notifications)
and clear old retained device-state messages from the broker.
Deduplication uses report timestamp plus action, source and slot, **not** payload
or time-window debouncing: identical uses with different timestamps each emit.

### Plain Home Assistant automation (no app required)

This creates a persistent notification for both locking and unlocking. Replace
`lock.nimly_lock` with the entity configured in Nimlykoder. Omit a fixed
`notification_id` so successive operations create separate notifications.

```yaml
automation:
  - alias: "Nimlykoder lock activity"
    mode: queued
    max: 50
    trigger:
      - platform: event
        event_type: nimlykoder_lock_activity
        event_data:
          entity_id: lock.nimly_lock
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.get('action') in ['lock', 'unlock'] }}"
    action:
      - service: persistent_notification.create
        data:
          title: "Lock activity"
          message: >-
            {% set event = trigger.event.data %}
            {% set actor = event.get('name') or {
              'pin': 'Someone using an unnamed PIN',
              'rfid': 'Someone using an unnamed RFID tag',
              'fingerprint': 'Someone using an unnamed fingerprint',
              'manual': 'Manual operation',
              'remote': 'Remote control',
              'automatic': 'Automatic operation'
            }.get(event.get('method'), 'Unknown person') %}
            {% set method = {
              'pin': 'PIN',
              'rfid': 'RFID tag',
              'fingerprint': 'fingerprint',
              'manual': 'manual',
              'remote': 'remote',
              'automatic': 'automatic',
              'unattributed': 'unattributed',
              'unknown': 'unknown method'
            }.get(event.get('method'), 'unknown method') %}
            {{ actor }} {{ 'locked' if event.action == 'lock' else 'unlocked' }}
            {{ state_attr(event.entity_id, 'friendly_name') or 'the lock' }}
            ({{ method }}).
```

Event payloads and these notifications contain no PIN digits, RFID identifiers
or fingerprint data. They do include names and activity metadata: limit access
to Home Assistant and notification recipients accordingly. Native HomeKit can
notify about standard lock-state changes, but cannot provide named activity
notifications; use the blueprint or a Home Assistant automation instead.

## Helpers Required for Some Automations

```yaml
# Input helpers you may need (configuration.yaml)
input_boolean:
  add_family_code:
    name: Add Family Code
  extend_guest_code:
    name: Extend Guest Code
  vacation_mode:
    name: Vacation Mode
  emergency_lockdown:
    name: Emergency Lockdown

input_text:
  family_member_name:
    name: Family Member Name
  family_member_pin:
    name: Family Member PIN
  sitter_pin:
    name: House Sitter PIN

input_number:
  guest_code_slot:
    name: Guest Code Slot
    min: 0
    max: 99
    mode: box

input_datetime:
  vacation_end:
    name: Vacation End Date
    has_date: true
    has_time: false
```
