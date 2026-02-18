from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from src.application.use_cases.generate_origin_report import GenerateOriginReport
from src.application.use_cases.generate_destination_report import GenerateDestinationReport
from src.application.use_cases.generate_region_report import GenerateRegionReport
from src.application.use_cases.generate_flight_type_report import GenerateFlightTypeReport
from src.application.use_cases.generate_company_report import GenerateCompanyReport
from src.application.use_cases.generate_time_report import GenerateTimeReport
from src.application.use_cases.generate_heatmap_report import GenerateHeatmapReport
from src.application.use_cases.export_raw_flights_use_case import ExportRawFlightsUseCase
from src.application.use_cases.generate_executive_report import GenerateExecutiveReport
from src.application.di.container import get_export_raw_flights_use_case, get_generate_executive_report_use_case
import io

router = APIRouter(prefix="/reports", tags=["reports"])

def get_report_use_case():
    return GenerateOriginReport()

def get_destination_report_use_case():
    return GenerateDestinationReport()

def get_region_use_case(): return GenerateRegionReport()
def get_flight_type_use_case(): return GenerateFlightTypeReport()
def get_company_use_case(): return GenerateCompanyReport()
def get_time_use_case(): return GenerateTimeReport()
def get_heatmap_use_case(): return GenerateHeatmapReport()

@router.post("/origin/excel")
def generate_origin_excel(
    filters: Dict[str, Any] = Body(...),
    use_case: GenerateOriginReport = Depends(get_report_use_case)
):
    """
    Generate Excel report for Flights by Origin.
    """
    try:
        excel_file = use_case.generate_excel(filters)
        return StreamingResponse(
            excel_file, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=reporte_origen.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/origin/pdf")
def generate_origin_pdf(
    filters: Dict[str, Any] = Body(...),
    use_case: GenerateOriginReport = Depends(get_report_use_case)
):
    """
    Generate PDF report for Flights by Origin.
    """
    try:
        pdf_file = use_case.generate_pdf(filters)
        return StreamingResponse(
            pdf_file, 
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=reporte_origen.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/destination/excel")
def generate_destination_excel(
    filters: Dict[str, Any] = Body(...),
    use_case: GenerateDestinationReport = Depends(get_destination_report_use_case)
):
    """
    Generate Excel report for Flights by Destination.
    """
    try:
        excel_file = use_case.generate_excel(filters)
        return StreamingResponse(
            excel_file, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=reporte_destino.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/destination/pdf")
def generate_destination_pdf(
    filters: Dict[str, Any] = Body(...),
    use_case: GenerateDestinationReport = Depends(get_destination_report_use_case)
):
    """
    Generate PDF report for Flights by Destination.
    """
    try:
        pdf_file = use_case.generate_pdf(filters)
        return StreamingResponse(
            pdf_file, 
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=reporte_destino.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Region Reports ---
@router.post("/region/excel")
def generate_region_excel(
    payload: Dict[str, Any] = Body(...),
    use_case: GenerateRegionReport = Depends(get_region_use_case)
):
    try:
        dimension = payload.get('dimension', 'origin')
        file = use_case.generate_excel(payload, dimension)
        return StreamingResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=reporte_region_{dimension}.xlsx"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/region/pdf")
def generate_region_pdf(
    payload: Dict[str, Any] = Body(...),
    use_case: GenerateRegionReport = Depends(get_region_use_case)
):
    try:
        dimension = payload.get('dimension', 'origin')
        file = use_case.generate_pdf(payload, dimension)
        return StreamingResponse(file, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=reporte_region_{dimension}.pdf"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- Flight Type Reports ---
@router.post("/flight-type/excel")
def generate_flight_type_excel(filters: Dict[str, Any] = Body(...), use_case: GenerateFlightTypeReport = Depends(get_flight_type_use_case)):
    try:
        file = use_case.generate_excel(filters)
        return StreamingResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=reporte_tipo_vuelo.xlsx"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/flight-type/pdf")
def generate_flight_type_pdf(filters: Dict[str, Any] = Body(...), use_case: GenerateFlightTypeReport = Depends(get_flight_type_use_case)):
    try:
        file = use_case.generate_pdf(filters)
        return StreamingResponse(file, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=reporte_tipo_vuelo.pdf"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- Company Reports ---
@router.post("/company/excel")
def generate_company_excel(filters: Dict[str, Any] = Body(...), use_case: GenerateCompanyReport = Depends(get_company_use_case)):
    try:
        file = use_case.generate_excel(filters)
        return StreamingResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=reporte_empresa.xlsx"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/company/pdf")
def generate_company_pdf(filters: Dict[str, Any] = Body(...), use_case: GenerateCompanyReport = Depends(get_company_use_case)):
    try:
        file = use_case.generate_pdf(filters)
        return StreamingResponse(file, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=reporte_empresa.pdf"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- Time Reports ---
@router.post("/time/excel")
def generate_time_excel(payload: Dict[str, Any] = Body(...), use_case: GenerateTimeReport = Depends(get_time_use_case)):
    try:
        groupBy = payload.get('groupBy', 'month')
        file = use_case.generate_excel(payload, groupBy)
        return StreamingResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=reporte_tiempo_{groupBy}.xlsx"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/time/pdf")
def generate_time_pdf(payload: Dict[str, Any] = Body(...), use_case: GenerateTimeReport = Depends(get_time_use_case)):
    try:
        groupBy = payload.get('groupBy', 'month')
        file = use_case.generate_pdf(payload, groupBy)
        return StreamingResponse(file, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=reporte_tiempo_{groupBy}.pdf"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

# --- Heatmap Reports ---
@router.post("/heatmap/excel")
def generate_heatmap_excel(payload: Dict[str, Any] = Body(...), use_case: GenerateHeatmapReport = Depends(get_heatmap_use_case)):
    try:
        timeColumn = payload.get('timeColumn', 'hora_salida')
        file = use_case.generate_excel(payload, timeColumn)
        return StreamingResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=reporte_heatmap.xlsx"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/heatmap/pdf")
def generate_heatmap_pdf(payload: Dict[str, Any] = Body(...), use_case: GenerateHeatmapReport = Depends(get_heatmap_use_case)):
    try:
        timeColumn = payload.get('timeColumn', 'hora_salida')
        file = use_case.generate_pdf(payload, timeColumn)
        return StreamingResponse(file, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=reporte_heatmap.pdf"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


# --- Raw Data Export ---
@router.post("/raw/csv")
def export_raw_data_csv(
    filters: Dict[str, Any] = Body(...),
    use_case: ExportRawFlightsUseCase = Depends(get_export_raw_flights_use_case)
):
    try:
        csv_file = use_case.execute(filters)
        return StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data_cruda_vuelos.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Executive Reports ---
@router.post("/executive/pdf")
def generate_executive_pdf(
    filters: Dict[str, Any] = Body(...),
    use_case: GenerateExecutiveReport = Depends(get_generate_executive_report_use_case)
):
    try:
        file = use_case.generate_pdf(filters)
        return StreamingResponse(file, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=reporte_ejecutivo.pdf"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/executive/excel")
def generate_executive_excel(
    filters: Dict[str, Any] = Body(...),
    use_case: GenerateExecutiveReport = Depends(get_generate_executive_report_use_case)
):
    try:
        file = use_case.generate_excel(filters)
        return StreamingResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=reporte_ejecutivo.xlsx"})
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
