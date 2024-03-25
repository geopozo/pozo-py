# 🐰 Pozo: Visualizador de... pozos!

Pozo es una API intuitiva, de código abierto, para visualizar registros de pozos. Se usa [plotly](https://github.com/plotly/plotly.py) para renderizar gráficos interactivos.

```bash
$ pip install pozo
```

Si usas lasio recuerda `pip install lasio`. Si usas jupyter entonces `pip install ipywidgets nbformat`.

## Glosario de palabras claves

```
- Track               --> Vía
- Axis (plural: Axes) --> Eje
- Pop                 --> Quitar (más como echar)
- Fallback            --> Respaldo
```

## Uso Sencillo

```python
import pozo
import lasio
las = lasio.read("SALADIN.LAS")

# Se puede indicar los datos relevantes
myGraph = pozo.Graph(las, include=["CALI", "CGR", "LLS", "ILD", "LLD", "NPH", "RHOB"])

# Cangrejo es un buen tema predeterminado para empezar!
myGraph.set_theme("cangrejo") # recomendado!

myGraph.render(height=800, depth=[1080, 1180])

```
<p align="center"><img src="../images/log_example2.png" /> </p>

<br />

Se nota que las vías están ordenadas como la lista `include=[...]`.

**Ya hay una función nueva: [saber de crossplots](docs/es/usuarios/CROSSPLOTS.md)**

### Combinar Vías
```
# Antes de renderizar

graph1.combine_tracks("CGR", "CALI") # También se preserva el orden!

graph1.combine_tracks("LLD","ILD","LLS") 

graph1.combine_tracks("RHOB", "NPHI")

# Podemos cambiar la posición del eje de la profunidad con `depth_position=1`
graph1.render(height=800, depth_position=1, depth=[1080, 1180])
```
<p align="center"><img src="../images/log_example.png" /> </p>

Un `pozo.Graph` se construye por un `pozo.Track`, que contiene `pozo.Axes`, que tiene `pozo.Data`.

#### Temas

```
# Unas configuraciones:
#  "color": "blue"
#  "scale": "log"
#  "range": [0, 10]
#  "range_unit": "meter"
```

Temas pegadas en cosas mas especificas tienen prioridad. Es decir, un tema por un `Axis` se da antes de un tema por un `Track`. Si no hay clave pertinente en el `Axis`, se busca los otros objetos en la jerarquía.

El tema `"cangrejo"` está incluido en pozo. Se emplea el `mnemonic` de los datos para determinar el color, rango, and unidad. Pero este no nos entrega toda la información, así que hay dos opciones:

*Se nota: Temas por un `Trace` solo funcionan con ciertas claves.*

```
# Una: Poner un respaldo para todos (solo funciona con "cangrejo")
graph.get_theme().set_fallback{"track_width":200}

# Dos: Poner un tema especifica para la vía.
graph.get_tracks("CGR")[0].set_theme({"track_width":200})
```

[saber más de los temas](docs/es/users/THEMING.md)

#### Seleccionar Vías

```
# Devuelven una lista de objetos tipo Track
tracks         = graph1.get_tracks("CGR", "MDP") # por nombre
other_tracks   = graph1.get_tracks(0, 2)         # por posición

# Quitan Y devuelven una lista de objetos tipo Track
popped_tracks  = graph1.pop_tracks("CGR", 3)     # por nombre o posición

# Nota: El `name` suele ser el `mnemonic`. Pero no siempre, como con vías compuestas.
# Para buscar por `mnemonic`:
popped_tracks2 = graph1.pop_tracks(pozo.HasLog("CGR")) # pozo.HasLog( "MNEMONIC" )
```

## Agregar Data a mano

#### A veces se quiere hacer cálculos y construir nuevos datos:

```
data = [1, 2, 3]
depth = [1010, 1020, 1030]

# todo Data requiere o un `mnemonic` o un `name`
new_data=Data(data, depth=depth, mnemonic="LOL!")
graph.add_tracks(new_data)
# Renderizalo....

```
Ya se puede llamar `graph.add_tracks(new_data)`

Pero si se quiere un tema primero. Un objeto tipo `Data` no va bien con temas (solo se cambia el color de la linea):

```
new_tracks = graph.add_tracks(new_data)
new_tracks[0].set_theme({"color":"red", range=[0, 1], range_unit="fraction"})
graph.add_tracks(new_track)
# Renderizalo....
```

[saber más de los internos](docs/es/users/INTERNOS.md)

## Depurar los Datos

### Unidades

`pozo.units.check_las(las_object)` es una funcion que te ayuda verificar los datos y las unidades en un LAS. Crea un tabla de las unidades en forma las y la confianza de la interpretación.