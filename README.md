# Task Time Manager ⏱️

Una aplicación web ágil y adaptada para dispositivos móviles, diseñada para registrar, categorizar y analizar el tiempo dedicado a múltiples proyectos, tareas de gestión e investigación. Construida con Python y Streamlit, y conectada a Google Sheets para un almacenamiento seguro y persistente en la nube.

## 🚀 Características Principales

*   **Interfaz Rápida y Móvil:** Diseñada para registrar tareas en pocos segundos desde el celular o la computadora.
*   **Categorización Multidimensional:** 
    *   *Ámbito* (Clínico, Académico, Ingeniería, Gestión).
    *   *Sector/Proyecto* (Kine CR, Proyecto AMBLE, Laboratorio de Marcha, etc.).
    *   *Tipo de Tarea* (Desarrollo, Reunión, Atención a paciente, etc.).
*   **Seguimiento de Imprevistos:** Opción de un solo toque para marcar urgencias e interrupciones no planificadas.
*   **Notas por Dictado de Voz:** Campo de texto libre optimizado para usar el micrófono del teclado del celular.
*   **Tablero de Análisis Dinámico:** Visualización en tiempo real de horas totales, distribución de tiempo por área, porcentaje de horas consumidas en imprevistos y registro histórico.
*   **Base de Datos en la Nube:** Integración nativa con Google Sheets.

## 🛠️ Tecnologías Utilizadas

*   **Lenguaje:** Python 3.11
*   **Frontend y Dashboard:** Streamlit
*   **Manipulación de Datos:** Pandas
*   **Base de Datos:** Google Sheets API (`st-gsheets-connection`)

## ⚙️ Estructura del Proyecto

*   `app.py`: Script principal que contiene la lógica de la interfaz y la conexión a la base de datos.
*   `config.json`: Archivo de configuración centralizado para modificar rápidamente los botones, categorías y opciones de tiempo sin alterar el código Python.
*   `environment.yml`: Archivo de entorno para la gestión de dependencias con Conda.

## 💻 Instalación y Uso Local

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/crespomj/Task_Time_Manager.git](https://github.com/crespomj/Task_Time_Manager.git)
    cd Task_Time_Manager
