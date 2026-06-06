# Procesador de Lenguaje Natural para Comandos de un Robot 

Este proyecto implementa un **Analizador Sintáctico y Semántico (Parser y Traductor)** . El objetivo principal es procesar instrucciones en lenguaje natural dirigidas a un robot (como "avanza 2 casillas" o "gira a la derecha 30 grados"), validar su coherencia sintáctica y semántica, extraer la intención del comando y visualizar la estructura gramatical mediante un árbol.

Desarrollado como parte del curso de Procesamiento de Lenguaje Natural en la **Universidad del Valle**.

## 🚀 Características del Proyecto

- **Gramática Integral Estricta:** Implementación explícita de reglas de producción para Oraciones (`S`), Sintagmas Nominales (`NP`) y Sintagmas Verbales (`VP`).
- **Análisis Basado en Rasgos (Unificación):** El sistema detecta y previene errores semánticos o incongruencias (por ejemplo, rechaza comandos erróneos como *"avanza 2 grados"* o *"gira a la derecha 30 casillas"*).
- **Procesamiento de Orden Única:** Optimizado para la ejecución limpia, lineal y eficiente de instrucciones individuales (un comando a la vez).
- **Interfaz Gráfica del Árbol Sintáctico:** Generación automática y jerárquica del árbol gramatical utilizando `matplotlib`, desglosando componentes mayores (Sintagmas) y categorías léxicas intermedias (`V`, `Det`, `N`).
- **Traductor Semántico:** Extracción directa de los parámetros operativos requeridos por el robot (Acción, Dirección, Magnitud y Unidad).

---

## 📐 Gramática Formal Implementada

El analizador se rige bajo la siguiente gramática formal libre de contexto enriquecida con restricciones de rasgos, diseñada para evitar completamente la ambigüedad en instrucciones individuales:

```python
gramatica = {
    'S':   [
        ['VP']                # Producción única: Oración de comando simple
    ],
    'NP':  [
        ['Det', 'Det', 'N'],  # Estructura para locuciones de dirección: "a la derecha"
        ['Det', 'N'],         # Estructura cuantitativa: "2 casillas", "30 grados"
        ['N']                 # Estructura nominal simple: "izquierda"
    ],
    'VP':  [
        ['V', 'Det', 'NP'],      # Comando de traslación lineal: "avanza 2 casillas"
        ['V', 'NP', 'Det', 'NP'] # Comando de rotación angular: "gira a la derecha 30 grados"
    ]
}

Analizador Léxico: El Autómata Finito (AFD)Para limpiar el texto que introduce el usuario y dividirlo en palabras individuales (tokens), el sistema simula un Autómata Finito Determinarístico. Su estructura formal simplificada es la siguiente:Estados 
(Q): {q_0, q_1, q_2, q_3 , q_4}
Alfabeto : categorias gramaticales {V, Det , NP} 
(q_0): El punto de partida antes de leer una palabra.
Estados de Aceptación (q_F): {q_4} (El sistema acepta la entrada cuando termina de procesar palabras o números válidos).
Cómo funciona el Autómata : Si está en q_0 y lee una palabara de categoria verbo, pasa al estado q_1 (Aceptación de Palabras como "avanza", "grados"). Si está en q_0 y lee una palabra diferente a verbo lo enviaria al estado trampa, en el estado q_1 si llega un Det pasa a q_3 y si llega un NP pasa a q_2 y si pasa a q_3 espara un NP y da la cadena como validad en caso de que llegue un NP pasa a q_2 y estando en q_2 espara un Det parpasar a q_3 y en q_3 espera un NP y llega a q_4 cadena aceptada en cada un de los estados si no llega las palabras esperadas se envia al estado trampa por lo cual no acepta las palabras. 

Estructura del Código

El archivo principal (proyecto.py) se encuentra modularizado bajo buenas prácticas de ingeniería de software en secciones clave:

Parte 1 (Algoritmo de Unificación): Función unificar(dag1, dag2) encargada de fusionar las estructuras de rasgos y validar la consistencia semántica descartando conflictos.

Parte 2 (Léxico): Diccionario expandido con las categorías gramaticales básicas y sus respectivos rasgos informativos (ej. tipo de medida, valor, dirección).

Parte 3 (Gramática): Declaración explícita y visible de las producciones gramaticales analizadas.

Parte 4 (Parser de Descenso Recursivo): Funciones parse_s, parse_vp y parse_np que analizan linealmente el flujo de tokens sin necesidad de recursiones complejas sobre conectores.

Parte 5 (Traductor Semántico Directo): Función extraer_intencion_robot que extrae y procesa la semántica operativa final una vez el parser ha unificado con éxito.

Parte 6 (Mapeador de Estructuras): Transforma el DAG anidado (diccionario de Python) en un árbol de tuplas legible por la librería gráfica.

Parte 7 (Función Gráfica): Dibuja recursivamente el árbol en un lienzo de matplotlib, aplicando códigos de color normalizados para facilitar la sustentación académica.

Ejemplos de Ejecución y Validación
El sistema viene configurado con ejemplos nativos de validación. Al correr el programa se producen las siguientes salidas en terminal:

1. Entrada: "avanza 2 casillas"
Consola:

Instrucción recibida: "avanza 2 casillas"
Estado ----> Comando válido (Unificación exitosa).
Resultado -> Acción: Caminar | Cantidad: 2 casillas

Nomenclatura Visual del Árbol Sintáctico
Para facilitar la sustentación y comprensión en la entrega, el gráfico utiliza la siguiente paleta de colores:

🟦 Azul Claro (lightblue): Nodos correspondientes a Sintagmas mayores (S, VP, NP).

🟧 Naranja Pastel (peachpuff): Categorías gramaticales básicas o intermedias (V, Det, N).

🟩 Verde Claro (lightgreen): Palabras léxicas finales o tokens terminales ingresados por el usuario.

Autor

Juan Pablo Ochoa Alvarez

Estudiante de Tecnología en desarrollo de software

Universidad del Valle
