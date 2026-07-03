"""Reports Module — Automated report generation.

Responsibilities:
  - Daily hospital operational reports
  - Weekly district summary reports
  - Monthly government submission reports
  - Medicine inventory reports
  - Patient statistics reports
  - Doctor attendance reports
  - Emergency incident reports
  - AI recommendation reports

Export Formats:
  - PDF (reportlab)
  - Excel (openpyxl)
  - CSV

This module is READ-ONLY from a business data perspective.
It generates documents from existing data and stores them in Supabase Storage.
"""
