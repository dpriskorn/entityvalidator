# Entityshape
A python library to compare a wikidata item with an entityschema

Based on https://github.com/Teester/entityshape by Mark Tully 
and https://github.com/dpriskorn/PyEntityshape by Dennis Priskorn

# Features
* compare a given wikidata item with an entityschema and dig into missing properties, too many statement, etc.
* determine whether an item is valid according to a certain schema or not

# Installation
Get it from pypi

`$ pip install pyentityshape`

# Usage
Example:
```
e = EntityShape(eid="E1", lang="en", qid="Q1")
result = e.get_result()
result.is_valid
False|True
result.required_properties_that_are_missing
{"P1", "P2"}
```

## Validation
The is_valid method on the Result object mimics all red warnings displayed by https://www.wikidata.org/wiki/User:Teester/EntityShape.js 

It currently checks these five conditions that all have to be false for the item to be valid:
1.  properties with too many statements found
2.   incorrect statements found
3.   some required properties are missing
4.   properties without enough correct statements found
5.   statements with properties that are not allowed found

# Background
This library is the glue between libraries like [Wikibase 
Integrator](https://github.com/LeMyst/WikibaseIntegrator/) and entityschemas. 

It makes it easy to batch check a whole subset of Wikidata 
items against a schema. Nice!

# TODO
The CompareShape and Shape classes should be rewritten using OOP 
and enums to avoid passing strings around because that is not 
nice to debug or maintain.

What do we want to know from the CompareShape class?

On the property level:
* whether the property is mandatory and present/missing

On the statement level
* whether the cardinality of values is allowed (min/max)
* whether the value(s) are correct/incorrect

Cases:
* mandatory property is missing
* optional property is missing (this is not invalidating)
* a property has an incorrect value
* a property has a correct value
* a property has too many values
* a property has not enough values
* ?

# ShEx Tip
When working on your Entity Schemas the constraints here are nice to know/remember
https://shex.io/shex-primer/#tripleConstraints

# Thanks
Big thanks to [Myst](https://github.com/LeMyst) and 
[Christian Clauss](https://github.com/cclauss) for 
advice and help with Ruff to make this better. 

# License
GPLv3+

# What I learned
* Forking other peoples undocumented spaghetti code is not much fun.
* Pydantic is wonderful yet again it makes working with OOP easy peasy :)
* Ruff is crazy fast and very nice!