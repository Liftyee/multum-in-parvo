# Independent charge-temperature interlock

U401/U402 are TLV7031**S**DCKR comparators: SC70 pin 1 IN+, 2 GND, 3 IN−, 4 OUT, 5 VCC. The S suffix matters; the non-S device has a different pinout. This replaces TLV3691 because the specified offset improves from ±22 mV to ±8 mV. Its higher 335 nA typical supply current is drawn from solar.

TPS3839L30DBZR provides a solar-valid signal above approximately 2.63 V, after a nominal 200 ms delay. Its negative threshold spans 2.564–2.669 V. Comparator supplies are SOLAR_P; all three resistive dividers are supplied by SOLAR_VALID, so their load disappears when solar cannot support the chosen sensing operating range. This intentionally gives up harvesting at low source voltages in exchange for a defined temperature check. The design is for a panel with usable MPP above this threshold, not an arbitrary indoor harvester.

The external cell-mounted NTC is NCP18WF104F12RB: 100 kΩ ±1%, B25/50=4200 K ±1%. Murata lists this older part NRND; confirm availability or qualify a replacement using its full resistance/temperature curve. The sensor must be thermally attached and electrically insulated from the cell. A loose air-temperature sensor is insufficient.

The first-order beta relation is R(T)=100k exp[4200(1/T−1/298.15)], T in kelvin. R401=100 kΩ; reference ratios are 1M/(357k+1M)=0.7369197 and 1M/(1.98M+1M)=0.3355705. Nominal crossing temperatures are 4.685 °C and 40.195 °C. At a 4 V divider supply, the NTC branch draws 20 µA at 25 °C and the reference branches total 4.290 µA. These branches have no direct battery connection.

`reports/temperature.json` enumerates resistor ±0.1%, NTC R25 ±1%, beta ±1%, comparator offset ±8 mV, a conservative full 17 mV hysteresis allowance and 2 mV additional error allowance. At a conservative 2.164 V divider supply (minimum supervisor threshold minus its 0.4 V loaded-output allowance), conditional crossing bounds are 3.05–6.27 °C cold and 38.46–42.01 °C hot. Typical 7 mV hysteresis corresponds to about 0.17/0.18 °C at a 4 V divider supply.

These are conditional engineering calculations, not guaranteed safety limits: TI specifies the hysteresis extrema at 25 °C and gives no maximum input-bias current. The beta model also approximates the actual R/T curve. Chamber tests and the actual cell charging specification remain necessary.

Cold-good, hot-good and solar-valid drive three series NMOS devices. All three must conduct to pull down Q403's gate and pass VINT to charge enable. The pass stage defaults off; R410 pulls charge enable down. MCU CHG_INHIBIT independently pulls charge enable down through Q404 and cannot override the hardware inhibit. An open NTC drives its sense node high; a short drives it low, so either fault blocks charging.

Before release, verify the AEM10300 internal charge-enable pullup against the external 100 kΩ pulldown, include GPIO sampling delay, and test startup/shutdown below the supervisor's 0.6 V valid-reset floor. No claim of a completed battery-safety qualification is made by the ERC result.
