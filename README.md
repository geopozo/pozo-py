# Pozo

Pozo is an open source, intuitive api for graphing well logs. It accepts las objects from [lasio](https://github.com/kinverarity1/lasio).

This week, styling, defaults, and spanish documentation will be published.

## Español

Pozo es una API intuitiva, y de codigo abierto, para visualizar registros de pozos. Se acepta objetos de LAS de [lasio](https://github.com/kinverarity1/lasio).

Esta semana, se publicará estilo, defectos, y más documentación!

## Example/Ejemplo

```python
from pozo.graphs import Graphs
import lasio
las = lasio.read("/your/las/file/here") 
Graph(las).render()
```
