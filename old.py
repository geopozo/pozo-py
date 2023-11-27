        
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