# Multum in Parvo — KiCad 8 engineering draft

**Revision A is still under development. Do not order or populate this draft.** The native project uses KiCad 8 schematic format 20231120 and PCB format 20240108. Validation runs with installed `kicad-cli 8.0.9`; no KiCad 9/10 format conversion is used. Open `mesh-node.kicad_pro`. All symbols and footprints are project-local.

The schematic has been captured and passes ERC. PCB routing and ground-return review are in progress. The current DRC report records the outstanding connections; a report with zero clearance violations alone does not mean the board is complete. Fabrication release requires zero unconnected items, a deliberate RF/power layout review, and completion of the checks below.

## Architecture

Solar feeds AEM10300; its storage pin joins PACK+. The battery supplies transmit pulses directly. BQ29700 and two common-drain AO3400A N-channel MOSFETs interrupt the negative cell lead. **CELL_N belongs only to the cell connector and protection circuit. Every load, charger return, programmer ground and shield connects to system GND / PACK−.** Raw BAT+ and protected PACK+ are electrically the same positive conductor in this low-side protection topology.

TPS63900 makes always-on 3.3 V. STM32WLE5CCU6 uses its low-power RF output, pin 22, with the ST MB1720 high-band low-power matching circuit. Pin 23, the high-power output, remains unconnected. A BGS12SN6 selects TX/RX for the normal population. The alternate path uses SKY66423-11 with its EK3 868 MHz matching/filter network and pack-referenced controls. MAX17048 is optional. TPS22919 supplies a peripheral connector carrying switched power and GND only.

The system needs an STM32WLE5 firmware/board port; this hardware is not a claim of existing drop-in Meshtastic firmware compatibility.

## Stack and RF geometry

Proposed stack: 2 layers, 0.8 mm finished board, 35 µm copper per side, approximately 0.73 mm dielectric, FR-4 Er 4.5, ENIG, 20 µm soldermask with assumed Er 3.8. RF corridors use top grounded coplanar waveguide, 0.75 mm trace and 0.25 mm side gap, with a continuous bottom reference. The 2-D quasi-static finite-volume calculation gives **50.65 Ω** at 10 µm grid resolution and 50.46 Ω at 20 µm. See `reports/field-impedance.json`; the earlier conformal approximation is retained separately for comparison.

These are proposed material properties, not guaranteed JLCPCB controlled impedance. Confirm the actual offered 0.8 mm stack and measure a coupon. The finite-box calculation does not include pad launches, component parasitics, connector transitions or RF matching. Short narrow launches at fine-pitch parts require VNA tuning. Two layers are quantitatively feasible; a switch to four layers is not justified by the line width.

Ordinary clearance is 0.15 mm, with 0.20 mm ordinary signal routing preferred where space allows. Vias use 0.60/0.30 mm copper/drill. Power routing uses wider conductors and will be reviewed for bottlenecks before release. RF signal routing is restricted to the top layer. Routing output alone is not sufficient: copper pours, stitching and visual ground continuity must also pass review.

## Configuration and operating assumptions

- Solar panel **worst-case cold Voc ≤4.3 V**, providing margin below AEM10300's 4.5 V recommended SRC limit. Its 5.5 V absolute maximum is not an operating target. A nominal 6 V panel is unsuitable.
- AEM10300 straps: STO_CFG=0000 gives 4.05 V charge, 3.50 V ready and 3.00 V low status; R_MPP=100 selects 80% Voc; T_MPP=01 selects nominal 4.5 s/70.8 ms sampling. EN_HP is high; charge is independently inhibited by the temperature/solar-valid logic and MCU.
- Four 100 µF/10 V/1210 storage capacitors are provided. The manufacturer requires at least 100 µF **effective** capacitance with an absent battery. DC-bias/temperature derating of the exact selected capacitor remains a release check.
- TPS63900: CFG3=16.2 kΩ for 3.3 V at SEL=0; CFG1=36.5 kΩ and CFG2=0 also select 3.3 V/unlimited current in the alternate state. Configuration resistors are 1%.
- BQ29700 nominal overcharge/undervoltage levels are 4.275/2.800 V. Normal firmware operating floor is 3.0 V with burst-droop margin. Protection is independent of firmware.
- AO3400A replaces CSD16301Q2 because it specifies ≤48 mΩ at 2.5 V gate drive. Two devices give ≤96 mΩ at 25 °C: 28.8 mV drop and 8.64 mW at 300 mA, excluding traces/connectors. Temperature and protection-threshold tolerances still need inclusion in the final current-path review.
- AQ3118E-01ETG replaces the suggested ESD part: 18 V bidirectional standoff and 0.3 pF typical capacitance accommodate the 7.08 V RF peak at +27 dBm into 50 Ω. A 5 V standoff diode is inappropriate at that power. ESD system performance must be tested.

