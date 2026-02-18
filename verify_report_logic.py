from src.application.use_cases.generate_origin_report import GenerateOriginReport
from src.application.use_cases.generate_destination_report import GenerateDestinationReport
from src.application.use_cases.generate_region_report import GenerateRegionReport
from src.application.use_cases.generate_flight_type_report import GenerateFlightTypeReport
from src.application.use_cases.generate_company_report import GenerateCompanyReport
from src.application.use_cases.generate_time_report import GenerateTimeReport
from src.application.use_cases.generate_heatmap_report import GenerateHeatmapReport
from src.application.use_cases.generate_raw_data_report import GenerateRawDataReport
import pandas as pd
import datetime

def test_report(ReportClass, name, **kwargs):
    print(f"\n--- Testing {name} ---")
    try:
        report = ReportClass()
        filters = {} 
        
        print(f"  > Excel ({kwargs})...")
        report.generate_excel(filters, **kwargs)
        print("    SUCCESS")

        print(f"  > PDF ({kwargs})...")
        report.generate_pdf(filters, **kwargs)
        print("    SUCCESS")
    except Exception as e:
        print(f"FAILED {name}: {e}")
        # raise e # Don't raise, continue testing others

if __name__ == "__main__":
    try:
        # 1. Origin & Destination
        # test_report(GenerateOriginReport, "Origin Report")
        # test_report(GenerateDestinationReport, "Destination Report")
        
        # 2. Region
        test_report(GenerateRegionReport, "Region Report (Origin)", dimension='origin')
        test_report(GenerateRegionReport, "Region Report (Destination)", dimension='destination')
        
        # 3. Flight Type
        # test_report(GenerateFlightTypeReport, "Flight Type Report")
        
        # 4. Company
        # test_report(GenerateCompanyReport, "Company Report")
        
        # 5. Time
        # test_report(GenerateTimeReport, "Time Report (Month)", group_by='month')
        # test_report(GenerateTimeReport, "Time Report (Year)", group_by='year')
        
        # 6. Heatmap
        # test_report(GenerateHeatmapReport, "Heatmap (Departure)", timeColumn='hora_salida')
        # test_report(GenerateHeatmapReport, "Heatmap (Arrival)", timeColumn='hora_llegada')

        # 7. Raw Data
        print("\n--- Testing Raw Data Export ---")
        try:
             uc = GenerateRawDataReport()
             uc.generate_excel({"start_date": "2023-01-01"})
             print("    SUCCESS")
        except Exception as e:
             print(f"    FAILED: {e}")
        
    except ImportError as e:
        print(f"Import Error: {e}")
    except Exception as e:
        print(f"General Error: {e}")
