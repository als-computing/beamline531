from dash import Dash
from layout.app_layout import get_app_layout
from callback.move import move_callback
from callback.read import read_callback
from callback.scaler import plot_scaler
import dash_bootstrap_components as dbc
import sys, os

sys.path.append("/home/bl531/bl531_gui/beamline531_gyl")
from beamline_service.epicsDB.epicsdb_utils import getListOphydDashItems
from helper_utils import BeamlineComponents


def get_beamline_components(BL_API_URL, BL_API_KEY, BL_UID):
    # Get beamline PVs from MongoDB as OphydDash object
    response = requests.get(
        f"{BL_API_URL}/beamline/{BL_UID}/components", headers={"api_key": BL_API_KEY}
    )
    if response.status_code != 200:
        raise BeamlineComponentsNotFound(f"Status code: {response.status_code}")
    ophyd_items = get_ophyd_dash_items(raw_json=response.json())
    component_list = BeamlineComponents(ophyd_items)
    return component_list


def get_beamline_components_json(
    json_path="./beamline_service/epicsDB/epicsHappi_DB.json",
):
    l = getListOphydDashItems(json_path=json_path)
    return BeamlineComponents(l)


class bl531App:
    BL_API_URL = str(os.environ.get("BL_API_URL"))
    BL_API_KEY = str(os.environ.get("BL_API_KEY"))
    BL_UID = str(os.environ.get("BL_UID"))
    app = None

    def __init__(
        self,
        title="BL 5.3.1",
        favicon="LBL_icon.ico",
        # beamline="als_5_3_1",
        # version="0",
    ):
        # Set up app
        self.setup_app(title=title, favicon=favicon)

        # Get beamline components
        # self.component_list = self.get_beamline_components(self.BL_API_URL, self.BL_API_KEY, self.BL_UID)
        self.component_list = get_beamline_components_json()
        self.component_gui = self.component_list.get_gui()

        # Dropdown options for live scalers
        self.dropdown_scalers = ["Time"] + self.component_list.comp_id_list

        # Assign app layout
        self.assign_layout()

        # Link GUI components with callback functions
        move_callback(self.app, self.component_list)
        read_callback(self.app, self.component_list)
        plot_scaler(self.app, self.component_list)

    def assign_layout(
        self,
        src_app_logo="assets/LBL_logo.png",
        logo_height="60px",
        app_title="Advanced Light Source | Beamline 5.3.1",
    ):
        layout = get_app_layout(
            self.component_list,
            self.component_gui,
            self.dropdown_scalers,
            src_app_logo=src_app_logo,
            logo_height=logo_height,
            app_title=app_title,
        )
        self.app.layout = layout

    def setup_app(
        self,
        title="BL 5.3.1",
        favicon="LBL_icon.ico",
        # beamline="als_5_3_1",
        # version="0",
    ):
        #### SETUP DASH APP ####
        external_stylesheets = [
            dbc.themes.BOOTSTRAP,
            "../assets/style.css",
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
        ]
        self.app = Dash(__name__, external_stylesheets=external_stylesheets)
        self.app.title = title
        self.app._favicon = favicon

    # def run(self, port="8053", host="0,0,0,0"):
    #     self.app.run_server(debug=True, host=host, port=port)


if __name__ == "__main__":
    bl531_gui = bl531App()
    bl531_gui.app.run_server(debug=True, host="0.0.0.0", port="8053")
