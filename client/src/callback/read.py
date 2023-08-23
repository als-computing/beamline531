from dash.dependencies import Input, Output, ALL


def read_callback(app, component_list):
    @app.callback(
        Output({"base": ALL, "type": "current-pos"}, "children"),
        Input("refresh-interval", "n_intervals"),
    )
    def _update(refresh_interval):
        """
        This callback reads and updates the position of all the components
        Args:
            refresh_interval:   Time interval between updates

        Output:
            current reading of all the components
        """
        comp_list = component_list.comp_list

        # Update component status
        for c in comp_list:
            c.update_status()

        response_list = []
        # Get current position - temporaty patch
        for c in comp_list:
            try:
                position = c.position
                unit = c.unit
                msg = "%.5f %s" % (position, unit)
                response_list.append(msg) #= ["%.5f %s" % (c.position, c.unit) for c in comp_list]
            except:
                response_list
            
        return response_list
