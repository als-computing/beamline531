from dash.dependencies import Input, Output, State, MATCH


def move_callback(app, component_list):
    @app.callback(
        Output({"base": MATCH, "type": "target-value"}, "data"),
        Output({"base": MATCH, "type": "target-go"}, "n_clicks"),
        Output({"base": MATCH, "type": "target-left"}, "n_clicks"),
        Output({"base": MATCH, "type": "target-right"}, "n_clicks"),
        Input({"base": MATCH, "type": "target-go"}, "n_clicks"),
        Input({"base": MATCH, "type": "target-left"}, "n_clicks"),
        Input({"base": MATCH, "type": "target-right"}, "n_clicks"),
        Input({"base": MATCH, "type": "target-go"}, "id"),
        State({"base": MATCH, "type": "target-step"}, "value"),
        State({"base": MATCH, "type": "target-absolute"}, "value"),
        prevent_initial_call=True,
    )
    def _move(
        target_go=None,
        target_left=None,
        target_right=None,
        target_id=None,
        target_step=0,
        target_absolute=0,
    ):
        """
        This callback reads and moves the control
        Args:
            target-go:        GO button has been clicked
            target-left:      LEFT arrow has been clicked
            target-right:     RIGHT arrow has been clicked
            target-go_id:     Motor name associated with the button
            target-step:      Value of interval movement
            target-absolute:  Value of target motor position

        Output:
            current target position
        """
        component_name = target_id["base"]
        component_ophyd = component_list.find_component(component_name)
        current_pos = component_ophyd.ophyd_obj.position
        if target_go:
            target_pos = target_absolute
        else:
            target_pos = (
                (current_pos - target_step)
                if target_left
                else (current_pos + target_step)
            )
        component_ophyd.move(target_pos)
        msg = f"Move {component_name} from {current_pos} to {target_pos}"
        return msg, None, None, None

    return
