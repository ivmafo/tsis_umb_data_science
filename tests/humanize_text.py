import re
import random
import requests
import textwrap

class ColombianHumanizerPro:
    """
    Versión avanzada del humanizador que simula patrones de escritura humana:
    1. Ráfaga (Burstiness): Variedad en longitud de oraciones.
    2. Perplejidad: Vocabulario de nicho y local.
    3. Contexto: Anclaje a la realidad colombiana (Aerocivil, El Dorado).
    4. Opinión: Matices críticos y autocrítica.
    """

    def __init__(self):
        # Mapeo de vocabulario "Corporativo/IA" a "Humano/Nicho"
        self.vocab_map = {
            r'\bimportante\b': ['clave', 'crucial', 'que no se nos puede pasar', 'vital'],
            r'\boptimizar\b': ['sacarle el jugo', 'afinar', 'desenredar', 'pulir'],
            r'\bgarantizar\b': ['asegurar', 'velar por', 'hacer que funcione sí o sí'],
            r'\bmétrica\b': ['el dato', 'la cifra que manda', 'el termómetro'],
            r'\bdesafío\b': ['reto bravo', 'chicharrón', 'camello'],
            r'\befficiente\b': ['que vuela', 'fino', 'sin tanta vuelta'],
            r'\brecurso\b': ['lo que hay', 'las herramientas', 'el equipo'],
            r'\banálisis\b': ['echarle cabeza', 'estudio a fondo', 'radiografía'],
        }

        # Contexto Local (Aerocivil, El Dorado, Regiones)
        self.context_injections = {
            r'\btorre de control\b': [
                'torre de control (como la del Dorado o Rionegro)',
                'torre, pensando en nuestra realidad local,'
            ],
            r'\btraffic management\b': [
                'manejo del tráfico (con lo complicado que es acá)',
                'gestión del espacio aéreo'
            ],
            r'\baeronáutica civil\b': [
                'la Aerocivil', 'la autoridad', 'nuestra Aeronáutica'
            ],
             r'\bbase de datos\b': [
                'la base de datos (ojalá no sea un Excel gigante)', 'el repositorio'
            ],
        }

        # Conectores Críticos / Reflexivos
        self.critical_connectors = [
            ", y ojo que esto no es menor,", 
            ". Bueno, viéndolo bien, ", 
            "; aunque claro, la teoría aguanta todo, pero ",
            ". Y aquí es donde la puerca tuerce el rabo: ",
            ", cosa que a veces pasamos por alto, "
        ]

    def _call_datamuse_synonym(self, word: str) -> str:
        """Intenta buscar un sinónimo inusual en la web para aumentar perplejidad."""
        try:
            # Busca palabras relacionadas que suenen 'técnicas' o 'inusuales'
            url = f"https://api.datamuse.com/words?ml={word}&max=3"
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                options = [w['word'] for w in resp.json()]
                if options:
                    return random.choice(options)
        except:
            return word # Fallback
        return word

    def _inject_burstiness(self, text: str) -> str:
        """
        Rompe la monotonía combinando oraciones cortas o partiendo largas.
        Simula el ritmo de pensamiento humano.
        """
        sentences = text.split('. ')
        new_sentences = []
        i = 0
        while i < len(sentences):
            current = sentences[i].strip()
            if not current: 
                i += 1
                continue
                
            # Decisión aleatoria: Combinar, Partir o Dejar igual
            dice = random.random()
            
            if dice < 0.2 and i < len(sentences) - 1: # Combinar con la siguiente (oración larga y compleja)
                next_s = sentences[i+1].strip()
                connector = random.choice([", y además ", "; es más, ", ", lo que nos lleva a que "])
                combined = current + connector + next_s
                new_sentences.append(combined)
                i += 2
            elif dice > 0.8 and len(current.split()) > 20: # Partir una muy larga (énfasis corto)
                # Buscar una coma o 'y' para partir
                parts = re.split(r', | y ', current, 1)
                if len(parts) > 1:
                    new_sentences.append(parts[0] + ". " + parts[1].capitalize())
                else:
                    new_sentences.append(current)
                i += 1
            else:
                new_sentences.append(current)
                i += 1
        
        return ". ".join(new_sentences)

    def _apply_vocabulary_layer(self, text: str) -> str:
        """Sustituye palabras corporativas por jerga de nicho."""
        for pattern, replacements in self.vocab_map.items():
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, lambda x: random.choice(replacements), text, flags=re.IGNORECASE)
        return text

    def _inject_critical_context(self, text: str) -> str:
        """Añade opiniones y contexto local."""
        # Inyectar contexto local
        for pattern, replacements in self.context_injections.items():
            if re.search(pattern, text, re.IGNORECASE) and random.random() > 0.6:
                text = re.sub(pattern, lambda x: random.choice(replacements), text, count=1, flags=re.IGNORECASE)
        
        # Inyectar conectores críticos al azar
        words = text.split()
        if len(words) > 30:
            insert_pos = random.randint(10, len(words) - 10)
            words.insert(insert_pos, random.choice(self.critical_connectors))
        
        return " ".join(words).replace(" ,", ",").replace(" .", ".")

    def humanize(self, text: str) -> str:
        print(f"\n[ENTRADA]: {text[:100]}... (longitud: {len(text)})\n")
        
        # 1. Pipeline de Transformación
        # Burstiness (Estructura)
        step1 = self._inject_burstiness(text)
        
        # Perplejidad (Vocabulario)
        step2 = self._apply_vocabulary_layer(step1)
        
        # Contexto y Crítica
        step3 = self._inject_critical_context(step2)
        
        # Limpieza final
        final_text = step3
        if not final_text.endswith('.'):
            final_text += '.'
            
        print(f"--- [SALIDA HUMANIZADA] ---\n")
        print(textwrap.fill(final_text, width=80))
        print("\n" + "-"*60 + "\n")
        return final_text

