# Requirements

These are initial requirements and should be refined with numerical test conditions during the design process.

## A. Purpose

- **A1.** The primary device shall operate as a fixed packet relay.
- **A2.** The hardware should support later variants without requiring a complete redesign.

## B. Deployment

- **B1.** The node shall support installation on a building, pole, or tree.
- **B2.** The prototype shall operate autonomously under normal conditions.
- **B3.** The node shall remain openable and repairable using ordinary tools.

## C. Availability

- **C1.** The node shall continuously receive during its normal energy state.
- **C2.** Reduced-duty or scheduled reception may only be used as an explicit degraded energy state.
- **C3.** Changes of availability state shall be recorded and exposed through diagnostics.

## D. Energy

- **D1.** The node shall use photovoltaic energy harvesting with maximum-power-point control or an equivalent appropriate control method.
- **D2.** The energy design shall use stated UK winter and partial-shade assumptions.
- **D3.** The node shall provide at least 48 hours of normal operation without harvested energy at beginning of life.
- **D4.** The harvesting system shall accept surplus available power rather than being limited to its minimum operating input.
- **D5.** The node shall adapt its service level to stored-energy thresholds with hysteresis.
- **D6.** Panel and storage capacity shall be justified using measured complete-system energy consumption.

## E. Processing and Radio

- **E1.** The first architecture shall evaluate an STM32WL MCU and integrated sub-GHz radio.
- **E2.** The radio shall support the EU868 band and applicable regional operating limits.
- **E3.** The protocol shall support multi-hop fixed relays without requiring Internet infrastructure.
- **E4.** Protocol selection shall compare airtime, forwarding overhead, route recovery, interoperability, and implementation effort against Meshtastic.
- **E5.** The firmware shall permit custom power and management behaviour.

## F. RF Performance

- **F1.** RF performance shall be compared against at least one defined reference node and antenna.
- **F2.** Testing shall report conducted or estimated link budget, received signal level, packet success rate, and operating radio settings.
- **F3.** Coverage claims shall state antenna height, terrain, separation, orientation, and test conditions.
- **F4.** Antenna mismatch and radiated performance shall be reported separately.

## G. Antenna

- **G1.** The RF path shall include an accessible 50-ohm test point or connector and a configurable matching network.
- **G2.** Revision one shall support a replaceable external EU868 antenna.
- **G3.** PCB antenna candidates should be evaluated using separate test coupons or interchangeable antenna boards before integration.
- **G4.** Antennas shall be tuned and tested with the intended enclosure, battery, panel wiring, mounting arrangement, and nearby structure represented.
- **G5.** Testing shall include at least one orientation or pattern comparison, not only VNA return-loss measurements.

## H. Positioning and Peripherals

- **H1.** GNSS shall not be populated by default.
- **H2.** Any optional peripheral provision shall have a true power-off state and shall not compromise the normal-state energy target.

## I. Configuration and Recovery

- **I1.** The node shall support authenticated configuration and diagnostic messages over the primary radio link.
- **I2.** The PCB shall expose SWD and a bootloader-capable wired interface.
- **I3.** The node shall recover automatically from ordinary firmware hangs using an independent watchdog.
- **I4.** Repeated resets and reset causes shall be retained for diagnosis.
- **I5.** Any BLE or Wi-Fi service processor shall be electrically switchable and normally unpowered.
- **I6.** A failed optional service processor shall not prevent the primary relay from operating.

## J. Construction and Maintainability

- **J1.** The enclosure design shall target IP67-level protection, subject to prototype verification.
- **J2.** External penetrations shall use suitable seals, strain relief, and corrosion-resistant hardware.
- **J3.** The design shall include a condensation and pressure-equalisation strategy.
- **J4.** The node shall expose battery, harvesting, reset, and radio-health information for remote maintenance.
- **J5.** Hardware design files, firmware, assembly information, and test results shall be published under stated open-source licences.

## K. Project Outcome and Budget

- **K1.** The project shall produce at least one field-testable integrated prototype.
- **K2.** The report shall document design decisions, unsuccessful approaches, measurements, and community feedback.
- **K3.** Spending from the engineering-society grant shall not exceed £200; any personal overage shall be recorded separately.

