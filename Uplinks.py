import streamlit as st
import pandas as pd
import os

import meraki

st.set_page_config(
     page_title="MerakiLit - Uplinks",
     layout="wide",
     initial_sidebar_state="expanded"
 )

st.title('Estado Uplinks Meraki MX Firewalls')

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
    # Instantiate a Meraki dashboard API session
    dashboard = meraki.DashboardAPI(
        api_key=st.secrets["API_KEY"],
        base_url='https://api.meraki.com/api/v1/',
        output_log=False,
        log_file_prefix=os.path.basename(__file__)[:-3],
        log_path='',
        print_console=False
    )


    #if st.button('Ver estado de Enlaces', key='enlaces'):
    organizations = dashboard.organizations.getOrganizations()
    for org in organizations:
        org_id = org['id']
        
        try:
            devices = dashboard.organizations.getOrganizationUplinksStatuses(org_id)
        except meraki.APIError as e:
            print(f'Meraki API error: {e}')
            print(f'status code = {e.status}')
            print(f'reason = {e.reason}')
            print(f'error = {e.message}')
            continue
        except Exception as e:
            print(f'some other error: {e}')
            continue
    
        #todays_date = f'{datetime.now():%Y-%m-%d}'
        #folder_name = f'Org {org_id} clients {todays_date}'
        #if folder_name not in os.listdir():
        #    os.mkdir(folder_name)
            
        total = len(devices)
        counter = 1
        cols = ["Red","Timezone", "Modelo", "Fecha", "WAN 1", "WAN 2"]
        rows = []
        
        with st.spinner('Buscando Información...'):
            for dev in devices:
                red = dashboard.networks.getNetwork(dev["networkId"])
                nombre_red = red["name"]
                timezone = red["timeZone"]
                
                try:
                    rows.append({"Red":nombre_red,
                                "Timezone": timezone,
                                "Modelo": dev["model"],
                                "Fecha": dev["lastReportedAt"],
                                "WAN 1": dev["uplinks"][0]["status"],
                                "WAN 2": dev["uplinks"][1]["status"]
                    })
                except:
                    rows.append({"Red":nombre_red,
                                "Timezone": timezone,
                                "Modelo": dev["model"],
                                "Fecha": dev["lastReportedAt"],
                                "WAN 1": dev["uplinks"][0]["status"],
                                "WAN 2": ""
                    })
            
            def highlight_cells(value):
                if value == 'failed':
                    color = '#FFB3BA' # Red
                elif value == 'active':
                    color = '#BAFFC9' # Green
                elif value == 'ready':
                    color = '#BAE1FF' # Blue
                else:
                    color = ''
                return 'background-color: {}'.format(color)
            
            df = pd.DataFrame(rows, columns=cols)
            rerun_button = st.button('Recargar')
            if rerun_button:
                st.experimental_rerun()
            st.dataframe(df.style.applymap(highlight_cells), height=950)
