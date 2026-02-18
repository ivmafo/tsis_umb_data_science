import { useState } from 'react';
import { MainLayout } from './components/layout/MainLayout';
import { FilesView } from './views/FilesView';
import { UploadView } from './views/UploadView';
import { RegionsView } from './views/RegionsView';
import { AirportsView } from './views/AirportsView';
import { RegionAirportsView } from './views/RegionAirportsView';
import { FlightDistributionView } from './views/FlightDistributionView';
import { HistoryView } from './views/HistoryView';
import SectorConfigurationView from './views/SectorConfigurationView';
import CapacityReportView from './views/CapacityReportView';
import PredictiveView from './views/PredictiveView';
import { LayoutDashboard } from 'lucide-react';

/**
 * Componente Principal de la Aplicación (App).
 * Gestiona el enrutamiento interno de vistas, el estado de navegación global 
 * y la persistencia de datos mediante el refresco de componentes.
 */
function App() {
  // ESTADO: Almacena la vista activa (slug) para el renderizado condicional
  const [currentView, setCurrentView] = useState('dashboard');
  // ESTADO: Clave para forzar el refresco de vistas que dependen de datos frescos
  const [refreshKey, setRefreshKey] = useState(0);

  /**
   * Cambia la vista actual según la selección del usuario en la Sidebar.
   */
  const handleNavigate = (view: string) => {
    setCurrentView(view);
  };

  /**
   * Se dispara tras una carga exitosa de archivos para notificar a los componentes de lista.
   */
  const handleUploadSuccess = () => {
    setRefreshKey(prev => prev + 1);
  };

  /**
   * Función de enrutamiento: Retorna el componente asociado a la vista seleccionada.
   */
  const renderContent = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <div className="flex flex-col items-center justify-center h-96 text-center space-y-4">
            <div className="p-4 bg-blue-100 text-primary rounded-full">
              <LayoutDashboard size={48} />
            </div>
            <h2 className="text-2xl font-bold text-slate-700">Bienvenido al Tablero</h2>
            <p className="text-slate-500 max-w-md">Selecciona una opción en el menú lateral para comenzar a gestionar tus archivos y regiones.</p>
          </div>
        );
      case 'files':
        return <FilesView key={refreshKey} />;
      case 'regions':
        return <RegionsView />;
      case 'airports':
        return <AirportsView />;
      case 'region-airports':
        return <RegionAirportsView />;
      case 'flight-distribution':
        return <FlightDistributionView />;
      case 'upload':
        return <UploadView onSuccess={handleUploadSuccess} />;
      case 'history':
        return <HistoryView />;
      case 'sector-config':
        return <SectorConfigurationView />;
      case 'capacity-report':
        return <CapacityReportView />;
      case 'predictive':
        return <PredictiveView />;
      default:
        return (
          <div className="p-10 text-center text-slate-500">
            Vista en construcción: {currentView}
          </div>
        );
    }
  };

  return (
    <MainLayout currentView={currentView} onNavigate={handleNavigate}>
      {renderContent()}
    </MainLayout>
  );
}

export default App;
