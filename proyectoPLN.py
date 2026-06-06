import matplotlib.pyplot as plt

# ============================================================
# PARTE 1: ALGORITMO DE UNIFICACIÓN 
# ============================================================
def unificar(dag1, dag2):
    if dag1 is None or dag2 is None:
        return None
    
    resultado = dict(dag1)
    for rasgo, valor in dag2.items():
        if rasgo in resultado:
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None
                resultado[rasgo] = sub
            elif resultado[rasgo] != valor:
                return None  # Descarta interpretaciones semánticas erróneas
        else:
            resultado[rasgo] = valor
    return resultado

# ============================================================
# PARTE 2: LÉXICO CON ESTRUCTURAS DE RASGOS (DAGs)
# ============================================================
lexico = {
    'avanza':   {'cat': 'V', 'accion': 'Mover'},
    'camina':   {'cat': 'V', 'accion': 'Mover'},
    'gira':     {'cat': 'V', 'accion': 'Mover'},
    'rota':     {'cat': 'V', 'accion': 'Mover'},
    
    'a':        {'cat': 'Det', 'tipo_det': 'conector'},
    'la':       {'cat': 'Det', 'tipo_det': 'articulo'},
    'el':       {'cat': 'Det', 'tipo_det': 'articulo'},
    
    '2':        {'cat': 'Det', 'tipo_det': 'numeral', 'medida': 'distancia', 'valor': '2'},
    '30':       {'cat': 'Det', 'tipo_det': 'numeral', 'medida': 'angulo',    'valor': '30'},
    '45':       {'cat': 'Det', 'tipo_det': 'numeral', 'medida': 'angulo',    'valor': '45'},
    
    'izquierda':{'cat': 'N', 'giro': 'Izquierda'},
    'derecha':  {'cat': 'N', 'giro': 'Derecha'},
    'casillas': {'cat': 'N', 'unidad': 'distancia'},
    'casilla':  {'cat': 'N', 'unidad': 'distancia'},
    'grados':   {'cat': 'N', 'unidad': 'angulo'},
    'grado':    {'cat': 'N', 'unidad': 'angulo'}
}

# ============================================================
# PARTE 3: LA GRAMÁTICA INTEGRAL ESTRICTA
# ============================================================
gramatica = {
    'S':   [['VP']],                  
    'NP':  [
        ['Det', 'Det', 'N'],          # "a la derecha"
        ['Det', 'N'],                 # "2 casillas", "30 grados"
        ['N']                         # "izquierda"
    ],
    'VP':  [
        ['V', 'Det', 'NP'],           # "avanza 2 casillas"
        ['V', 'NP', 'Det', 'NP']      # "gira a la derecha 30 grados"
    ]
}

# ============================================================
# PARTE 4: PARSER DE DESCENSO RECURSIVO
# ============================================================
def parse_np(tokens, pos):
    if pos >= len(tokens): return None, pos
    palabra1 = tokens[pos]
    if palabra1 not in lexico: return None, pos
    rasgos_p1 = lexico[palabra1]

    # NP -> Det Det N
    if pos + 2 < len(tokens):
        palabra2 = tokens[pos + 1]
        palabra3 = tokens[pos + 2]
        if (palabra2 in lexico and lexico[palabra2]['cat'] == 'Det' and 
            palabra3 in lexico and lexico[palabra3]['cat'] == 'N'):
            return {
                'cat': 'NP', 'hijo_tipo': 'Det_Det_N',
                'det1_word': palabra1, 'det2_word': palabra2, 'n_word': palabra3,
                'rasgos': lexico[palabra3]
            }, pos + 3

    # NP -> Det N (Verificación de rasgos)
    if pos + 1 < len(tokens):
        palabra2 = tokens[pos + 1]
        if palabra2 in lexico and lexico[palabra2]['cat'] == 'N':
            check_medida = {'tipo': rasgos_p1.get('medida')} if 'medida' in rasgos_p1 else {}
            check_unidad = {'tipo': lexico[palabra2].get('unidad')} if 'unidad' in lexico[palabra2] else {}
            if unificar(check_medida, check_unidad) is not None:
                return {
                    'cat': 'NP', 'hijo_tipo': 'Det_N',
                    'det_word': palabra1, 'n_word': palabra2, 
                    'rasgos': unificar(rasgos_p1, lexico[palabra2])
                }, pos + 2

    # NP -> N
    if rasgos_p1['cat'] == 'N':
        return {'cat': 'NP', 'hijo_tipo': 'N', 'n_word': palabra1, 'rasgos': rasgos_p1}, pos + 1
    return None, pos

