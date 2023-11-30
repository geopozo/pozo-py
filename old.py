        
    def render_style(self, style):
        min = None
        max = None
        for datum in self.data:
            min = datum.index[0] if min is None else min(datum.index[0], min)
            max = datum.index[-1] if max is None else max(datum.index[-1], max)
        style.set_min_max(min, max)

        mnemonic = None
        if len(self.data) == 1:
            mnemonic = self.data[0].mnemonic
        return style.get_axis(self.display_name, mnemonic=mnemonic)
    
    def render_traces(self, axis_number): 
        all_traces = []
        for datum in self.data: 
           all_traces.append(go.Scattergl(
                x=datum.values,
                y=datum.index,
                mode='lines', # nope, based on data w/ default
                line=dict(color='#000000'), # needs to be better, based on data
                xaxis='x' + str(axis_number),
                yaxis='y',
                name = datum.mnemonic, # probably needs to be better
            ))
        return all_traces


    def render_style(self, style, lower_parent):
        axes = [] # array of style dictionaries, not Axis()
        for axis_position, axis in enumerate(self.get_lower_axes()):
            axis_dict=axis.render_style(style)
            style.set_axis_veritcal_position(
                axis_dict,
                -(axis_position+1),
                lower_parent,
            ) # modifies the dict
            axes.append(axis_dict)
        for axis_position, axis in enumerate(self.get_upper_axes()):
            axis_dict=axis.render_style(style)
            style.set_axis_vertical_position(
                axis_dict,
                axis_position+1,
                lower_parent+self.count_lower_axes(),
            ) # modifies the dict
            axes.append(axis_dict)
        return axes