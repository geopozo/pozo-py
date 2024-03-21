# Qué es Pozo?

## El árbol
Si se tiene un graph `Graph`:
```
import pozo
myGraph = pozo.Graph()
```

Se tiene esto:

<p align=center><img src=../../images/internal/1.png /></p>


Y si se llama `myGraph.render()`... no se recibe nada porque todavía no hay datos.

Antes de agregar los datos, agreguemos unos `Track`:

```
myGraph.add_tracks(
	pozo.Track(name="track1"),
	pozo.Track(name="track2")
)
```

No tienen datos, pero la estructura interna es así:

<p align=center><img src=../../images/internal/2.png /></p>

Si hacemos `myGraph.render()` aún no hace nada, debemos agregar unos datos:

```
x = [2, 2, 1, 4, 5, 6]
y = [1, 2, 3, 4, 5, 6]

new_data = pozo.Data(x, depth=y, mnemonic="test")

# Y donde se pone ese Data:

track1 = myGraph.get_tracks("track1")[0] # siempre se devuelve una lista!
track1.add_axes(new_data)
```

Listo:

<p align=center><img src=../../images/internal/3.png /></p>

ESPERA! De donde se saca el `Axis`?

#### Creación Automatica de Pozo

Un `pozo.Data` está **contenido SIEMPRE** por un `pozo.Axis`, a su vez este está **contenido SIEMPRE** por un `pozo.Track`, que está **contenido SIEMPRE!** por un `pozo.Graph`.

Si se agrega algo más bajo en la jerarquía a algo más alto, los intermedios se crearán automaticamente: Si se agrega un`Axis` a un `Graph`, se crea un `Track` entre los dos. Si se agrega un `Data` a un `Graph`, se crea un `Axis` y u `Track`...

_O se hace todo a mano:_

```
aGraph = pozo.Graph()
aTrack = pozo.Track()
anAxis = pozo.Axis()
aData = pozo.Data()

aGraph.add_tracks(aTrack)
aTrack.add_axes(aAxis)
anAxis.add_data(aData)
```
### Renderizar
A ver, hagamos un `myGraph.render()`, y recibimos:

<p align=center><img src=../../images/internal/simple_pozo.png /></p>

Muy bien.

### Ficha de Referencia

## `Graph()`


### Crear:

`newGraph = pozo.Graph()` se toman objetos de pozo o un archivo tipo LAS como argumentos, y se crea un `Track` por cada una. También se toman los siguientes argumentos opcionales (para usar durante renderización):
* `show_depth`: True/False
* `depth_position`: 0, 1, 2, 3, 4
* `depth`: [minimo, maximo]
* `height`: altura en puntos

### Manipular:


`someGraph.get_tracks()`: Se toman `selector`: un nombre o un indice, y se devuelven los `Track` con ese nombre o a ese indice, si lo hay
	
`someGraph.pop_tracks()`: Se toman `selector`, y se devuelen los `Track`, pero también los quita del `someGraph` 

`someGraph.add_tracks()`: Se toman `pozo.Data`, `pozo.Axis`, o `pozo.Track`, se agregan al `Graph`, y se devuelvan los `Track` nuevos

`someGraph.combine_tracks()`: Se toman `selector` o `pozo.Track`, se destruyen, y se agregan todos al primer `selector` puesto (el que no es destruído) 

`someGraph.move_tracks()`: Se toman `selectors` y `position=?` para poner en el orden nuevo


### Mostrar:

`someGraph.render()`: Se intenta mostrar el gráfico. Se toman las mismas opciones extra de `pozo.Graph()`

### Especiales:

`someGraph.get_axes()` y `someGraph.get_data()` también funcionan.

## `Track()`

### Crear:

`newTrack = pozo.Track()` se toman objetos de pozo y `name=?`

### Manipular:

`someTrack.set_name()`: Se toma un nombre nuevo

`someTrack.get_name()`: Se devuelve el nombre actual

`someTrack.add_axes()`: Se toman objetos de pozo y se devuelven

`someTrack.get_axes()`: Se toman `selector` y se devuelven los `Axis` si se existen

`someTrack.get_...` bla bla bla, El patron sigue, es parecido a  `Graph()`. `Axis()`, también. `Data()` es distinto...

## `Axis()`

Lo mismo.

## `Data()`

### Crear:

`myData = pozo.Data(data, depth=algo, mnemonic="algo")`: Estos tres son requeridos. Se pueden poner `unit=` y `depth_unit=` también.

### Manipular:

`someData.get_mnemonic()`: Se devuelve la mnemotécnica.

`someData.set_mnemonic()`: Se toma una mnemotécnica nueva.

`someData.get_data()`: Se devuelven los datos.

`someData.set_data()`: Se toma una lista de datos, pero también se acepta "depth=" y "unit=" y "depth_unit="

`someData.get_depth()`: Se devuelven los datos de profunidad.

`someData.set_depth()`: Se toma una lista de datos de profunidad.

`someData.get_unit()`: Se devuelven las unidades de los datos.

`someData.set_unit()`: Se toman las unidades de los datos.

`someData.get_depth_unit()`: Se devuelvan las unidades de la profunidad.

`someData.set_depth_unit()`: Se toman las unidades de la profunidad.

`someData.convert_unit()`: Se toma una unidad nueva, y se puede entender, se hace la conversión.

`someData.convert_depth_unit()` Se toman una unidad nueva, y se puede entender, se hace la conversión.


## Selectores Especiales

Normalmente, un selector es un número (posición) o nombre. Hay unos especiales:

* un objeto de Pozo (`Track`, etc) tambien funcionan y encuentran sus mismos.
```
track1 = pozo.Track()
track2 = pozo.Track()
graph1.add_tracks(track1)
len(graph1.get_tracks(track1, track2)) == 1
```
* `pozo.HasLog("MNEMOTÉCNICA")` buscará cada dato, para ver si la cosa que buscas tiene esa "MNEMOTÉCNICA"
