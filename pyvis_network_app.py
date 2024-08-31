import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
from PIL import Image

# Verificar si la clave 'DATABASE_PASSWORD' existe en st.secrets
if "DATABASE_PASSWORD" not in st.secrets:
    st.error("No se encontró 'DATABASE_PASSWORD' en los secretos. Verifica la configuración en GitHub.")
else:
    # Pedir al usuario que ingrese la contraseña
    password = st.text_input("Enter your password", type="password")

    # Verificar si la contraseña ingresada coincide con la almacenada en los secretos
    if password == st.secrets["DATABASE_PASSWORD"]:
        st.success("Contraseña correcta!")

        # Mostrar la imagen
        st.image('People.jpg', use_column_width=True)

        # Leer el dataset (CSV)
        df_survey = pd.read_csv('data/survey_results.csv')

        # Título de la aplicación
        st.title('Análisis de redes organizacionales - Capacidades de las personas')

        # Lista de capacidades únicas y ordenarlas alfabéticamente
        capacity_list = sorted(df_survey['capacity'].unique())

        # Mapeo de colores para las capacidades
        color_map = {
            'Liderazgo': 'red',
            'Comunicación': 'blue',
            'Trabajo en equipo': 'green',
            'Facilitación': 'orange',
            'Gestion del cambio': 'purple'
        }

        # Menú desplegable para seleccionar capacidades
        selected_capacities = st.multiselect('Selecciona las capacidades a visualizar', capacity_list)

        # Mensaje inicial si no se selecciona ninguna capacidad
        if len(selected_capacities) == 0:
            st.text('Escoge al menos una para iniciar')
        else:
            # Filtrar el DataFrame según las capacidades seleccionadas
            df_select = df_survey[df_survey['capacity'].isin(selected_capacities)]
            df_select = df_select.reset_index(drop=True)

            # Crear objeto de grafo con NetworkX a partir del DataFrame
            G = nx.from_pandas_edgelist(df_select, 'person_name', 'capacity', 'weight', create_using=nx.Graph())

            # Iniciar objeto de PyVis Network
            person_net = Network(
                height='400px',
                width='100%',
                bgcolor='#222222',
                font_color='white'
            )

            # Agregar nodos con colores
            for node in G.nodes():
                if node in df_select['person_name'].values:
                    # Color de nodos por defecto (blanco)
                    person_net.add_node(node, label=node, color='white')
                else:
                    # Color de nodos por capacidad
                    capacity = df_select[df_select['capacity'] == node]['capacity'].values[0]
                    person_net.add_node(node, label=node, color=color_map[capacity])

            # Agregar bordes con colores
            for index, row in df_select.iterrows():
                person_net.add_edge(row['person_name'], row['capacity'], color=color_map[row['capacity']], value=row['weight'])

            # Generar red con configuraciones específicas de diseño
            person_net.repulsion(
                node_distance=420,
                central_gravity=0.33,
                spring_length=110,
                spring_strength=0.10,
                damping=0.95
            )

            # Guardar y leer el grafo como archivo HTML
            try:
                path = '/tmp'
                person_net.save_graph(f'{path}/pyvis_graph.html')
                HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')
            except:
                path = '/html_files'
                person_net.save_graph(f'{path}/pyvis_graph.html')
                HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

            # Cargar el archivo HTML en el componente HTML para mostrar en la página de Streamlit
            components.html(HtmlFile.read(), height=435)

        # Pie de página
        st.markdown(
            """
            <br>
            <h6>Para mayor información escribeme: https://www.linkedin.com/in/josemaguilar/ </h6>
            """, unsafe_allow_html=True
        )
    else:
        st.error("Contraseña incorrecta.")

