"""Inventory Module — Medicine stock management.

Responsibilities:
  - Medicine master data
  - Stock level tracking per hospital
  - Medicine consumption recording
  - Expiry date tracking and alerts
  - Purchase order management
  - Stock transfer between facilities
  - Supplier management
  - Reorder point configuration

Publishes Events:
  - inventory.medicine.stock_updated
  - inventory.medicine.stock_critical_low
  - inventory.medicine.expiry_approaching
  - inventory.medicine.stock_out
  - inventory.stock.received
  - inventory.stock.issued
  - inventory.purchase_order.created
"""