def parse_vp(tokens, pos):
    if pos >= len(tokens): return None, pos
    palabra_v = tokens[pos]
    if palabra_v not in lexico or lexico[palabra_v]['cat'] != 'V': return None, pos
    pos_actual = pos + 1

    # VP -> V NP Det NP ("gira a la derecha 30 grados")
    pos_temp = pos_actual
    np1, pos_temp = parse_np(tokens, pos_temp)
    if np1 is not None and pos_temp < len(tokens):
        palabra_det = tokens[pos_temp]
        if palabra_det in lexico and lexico[palabra_det]['cat'] == 'Det':
            np2, pos_final_vp = parse_np(tokens, pos_temp + 1)
            if np2 is not None:
                check_medida = {'tipo': lexico[palabra_det].get('medida')} if 'medida' in lexico[palabra_det] else {}
                check_unidad = {'tipo': np2['rasgos'].get('unidad')} if 'unidad' in np2['rasgos'] else {}
                if unificar(check_medida, check_unidad) is not None:
                    return {
                        'cat': 'VP', 'hijo_tipo': 'V_NP_Det_NP', 'v_word': palabra_v, 
                        'np1': np1, 'det_word': palabra_det, 'np2': np2, 'rasgos': lexico[palabra_v]
                    }, pos_final_vp

    # VP -> V Det NP ("avanza 2 casillas")
    if pos_actual < len(tokens):
        palabra_det = tokens[pos_actual]
        if palabra_det in lexico and lexico[palabra_det]['cat'] == 'Det':
            
            # === CORRECCIÓN DE SEGURIDAD ===
            # Verificamos que el Det sea un numeral (un número). Si es un conector como "a", abortamos.
            if lexico[palabra_det].get('tipo_det') != 'numeral':
                return None, pos
                
            # ===============================

            np, pos_final_vp = parse_np(tokens, pos_actual + 1)
            if np is not None:
                check_medida = {'tipo': lexico[palabra_det].get('medida')} if 'medida' in lexico[palabra_det] else {}
                check_unidad = {'tipo': np['rasgos'].get('unidad')} if 'unidad' in np['rasgos'] else {}
                if unificar(check_medida, check_unidad) is not None:
                    return {
                        'cat': 'VP', 'hijo_tipo': 'V_Det_NP', 'v_word': palabra_v,
                        'det_word': palabra_det, 'np': np, 'rasgos': lexico[palabra_v]
                    }, pos_final_vp
                

def parse_s(tokens, pos=0):
    vp, pos_actual = parse_vp(tokens, pos)
    if vp is None: return None, pos
    return {'cat': 'S', 'hijo_tipo': 'VP', 'vp': vp, 'rasgos': vp.get('rasgos', {})}, pos_actual

# ============================================================
# PARTE 5: TRADUCTOR SEMÁNTICO 
# ============================================================
def extraer_intencion_robot(tokens):
    # Buscamos si es una acción de avance o de giro analizando las palabras clave
    es_giro = "gira" in tokens or "rota" in tokens
    
    # Valores por defecto 
    accion = "Mover"
    cantidad = 0
    direccion = "No aplica"
    grados = 0
    
    # Extraemos los datos basándonos en el léxico unificado
    for t in tokens:
        if t in lexico:
            datos = lexico[t]
            if datos['cat'] == 'Det' and datos.get('tipo_det') == 'numeral':
                if datos.get('medida') == 'distancia':
                    cantidad = int(datos['valor'])
                elif datos.get('medida') == 'angulo':
                    grados = int(datos['valor'])
            elif datos['cat'] == 'N' and 'giro' in datos:
                direccion = datos['giro']

    # Si es un comando de avance directo, la dirección no aplica y grados es 0
    if not es_giro:
        direccion = "No aplica"
        grados = 0
    else:
        cantidad = 0  # En los giros, según el ejemplo, la cantidad de casillas es 0
        
    print(f"Salida -> Acción: {accion} - Cantidad: {cantidad} - Dirección: {direccion} - Grados: {grados}")

