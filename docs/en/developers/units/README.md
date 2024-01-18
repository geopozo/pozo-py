# Units
The units interface is based off package `pint`. It can be accessed w/ `pozo.units`.

## Main Functions

It exposes a pint registry `pozo.units.registry` object, and a quantity function, `pozo.units.Q()`.

`pozo.units.registry` is an enhanced pint registry:

* It has units registers specific to geology.
* It has an extra API for mapping LAS-format unit specification (CM = centimeters, for example) to pint-format, which is better since it's based off of SI.

The registry has several important custom methods:

* `add_las_map(self, mnemonic, unit, ranges, confidence="- not indicated - LOW")` will create a new las map entry. Ranges should be equal to a `LasMapEntry` object or list. Otherwise if ranges is just a string that indicates the pint unit string, it is coerced into a `LasMapEntry` object for all possible values.
* `resolve_las_unit(self, curve)` is what actually calls the mapping function to try to see if there is entry for the curve unit.
* `parse_unit_from_curve(self, curve)` which, like it's wrapper in _Utility Functions_ below, takes a curve and figures out it's pint unit. After mapping LAS->Pint, it returns a pint unit. If it can't map, it tries to use pint directly on what is written in the LAS file.

as well as some normal methods:
* `parse_units(unit)` which is part of the pint library.

`pozo.units.Q(magnitude, unit)` takes a number and a unit (a string or object) to produce a `pint.quanity` object. The individual parts can be accessed with `variable.magnitude` and `variable.unit`.

## Utility Functions
Module `pozo.units` also has utility functions:

`pozo.units.check_las(las, registry=registry)` will read a LAS file a produce information about our confidence in the units. This displays a table, if it can.

`pozo.units.parse_unit_from_curve(curve, registry=registry)` is a wrapper to a method of our enhanced `pozo.registry` object which, taking a curve and interpreting its LAS-format unit identifier into a normal standard unit.


## Registry Customizations
You can currently view all of the added units in the `units/__init__.py` as well as the map to convert a _(mnemonic, las unit, range)_ to some pint unit. For example 

`('DEPT' 'M', range=all)` is understood to be meter. 

Whereas `('NPHI', 'PU', 30)` is understood to be a porosity unit- effectively a percentage. 

`('NPHI', 'PU', .3)` is also understand to be a porosity unit, except a fraction. 
