# Stakeholders and Design Decisions

## Stakeholders

The primary stakeholders are people deploying and maintaining fixed mesh infrastructure, particularly for emergency and off-grid communication. Secondary stakeholders are the users relying on that infrastructure, community members testing the nodes, and future contributors reproducing or improving the open-source design.

Deployers need a node that is dependable, easy to install, remotely observable, and unlikely to require visits. Users need useful coverage and availability when ordinary communication infrastructure is absent. Testers and contributors need accessible hardware, documentation, measurements, and recovery interfaces.

## Design Decisions

### A. Purpose

The device will primarily be a fixed relay rather than a handheld node. Variants may later be produced from the same PCB.

### B. Deployment

The node will be mounted outdoors on a building or pole, or hung in a tree. It should reach an alpha-product level: autonomous most of the time, while remaining openable and serviceable when faults occur.

### C. Availability

Normal operation will use continuous radio reception. Scheduled reception may be introduced later as a degraded low-energy mode, but will not be assumed by the initial design.

### D. Energy

The node will use solar harvesting designed around UK winter conditions and partial summer shade. It should survive for 48 hours without harvested energy. A micropower harvesting IC and adaptive energy states will minimise panel and battery size without permanently limiting performance to the worst case.

### E. Processing and Radio

The STM32WL family is the preferred starting point because it integrates an efficient MCU and sub-GHz LoRa radio. The PCB and firmware need not be limited to Meshtastic; infrastructure-oriented or routed protocols may be more efficient than managed flooding.

### F. RF Performance

RF success will primarily be measured through link margin and comparative antenna performance rather than an absolute coverage distance. Position and terrain will be treated as deployment variables rather than properties of the radio alone.

### G. Antenna

The node will operate at EU868. Revision one should permit controlled comparison of external and PCB antenna designs, with matching performed in the final enclosure and mounting configuration.

### H. Positioning and Peripherals

GNSS is not required for a fixed node. An optional connector or unpopulated provision may be included if it does not materially increase power, area, or complexity.

### I. Configuration and Recovery

Custom firmware is acceptable. Normal configuration and diagnostics should work over authenticated LoRa management messages. A physical programming and recovery interface is required. BLE may be provided by an optional, normally unpowered coprocessor, but must not impose a continuous power cost.

### J. Construction and Maintainability

Build quality is part of performance. The enclosure, seals, connectors, solar mounting, condensation control, antenna mounting, and cable strain relief should be engineered for unattended outdoor use. The design will be open source and field-adjustable rather than permanently sealed.

### K. Project Outcome and Budget

The outcome should be a measured, documented prototype and project report rather than a production-ready commercial product. The engineering-society grant is £200, with personal funding available for justified overage.

