/**
 * Punto de entrada principal de la aplicación React.
 * Configura el renderizado en el DOM y habilita el modo estricto.
 */
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
