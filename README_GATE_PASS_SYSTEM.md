# Gate Pass System for ERPNext

## Overview

The Gate Pass system is designed to track all item movements through the gate, whether incoming or outgoing. It integrates seamlessly with ERPNext's purchase and sales workflows to automatically create gate passes when items enter or leave the premises.

## Features

### 1. Gate Inward Management
- **Automatic Creation**: Gate Inward documents are automatically created when Purchase Orders are submitted
- **Stock Entry Integration**: Gate Inward entries are created for inward stock movements
- **Item Tracking**: Tracks received vs pending quantities for each item
- **Vehicle Details**: Records vehicle and driver information for incoming shipments

### 2. Gate Outward Management
- **Automatic Creation**: Gate Outward documents are automatically created when Delivery Notes are submitted
- **Stock Entry Integration**: Gate Outward entries are created for outward stock movements
- **Item Tracking**: Tracks delivered vs pending quantities for each item
- **Vehicle Details**: Records vehicle and driver information for outgoing shipments

### 3. Integration with ERPNext Documents

#### Purchase Workflow
1. **Purchase Order** → Automatically creates **Gate Inward**
2. **Gate Inward** → Items can be fetched into **Purchase Receipt**
3. **Purchase Receipt** → Updates received quantities in **Gate Inward**

#### Sales Workflow
1. **Sales Order** → Creates **Delivery Note**
2. **Delivery Note** → Automatically creates **Gate Outward**
3. **Gate Outward** → Items can be fetched into **Delivery Note**

#### Stock Movement
- **Stock Entry** → Automatically creates **Gate Inward** (for inward movements) or **Gate Outward** (for outward movements)

## Document Types

### 1. Gate Inward
- **Purpose**: Track incoming items from suppliers or other sources
- **Source Documents**: Purchase Order, Stock Entry, Purchase Receipt
- **Key Fields**:
  - Gate Inward Type (Purchase Order, Stock Entry, Other)
  - Source Document Type and Reference
  - Supplier Information
  - Vehicle Details
  - Items with quantities and pending status

### 2. Gate Outward
- **Purpose**: Track outgoing items to customers or other destinations
- **Source Documents**: Delivery Note, Stock Entry, Sales Invoice
- **Key Fields**:
  - Gate Outward Type (Delivery Note, Stock Entry, Other)
  - Source Document Type and Reference
  - Customer Information
  - Vehicle Details
  - Items with quantities and pending status

### 3. Child Tables
- **Gate Inward Item**: Individual items in a Gate Inward
- **Gate Outward Item**: Individual items in a Gate Outward

## Workflow Integration

### Automatic Gate Pass Creation

The system automatically creates gate passes when the following documents are submitted:

1. **Purchase Order** → Creates Gate Inward
2. **Delivery Note** → Creates Gate Outward
3. **Stock Entry** → Creates Gate Inward (inward) or Gate Outward (outward)

### Manual Item Fetching

Users can manually fetch items from gate passes into other documents:

1. **Purchase Receipt** → "Fetch from Gate Inward" button
2. **Delivery Note** → "Fetch from Gate Outward" button

### Quantity Tracking

The system automatically tracks:
- **Received Qty**: Items received through Purchase Receipt
- **Delivered Qty**: Items delivered through Delivery Note
- **Pending Qty**: Remaining items to be received/delivered

## Installation and Setup

### 1. Install the App
```bash
bench get-app gate_pass
bench install-app gate_pass
```

### 2. Migrate the Database
```bash
bench migrate
```

### 3. Build Assets
```bash
bench build
```

## Usage

### Creating Gate Inward from Purchase Order

1. Create and submit a Purchase Order
2. System automatically creates a Gate Inward
3. Gate Inward shows all items with pending quantities
4. Create Purchase Receipt and use "Fetch from Gate Inward" button
5. Purchase Receipt updates received quantities in Gate Inward

### Creating Gate Outward from Delivery Note

1. Create and submit a Delivery Note
2. System automatically creates a Gate Outward
3. Gate Outward shows all items with pending quantities
4. Use "Fetch from Gate Outward" button to populate Delivery Note items

### Stock Entry Integration

1. Create a Stock Entry for inward/outward movement
2. System automatically creates appropriate Gate Inward/Outward
3. Track all stock movements through the gate

## Customization

### Adding Custom Fields

You can add custom fields to Gate Inward and Gate Outward documents through the Customize Form feature.

### Modifying Workflows

The integration logic is in `gate_pass_events.py`. You can modify the functions to customize the workflow according to your business needs.

## Reports and Dashboards

The system includes:
- Gate Pass Dashboard with status charts
- Gate Inward and Outward status reports
- Integration with ERPNext's reporting system

## Permissions

The system uses standard ERPNext permissions:
- System Manager: Full access to all gate pass documents
- Stock User: Can create and submit gate passes
- Stock Manager: Can approve and manage gate passes

## Troubleshooting

### Common Issues

1. **Gate Pass not created automatically**
   - Check if the source document is submitted
   - Verify the integration hooks are properly configured
   - Check error logs for any exceptions

2. **Items not fetching correctly**
   - Ensure the gate pass is in "Submitted" status
   - Check if items have pending quantities
   - Verify the source document relationship

3. **Quantities not updating**
   - Check if the related documents are properly linked
   - Verify the update functions in gate_pass_events.py

### Error Logs

Check the error logs in:
- `logs/frappe.log` for general errors
- `logs/bench.log` for bench-related errors

## Support

For support and customization requests, please contact the development team.

## License

This app is licensed under the MIT License. 