if __name__ == "__main__":
    h = ColombianHumanizerPro()
    
    # Texto proporcionado por el usuario
    long_text = "En Colombia la gestión del tráfico aéreo es un aspecto crítico de la industria de transporte, por lo que es importante garantizar una operación segura y eficiente en los sistemas de aviación, debido a esto el análisis de los datos es vital. La tendencia creciente de la demanda de viajes, hacen vital e importante los controles y métricas de puntualidad, coordinación y complejidad del tráfico aéreo; lo cual plantea desafíos muy significativos para las torres de control de tráfico aéreo y su personal. En este contexto, el uso de técnicas de ciencia de datos se vuelve esencial para mejorar la eficiencia y la seguridad de la gestión del tráfico aéreo mediante el análisis de grandes volúmenes de datos para la toma de decisiones y optimizar las operaciones de tráfico aéreo. Este trabajo de grado se centra en el análisis de datos de registro de vuelos de una torre de control de tráfico aéreo, extraído de las bases de datos abiertos de la Aeronáutica Civil Colombiana, mediante el uso de la plataforma de datos abiertos del gobierno nacional. https://www.aerocivil.gov.co/analitica; si bien, existe una buena analítica con respecto a los números de vuelo, operadores, destinos, arribos y cantidad de pasajeros transportados, no existe una métrica de horarios de vuelos que haga un análisis sobre horarios valle y pico de entrada y salida de vuelos, lo que en si puede representar un riesgo para control aéreo, ya que el personal es planificado sin tener en cuenta algunas veces la carga laboral probable. El análisis de estos horarios y demanda de vuelos puede permitir una mejor distribución del personal de torre de control y distribución de turnos, así como la cantidad de controladores necesarios para horarios pico y valle, garantizando una operación más eficiente y segura. Utilizando metodologías de ciencia de datos. El objetivo principal es mejorar la gestión del tráfico aéreo aprovechando los conocimientos extraídos de la información registrada de los vuelos. Mediante el empleo de técnicas de ciencia de datos, buscamos predecir los tiempos de vuelo y las demoras, identificar patrones y similitudes entre los vuelos y optimizar la asignación de recursos y horarios de vuelo.A pesar de la importancia de los datos disponibles, previamente no se ha realizado un análisis exploratorio de datos en este aspecto. Por lo tanto, la primera parte de este estudio se enfocará en obtener una comprensión integral de la distribución y las características de los vuelos registrados. El alcance de esta investigación abarca la aplicación de algoritmos de aprendizaje automático para la predicción, técnicas de agrupación para la clasificación y algoritmos de optimización para la asignación de recursos.Esta investigación tiene una importancia primordial, ya que busca contribuir al avance de las prácticas de gestión del tráfico aéreo. Se espera que los resultados obtenidos optimicen la planificación y coordinación de vuelos, reduciendo las demoras y mejorando la eficiencia general en la torre de control de tráfico aéreo. Además, la aplicación de la ciencia de datos en el campo de la gestión del tráfico aéreo tiene implicaciones de gran alcance para la industria de la aviación, abriendo el camino para una mayor seguridad, una mayor satisfacción de los pasajeros y una mejor utilización de los recursos humanos y técnicos.En resumen, este trabajo de grado tiene como objetivo aprovechar el poder de la ciencia de datos para optimizar la gestión del tráfico aéreo, realizando una contribución significativa al campo y ofreciendo soluciones prácticas para la comunidad de la aviación. Los capítulos posteriores profundizarán en la metodología, los hallazgos y las conclusiones derivadas del análisis de los datos de registro de vuelos."

    h.humanize(long_text)
