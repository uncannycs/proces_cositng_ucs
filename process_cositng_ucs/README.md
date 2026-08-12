# Manufacturing Process Costing UCS

## Overview
This module enables manufacturers to calculate, track, and manage process costing effectively. It provides complete visibility into material, labor, and overhead costs, comparing estimated against actual costs on Manufacturing Orders.

## Features
- Manually enter or automatically compute Material, Labor, and Overhead costs.
- Work center-based process costing logic.
- Total cost and cost-per-unit breakdowns on BOMs and MOs.
- Detailed reporting with actual vs estimated cost analysis.
- Multi-company and multi-currency support.

## Installation
1. Download the module.
2. Place it in your Odoo `custom/apps` directory.
3. Restart the Odoo server.
4. Update the App list and install `Manufacturing Process Costing UCS`.

## Configuration
Go to **Manufacturing > Configuration > Settings**. Under the **Process Costing** section, select:
- **Manual**: Enter costing manually on BOMs and MOs.
- **Work-Center**: Automatically compute costs based on Work Center labor and overhead hour rates.

## Usage
1. Configure cost rates on Work Centers.
2. Create a BOM. Use the **Compute Costs** button to pull in operations and materials costs.
3. Create a Manufacturing Order from the BOM. Estimated costs are tracked automatically.
4. Complete the MO. Actual costs are computed based on consumed materials and work order duration.

## Author
**Uncanny Consulting Services LLP**
