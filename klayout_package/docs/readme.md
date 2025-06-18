# KMeasurement Documentation
## 1. Overview
KMeasurement is a KLayout package designed to bridge the gap between chip layout and electrical characterization. It allows users to control and automate measurement instruments directly from the KLayout interface, streamlining the process of testing and validating integrated circuits.

The core philosophy is to integrate test-rule definitions and instrument control into the design environment, enabling a "measurement-aware" layout workflow.

## 2. Core Features
- Instrument Control: Directly manage and operate common lab equipment (SMUs, motor controllers, etc.) using the powerful qcodes framework.

- PCell-based Instruments: Instruments are defined as parametric cells (PCells) in your layout. Instantiating an instrument PCell makes its controls available in the KMeasurement tab.

- Technology-Integrated Test Rules: Define and standardize complete measurement procedures directly within your KLayout technology files (.lyt or an associated YAML/JSON file). This allows you to specify not just voltage/current ranges, but entire test recipes like 'MOSFET Id-Vg sweep' or 'Resistor Linearity Test', complete with sweep parameters, compliance limits, and timing delays. By linking test protocols to the PDK, you ensure consistency and repeatability. A comprehensive default set of rules is provided for technologies without specific definitions, ensuring the tool is always ready for ad-hoc measurements out of the box.

- Dynamic UI: A dedicated "Measurement" tab appears in KLayout, dynamically populating with controls corresponding to the instrument PCells present in your active layout.

Extensible Architecture: The package is designed to be easily extendable. Adding support for new instruments is as simple as creating a new PCell and a corresponding qcodes driver.

# 3. Installation
KMeasurement is distributed as a KLayout Salt package (.kip).

- Open KLayout.

- Navigate to Tools > Manage Packages.

- Click Install New Package and select the KMeasurement-vx.x.x.kip file.

- KLayout will automatically install the package. Upon first load, it will check for and attempt to install required Python dependencies (qcodes, pyvisa, etc.). This may take a moment.

- After installation, restart KLayout.

- A new "Measurement" menu will appear in the main menu bar, confirming the successful installation.