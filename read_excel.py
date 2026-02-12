import openpyxl
wb = openpyxl.load_workbook(r'C:\Users\edwin\Desktop\Department_Daily_Operational_Tracking.xlsx')
ws = wb.active
print("Departments and structure:")
for i, row in enumerate(ws.iter_rows(min_col=1, max_col=10, max_row=100), 1):
    values = [cell.value for cell in row]
    if any(values):
        print(f"Row {i}: {values}")
    if i > 30:  # Limit to first 30 rows with content
        break
