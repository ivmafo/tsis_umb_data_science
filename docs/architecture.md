# 🏛️ Arquitectura del Sistema

## 🏗️ Patrones de Diseño Utilizados

### 1. Arquitectura Hexagonal (Ports and Adapters)
El núcleo de la aplicación (Dominio) es independiente de la infraestructura (Base de Datos, API Web, Frameworks).

*   **Dominio**: Entidades puras (`Sector`, `Flight`).
*   **Puertos**: Interfaces (`SectorRepository`, `FileRepository`).
*   **Adaptadores**: Implementaciones (`DuckDBRepository`, `FastAPIController`).

### 2. Dependency Injection (DI)
Usamos el patrón de contenedores para inyectar dependencias, facilitando el testing y el desacoplamiento.

### 3. Container-Presenter (Frontend)
Separación entre lógica de estado (`View`) y renderizado visual (`Component`).

---

## 📚 Referencias Bibliográficas

*   Cockburn, A. (2005). *Hexagonal architecture*. Alistair Cockburn. https://alistair.cockburn.us/hexagonal-architecture/
*   Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.
*   Fowler, M. (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley.
*   Ramírez, S. (2023). [Containers and Presenters in React](https://medium.com/@dan_abramov/smart-and-dumb-components-7ca2f9a7c7d0).
