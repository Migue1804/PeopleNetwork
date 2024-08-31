import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

# Obtener la contraseña del secreto (debería ser configurada como una variable de entorno en GitHub)
SECRET_PASSWORD = os.getenv('DATABASE_PASSWORD', '')

# Configuración del formulario de autenticación
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def authenticate(password):
    return password == SECRET_PASSWORD

if not st.session_state.authenticated:
    st.title('Login')
    password_input = st.text_input('Enter password:', type='password')
    if st.button('Submit'):
        if authenticate(password_input):
            st.session_state.authenticated = True
            st.experimental_rerun()  # Recarga la aplicación
        else:
            st.error('Incorrect password')
else:
    # Read dataset (CSV)
    df_survey = pd.read_csv('data/survey_results.csv')

    # Set header title
    st.title('Network Graph Visualization of People and Their Capacities')

    # Define list of unique capacities and sort alphabetically
    capacity_list = sorted(df_survey['capacity'].unique())

    # Define color mapping for capacities
    color_map = {
        'Liderazgo': 'red',
        'Comunicación': 'blue',
        'Trabajo en equipo': 'green',
        'Facilitación': 'orange',
        'Gestion del cambio': 'purple'
    }

    # Implement multiselect dropdown menu for option selection (returns a list)
    selected_capacities = st.multiselect('Select capacity/capacities to visualize', capacity_list)

    # Set info message on initial site load
    if len(selected_capacities) == 0:
        st.text('Choose at least 1 capacity to start')

    # Create network graph when user selects >= 1 item
    else:
        df_select = df_survey[df_survey['capacity'].isin(selected_capacities)]
        df_select = df_select.reset_index(drop=True)

        # Create networkx graph object from pandas dataframe
        G = nx.from_pandas_edgelist(df_select, 'person_name', 'capacity', 'weight', create_using=nx.Graph())

        # Initiate PyVis network object
        person_net = Network(
                             height='400px',
                             width='100%',
                             bgcolor='#222222',
                             font_color='white'
                            )

        # Add nodes with colors
        for node in G.nodes():
            if node in df_select['person_name'].values:
                # Color nodes by person name default color (white)
                person_net.add_node(node, label=node, color='white')
            else:
                # Color nodes by capacity
                capacity = df_select[df_select['capacity'] == node]['capacity'].values[0]
                person_net.add_node(node, label=node, color=color_map[capacity])

        # Add edges with colors
        for index, row in df_select.iterrows():
            person_net.add_edge(row['person_name'], row['capacity'], color=color_map[row['capacity']], value=row['weight'])

        # Generate network with specific layout settings
        person_net.repulsion(
                             node_distance=420,
                             central_gravity=0.33,
                             spring_length=110,
                             spring_strength=0.10,
                             damping=0.95
                            )

        # Save and read graph as HTML file (on Streamlit Sharing)
        try:
            path = '/tmp'
            person_net.save_graph(f'{path}/pyvis_graph.html')
            HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Save and read graph as HTML file (locally)
        except:
            path = '/html_files'
            person_net.save_graph(f'{path}/pyvis_graph.html')
            HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Load HTML file in HTML component for display on Streamlit page
        components.html(HtmlFile.read(), height=435)

    # Footer
    st.markdown(
        """
        <br>
        <h6>Para mayor información escríbeme: https://www.linkedin.com/in/josemaguilar/ </h6>
        """, unsafe_allow_html=True
    )