## RF firmware requirements

BGS12SN6 draws 100 µA typical/180 µA maximum while powered. PA11 supplies its VDD, following the GPIO-supply option in the ST reference. Before sleep set CTRL=0, then PA11=0; keep CTRL low while the switch is unpowered. On wake drive PA11 high and wait at least 20 µs before transmitting. CTRL=0 selects RF1/TX; CTRL=1 selects RF2/RX.

FEM controls have pack-referenced high levels and default low. Allow at least 1 ms for the high-value level-translation networks to settle. Configure the radio's LP PA, start at −9 dBm conducted drive, verify output with an attenuator/load and spectrum analyzer, and never exceed the FEM's +10 dBm TX-input absolute maximum. Firmware must enforce regional output-power, antenna-gain and duty-cycle restrictions. +27 dBm is not universally permitted in EU868.

## Estimated standby budget

No board current has been measured. Typical component figures are not worst-case system guarantees.

| Contributor | Approximate standby contribution | Conditions |
|---|---:|---|
| BQ29700 | 4 µA | Omitted with externally protected pack |
| TPS63900 | 0.075 µA | Typical quiescent figure, conversion losses additional |
| STM32WLE5 | ~1 µA class | Stop 2 + RTC; configuration dependent |
| TPS22919 | 0.002 µA typical | OFF; datasheet permits up to 0.8 µA over full temperature |
| MAX17048 | ~3 µA | Hibernate, optional/DNP; active mode higher |
| BGS12SN6 | Supply driven low in sleep | GPIO/switch leakage must be measured |
| Temperature divider | No direct battery divider load | Powered from solar-valid output only |
| Temperature comparators/supervisor | Solar supplied | ~0.82 µA nominal combined IC current |
| AEM10300 | Unresolved in selected high-power mode | 5.9 nA figure applies to EN_HP=LOW, not the selected HIGH strap |
| FEM and translation | Optional/DNP | Shutdown leakage needs full-temperature audit |

Known default contributions are about 5.1 µA before AEM high-power-mode current, GPIO/MOSFET leakage, capacitor leakage and converter losses. The single-digit ancillary target is plausible but **not yet verified**. A continuously high BGS supply would alone defeat it; the circuit now explicitly avoids that.

## Bring-up sequence after layout release

1. Inspect all bridges, orientation marks, exposed pads and mutually exclusive population options. Leave antenna disconnected and all supplies off.
2. Check resistance between PACK+, GND and CELL_N. Verify protection MOSFET body-diode orientation. Use a current-limited battery simulator before attaching a cell.
3. Verify BQ cutoff/recovery and confirm that solar, debug and peripheral grounds cannot bypass the protector.
4. Sweep the temperature sensor resistance and solar voltage. Confirm EN_STO_CH goes low for absent/shorted NTC, out-of-window temperature, reset MCU and insufficient solar voltage. Measure response delay and leakage.
5. Check 3V3_AON, regulator startup, ripple and droop with pulsed loads. Verify all RF supply nodes before enabling the radio.
6. Attach SWD, test both oscillators, calibrate HSE loading/trim, verify RTC and deep-sleep current with debug detached.
7. Test normal RF with a suitable conducted load/attenuation. Tune matching and filter values with a VNA; measure harmonics, RX sensitivity and switching transients.
8. Fit the FEM variant only after the normal radio works. Verify control truth table/default shutdown and output power starting at minimum drive. Repeat spectral, RX and current-pulse checks.
9. Repeat temperature, battery cutoff/recovery, absent-battery and low-light tests across the intended operating range. Attach the real battery last.

## Release checks still open

Finish routing and ground pours/stitching; inspect both layers; resolve DRC including connectivity and schematic parity; verify every custom footprint against the manufacturer's drawing; verify exact capacitor derating and inductor land patterns; close charge-enable pullup/logic margins and temperature qualification; audit crystal startup/load/frequency tolerance; audit all sleep leakage at temperature; finish silk/test-point labels and connector orientation review. Only then export a fabrication set, assembly positions and final BOM.

See `population-options.md`, `temperature-analysis.md`, `sources/urls.json` and `reports/` for supporting material. Draft BOM entries that contain only an electrical value still require a purchasable manufacturer part number before fabrication release.
