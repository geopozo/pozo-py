
## Ways to change the style: 
We provide helper functions that change the style of the graph in common ways in a way that places nice with pozo, plotly, and jupyter. You can also update plotly objects directly with fig.update_layout (if you know plotly and read *working directly with plotly*) but there is spooky behavior. For example, you can set { title: "Hello World" }, which will work, but it will completely override the more verbose description { title: {text: "Hello World", color: "#00FF00" } } and therefore change the text AND the color. TODO: Also, you can look at these `default_templates`, copy and paste them, and provide your own!

Here we explain more about how layout is calculated

We have a separate `layout` object defined in package `pozo.graph.layout`. Here's the concept:

So, in plotly, a data object and a layout object sit side-by-side on a figure object:
``` # TODO fix this representation
figure {
    data: data{}
    layout: layout{}
}
```
caveat: some style information, unfortunately, is stored in `data` not `layout` (e.g. colors of the lines), and any style changes we need to make that are _not_ available in the plotly API through its `layout` object (or `data` object` have to be added after the fact by embedding CSS. These two *small* carve-outs are documented *here*.


In our framework, we divide the figure (we call it graph) into 
``` # TODO fix this representation
graph { 
    tracks[
        axes[
            data[]
        ]
    ]
}
```

The graph handles positioning its tracks, which positions its axes, which range themselves and color their data.

We do our best to have the tracks and axes supply their own style. But, for example, the axes need to be absolutely positioned by the tracks through a coordinate system, and therefore the tracks need to know the height of the graph! (this unfortunate constraint could be eliminated by a careful modifcation to plotly, planned for the future). Therefore, the `graph` needs to communicate with the `tracks` (and so on) during rendering.

So first of all, we started with a dictionary of static default styling to use for our well analysis. **Insert Here**. This dictionary is attached to a Graph.Style object (when that object is initialized) which will be responsible for calculating and modifying certain elements during render time based on the object that exists. The Graph.Style must provide methods that graph, trakcs, and axes expect. You can render any object without a Style object, but at best it will be ugly and at worst illegible (since again, axes need to be positioned correctly or they just all stack up on each other).
