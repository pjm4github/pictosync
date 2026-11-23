
There are these types of annottated states <<start>>, <<choice>>, <<fork>>, <<join>>, <<end>>, <<history>> and <<history*>>.  
In addition there are [*]-> (an exiting transition is not part of the definition) which represents a start state and an end state ->[*]. 
Additionaly, there is an <<entryPoint>> an <<exitPoint>> an <<inputPin>> an <<exitPin>> an <<expansionInput>> and an <<expansionOutput>> decorator types. 
The shape that should be used for all of these special states should use the table below to create the correct shape. For annotating the diagram. 
The text associated with the SVG and the state should not be rendered in teh annotation json data.

SPECIAL STATE		|  SHAPE TO USE (this should be parsed from the SVG where possible)
--------------------+------------------------------------------------------------------
<<start>>			|  an ellipse with black solid fill
<<choice>>			|  a diamond (polygon)
<<fork>>			|  a horizontal bar (rectangle) with dark gray fill
<<join>>			|  a horizontal bar (rectangle) with dark gray fill
<<end>>				|  an ellipse with white fill and thick back edge color
<<sdlreceive>>		|  this should be an ALT sequence block
<<history>>			|  an ellipse with white fill and thin black line with the letter H inside
<<history*>>		|  an ellipse with white fill and thin black line with the letter H* inside
<<inputPin>>		|  a square (rectangle) with white fill and a thin black line
<<outputPin>>		|  a square (rectangle) with white fill and a thin black line
<<expansionInput>>	|  a set of 4 squares (grouped) side by side with white fill and a black border
<<expansionOutput>>	|  a set of 4 squares (grouped) side by side with white fill and a black border
<<entryPoint>>		|  an ellipse with white fill and a thin black border
<<exitPoint>>		|  an ellipse with white fill and a thin black border with the X inside
[*]->				|  this is the same as the <<start>> SPECIAL SHAPE
->[*]				|  this is the same as the <<end>> SPECIAL SHAPE

