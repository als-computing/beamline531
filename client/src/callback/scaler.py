from dash.dependencies import Input, Output
import plotly.express as px


def plot_scaler(app, component_list, max_scaler_length=1800):
    @app.callback(
        Output("scalerPlot", "figure"),
        Output("livescaler-cache", "data"),
        Input("refresh-interval", "n_intervals"),
        Input("livescaler-cache", "data"),
        Input("scaler-x", "value"),
        Input("scaler-y", "value"),
    )
    def _plot(refresh_interval, data, x_component, y_component):
        """
        This callback reads and plot the selected scaler
        Args:
            refresh_interval:   Time interval between updates
            data:               Data stored in cache
            x_component:        Selected component to plot on x-axis
            y_component:        Selected component to plot on y-axis
            init:               Boolean variable for initializing cache data

        Output:
            px.Scatter, updated scattered figure
            dcc.Store,  update the store in cache
        """
        # print(refresh_interval, data, x_component, y_component)

        xobj = (
            x_component
            if x_component == "Time"
            else component_list.find_component(x_component)
        )
        yobj = (
            y_component
            if y_component == "Time"
            else component_list.find_component(y_component)
        )

        if (xobj is None) | (yobj is None):
            return px.scatter(), None

        xval = [refresh_interval if x_component == "Time" else xobj.position]
        yval = [refresh_interval if y_component == "Time" else yobj.position]
        xunit = "sec" if x_component == "Time" else xobj.unit
        yunit = "sec" if y_component == "Time" else yobj.unit

        if data is None:
            data = {}
            for l in ["xval", "yval", "xunit", "yunit", "x_component", "y_component"]:
                data.update({l: eval(l)})
        elif all(
            [x_component == data["x_component"], y_component == data["y_component"]]
        ):
            if len(data["xval"]) < max_scaler_length:
                xval = data["xval"] + xval
                yval = data["yval"] + yval
            else:
                xval = data["xval"][1:] + xval
                yval = data["yval"][1:] + yval
            data.update({"xval": xval})
            data.update({"yval": yval})
        else:
            data = None
            print("data initilization")
            return px.scatter(), None

        fig = px.scatter(x=data["xval"], y=data["yval"])
        fig.update_layout(
            xaxis_title="%s (%s)" % (x_component, data["xunit"]),
            yaxis_title="%s (%s)" % (y_component, data["yunit"]),
        )

        return fig, data

    return
