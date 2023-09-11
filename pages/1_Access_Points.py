import streamlit as st
import pandas as pd
import os

import meraki


st.set_page_config(
     page_title="MerakiLit - APs",
     layout="wide",
     initial_sidebar_state="expanded"
 )
 

st.title('Meraki Access Points')


# Instantiate a Meraki dashboard API session
dashboard = meraki.DashboardAPI(
    api_key=st.secrets["API_KEY"],
    base_url='https://api.meraki.com/api/v1/',
    output_log=False,
    log_file_prefix=os.path.basename(__file__)[:-3],
    log_path='',
    print_console=False
)

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    if st.button('Ver/Refrescar Estado', key='enlaces'):
        organizations = dashboard.organizations.getOrganizations()
        for org in organizations:
            org_id = org['id']
            
            try:
                devices = dashboard.organizations.getOrganizationDevicesStatuses(org_id, total_pages='all')
            except meraki.APIError as e:
                print(f'Meraki API error: {e}')
                print(f'status code = {e.status}')
                print(f'reason = {e.reason}')
                print(f'error = {e.message}')
                continue
            except Exception as e:
                print(f'some other error: {e}')
                continue
                
            total = len(devices)
            counter = 1
            cols = ["Nombre","Estado", "Modelo", "Serie"]
            rows = []
            
            with st.spinner('Buscando Información...'):
                for dev in devices:
                    try:
                        rows.append({"Nombre":dev["name"],
                                    "Estado": dev["status"],
                                    "Modelo": dev["model"],
                                    "Serie": dev["serial"]
                        })
                    except:
                        rows.append({"Nombre":"N/A",
                                    "Estado": "",
                                    "Modelo": "",
                                    "Serie": ""
                        })
                
                def highlight_cells(value):
                    if value == 'offline':
                        color = '#FFB3BA' # Red
                    elif value == 'online':
                        color = '#BAFFC9' # Green
                    elif value == 'alerting' or value == 'dormant':
                        color = '#BAE1FF' # Blue
                    else:
                        color = ''
                    return 'background-color: {}'.format(color)
                
                df = pd.DataFrame(rows, columns=cols)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Dispositivos Offline ("+str(len(df.query("Estado == 'offline'")))+")")
                    st.dataframe(df.query("Estado == 'offline'"))
                    
                    st.subheader("Alertando ("+str(len(df.query("Estado == 'alerting'")))+")")
                    st.dataframe(df.query("Estado == 'alerting'"))
                    
                    st.subheader("Offline por mas de una semana ("+str(len(df.query("Estado == 'dormant'")))+")")
                    st.dataframe(df.query("Estado == 'dormant'"))
                
                with col2:
                    st.subheader("Dispositivos Online ("+str(len(df.query("Estado == 'online'")))+")")
                    st.dataframe(df.query("Estado == 'online'"), height=950)