# ============================================================
# PARTE 6: MAPEO DEL DAG PARA EL ÁRBOL VISUAL
# ============================================================
def mapear_dag_a_arbol(dag):
    if not isinstance(dag, dict): return str(dag)
    categoria = dag['cat']
    hijos = []
    tipo = dag.get('hijo_tipo', '')
    
    if tipo == 'VP':
        hijos.append(mapear_dag_a_arbol(dag['vp']))
    elif tipo == 'V_NP_Det_NP':
        hijos.append(('V', [dag['v_word']]))
        hijos.append(mapear_dag_a_arbol(dag['np1']))
        hijos.append(('Det', [dag['det_word']]))
        hijos.append(mapear_dag_a_arbol(dag['np2']))
    elif tipo == 'V_Det_NP':
        hijos.append(('V', [dag['v_word']]))
        hijos.append(('Det', [dag['det_word']]))
        hijos.append(mapear_dag_a_arbol(dag['np']))
    elif tipo == 'Det_Det_N':
        hijos.append(('Det', [dag['det1_word']]))
        hijos.append(('Det', [dag['det2_word']]))
        hijos.append(('N', [dag['n_word']]))
    elif tipo == 'Det_N':
        hijos.append(('Det', [dag['det_word']]))
        hijos.append(('N', [dag['n_word']]))
    elif tipo == 'N':
        hijos.append(('N', [dag['n_word']]))
        
    return (categoria, hijos)

# ============================================================
# PARTE 7: FUNCIÓN GRÁFICA (Matplotlib)
# ============================================================
def dibujar_arbol_formal(nodo_tupla, ax, x, y, ancho):
    if not isinstance(nodo_tupla, tuple):
        ax.text(x, y, nodo_tupla, ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen'))
        return
    etiqueta, hijos = nodo_tupla
    color = 'lightblue' if etiqueta in ['S', 'VP', 'NP'] else 'peachpuff'
    ax.text(x, y, etiqueta, ha='center', va='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=color))
    if not hijos: return
    n = len(hijos)
    x_ini = x - ancho / 2
    for hijo in hijos:
        ancho_hijo = ancho / n
        x_hijo = x_ini + ancho_hijo / 2
        y_hijo = y - 1.0
        ax.plot([x, x_hijo], [y - 0.15, y_hijo + 0.15], 'k-', lw=1.1)
        dibujar_arbol_formal(hijo, ax, x_hijo, y_hijo, ancho_hijo)
        x_ini += ancho_hijo


# ============================================================
# PARTE 8: CONTROLADOR DE PRUEBAS (Con captura de excepciones)
# ============================================================
def procesar_instruccion(texto_usuario):
    print(f"\nEntrada: {texto_usuario}")
    
    # 1. Simulación del Autómata Finito (Lexer)
    tokens = texto_usuario.lower().split()
    
    try:
        # 2. Intenta realizar el análisis sintáctico (Parser)
        arbol_dag, pos_final = parse_s(tokens, 0)

        # Si el parser devolvió None o no consumió todas las palabras, la estructura está mal
        if arbol_dag is None or pos_final != len(tokens):
            print("Salida -> Error: Estructura sintáctica o semántica inválida.")
            return # Detiene la función aquí para que no intente graficar nada

        # 3. Si la estructura es correcta, ejecuta el Traductor Semántico
        extraer_intencion_robot(tokens)
        
        # 4. Generar gráfico del árbol estructurado (Matplotlib)
        tupla_grafica = mapear_dag_a_arbol(arbol_dag)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis('off')
        dibujar_arbol_formal(tupla_grafica, ax, 5, 5.5, 10)
        plt.title(f"Árbol Sintáctico - Compilador de Órdenes Robóticas", fontsize=11)
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        # Aquí capturamos cualquier error inesperado de Python (como intentar leer datos de un None)
        # y lo transformamos en un mensaje controlado para el usuario
        print("Salida -> Error: Estructura sintáctica o semántica inválida.")
        
# Pruebas con ejemplos:
procesar_instruccion("avanza 2 casillas")
procesar_instruccion("gira a la derecha 30 grados")
procesar_instruccion("avanza 2 casillas avanza")
procesar_instruccion("avanza")
procesar_instruccion("")
procesar_instruccion("2 casillas")
procesar_instruccion("avanza a izquierda")