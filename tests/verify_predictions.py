from src.application.use_cases.validate_models import ValidateModels
import json

def run_verification():
    print("Iniciando validación de modelos predictivos...")
    validator = ValidateModels()
    try:
        result = validator.execute()
        print("\n--- REPORTE DE VALIDACIÓN ---")
        print(f"Estado General: {result['overall_status']}")
        print(f"Fecha: {result['timestamp']}")
        print("\nDetalles:")
        for item in result['validation_report']:
            status_icon = "[OK]" if item['status'] == "Good" else ("[WARN]" if item['status'] == "Warning" else "[FAIL]")
            metric_text = f": {item.get('metric', 'Status')}"
            print(f"{status_icon} {item['model']}{metric_text} = {item.get('value', 'N/A')} ({item['status']})")
            print(f"   Detalles: {item.get('details', '')}")
            if 'threshold' in item:
                print(f"   Umbral: {item['threshold']}")
            print("-" * 30)
            
        if result['overall_status'] == "Healthy" or result['overall_status'] == "Warnings Detected":
            print("\nRESULTADO: ÉXITO - Los modelos funcionan dentro de parámetros aceptables.")
        else:
            print("\nRESULTADO: FALLO - Se detectaron problemas críticos.")
            
    except Exception as e:
        print(f"\nERROR CRÍTICO: {str(e)}")

if __name__ == "__main__":
    run_verification()
