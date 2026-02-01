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

## Monitor Code Usage

Track when codes are used (requires additional sensors):

```yaml
automation:
  - alias: "Log code usage"
    description: "Log when a code is used to unlock"
    trigger:
      - platform: state
        entity_id: lock.nimly_lock
        to: "unlocked"
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.attributes.get('lock_user_id') is not none }}"
    action:
      - service: logbook.log
        data:
          name: "Door Access"
          message: "Door unlocked with code slot {{ trigger.to_state.attributes.lock_user_id }}"
```

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
