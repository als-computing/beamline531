import dash
from dash.dependencies import Input, Output, State
from happi.client import from_container


def camControl(app, cam_list):
    cam_name_list = cam_list.comp_id_list

    def getCamOphyd(cam_name):
        cam_ophyd_dash = cam_list.find_component(cam_name)
        cam_ophyd = cam_ophyd_dash.ophyd_obj
        cam = cam_ophyd.cam
        return cam

    @app.callback(
        Output("stream-url", "value"),
        Output("img-mode", "options"),
        Output("cam-exp", "value"),
        Output("xpix-st", "value"),
        Output("xpix-ed", "value"),
        Output("ypix-st", "value"),
        Output("ypix-ed", "value"),
        Output("stream-status", "value", allow_duplicate=True),
        Input("cam-pv", "value"),
        prevent_initial_call='initial_duplicate'
        # prevent_initial_call=True,
    )
    def _selectCam(cam_name):
        msg = ""
        options = []
        exp_time, xpix_st, xpix_ed, ypix_st, ypix_ed = 0, 0, 0, 0, 0
        cam = getCamOphyd(cam_name)
        stream_url = 'ws://localhost:8000/ws/pva' #"ws://streamer_api:8000/ws/pva"
        # cam_ophyd_dash = cam_list.find_component(cam_name)
        # cam_ophyd = cam_ophyd_dash.ophyd_obj
        # cam = cam_ophyd.cam

        try:
            image_mode = cam.image_mode
            options = [
                {"label": l, "value": i}
                for i, l in enumerate(image_mode.metadata["enum_strs"])
            ]
            stream_url = 'ws://localhost:8000/ws/pva' #"ws://streamer_api:8000/ws/pva"
            # stream_url = f"ws://127.0.0.1:8000/ws/{cam_name}"
            exp_time = cam.acquire_time.get()
            xpix_st = cam.min_x.get()
            ypix_st = cam.min_y.get()
            xpix_ed = cam.size.size_x.get()
            ypix_ed = cam.size.size_y.get()
            msg = f"Connect to the detector {cam_name}, sync detector settings"
        except Exception as e:
            msg = f"Having issue reaching {cam_name} \nCannot retrieve value of {e} \nCheck if both IOC and detector are on"

        return (
            stream_url,
            options,
            exp_time,
            xpix_st,
            xpix_ed,
            ypix_st,
            ypix_ed,
            (msg),
        )

    @app.callback(
        Output("stream-status", "value", allow_duplicate=True),
        State("cam-pv", "value"),
        Input("img-mode", "value"),
        Input("cam-exp", "value"),
        Input("xpix-st", "value"),
        Input("xpix-ed", "value"),
        Input("ypix-st", "value"),
        Input("ypix-ed", "value"),
        State("stream-status", "value"),
        prevent_initial_call=True,
    )
    def _updateCam(
        cam_name, img_mode_idx, cam_exp, xpix_st, xpix_ed, ypix_st, ypix_ed, msg_old
    ):
        cam = getCamOphyd(cam_name)
        # cam_ophyd_dash = cam_list.find_component(cam_name)
        # cam = cam_ophyd_dash.ophyd_obj.cam
        msg = ""
        if img_mode_idx is not None:
            try:
                image_mode = cam.image_mode.metadata["enum_strs"]
                mode_name = image_mode[img_mode_idx]
                cam.image_mode.put(img_mode_idx)
                msg += f"Changing {cam_name}'s imaging mode to {mode_name}\n"

                cam.acquire_time.put(cam_exp)
                msg += f"Changing {cam_name}'s acquire_time to {cam_exp}\n"

                cam.min_x.put(xpix_st)
                msg += f"Changing {cam_name}'s x-pixel start to {xpix_st}\n"

                cam.min_y.put(ypix_st)
                msg += f"Changing {cam_name}'s y-pixel start to {ypix_st}\n"

                cam.size.size_x.put(xpix_ed)
                msg += f"Changing {cam_name}'s x-pixel size {xpix_ed}\n"

                cam.size.size_y.put(ypix_ed)
                msg += f"Changing {cam_name}'s y-pixel size {ypix_ed}\n"

            except Exception as e:
                msg += f"Having issue changing image mode. \n{e}"
        else:
            msg = msg_old

        return msg

    @app.callback(
        Output("stream-status", "value", allow_duplicate=True),
        Input("cam-acquire", "n_clicks"),
        State("cam-pv", "value"),
        prevent_initial_call=True,
    )
    def _camAcquire(acquire_click, cam_name):
        cam = getCamOphyd(cam_name)
        acquire_state = cam.acquire.get()
        if acquire_state:
            msg = f"{cam_name} is in acquiring mode"
        else:
            cam.acquire.put(1)
            msg = f"Trigger the {cam_name} to acquire data with the settings above"
        return msg

    @app.callback(
        Output("stream-status", "value", allow_duplicate=True),
        Input("cam-stop", "n_clicks"),
        State("cam-pv", "value"),
        prevent_initial_call=True,
    )
    def _camStop(stop_acquire, cam_name):
        cam = getCamOphyd(cam_name)
        acquire_state = cam.acquire.get()
        if acquire_state:
            cam.acquire.put(0)
            msg = f"{cam_name} is in acquiring mode, stopping the camera now"
        else:
            msg = f"{cam_name} is not actively acquiring data"
        return msg
