
# yx
Sly based interpreted language.

### main.yx

comments
```
#> comment;
// comment;
```

ops
```
+ | plus
- | minus
/ | divide
! | mod
^ | power
```

function
```
functionname("") > {~
	#>code_goes_here$
	#>more_code$
~};

function_with_return("") > {~
	returne=3$
~};

function_with_return("") > var_name;
var_name; #> 3;

function_with_args("string>n") > {~
	returne=2^n
~};
function_with_args("n=3") > x;
x; #> 8;
```

conditionals
```
x = 1;
if (x) {%
	print "True"&
	x = 0
%};

if (x) {%
	print "This code cannot be reached"
%} else {
	x = 3
}

x; #> 3;
```

example program
```
asknum("") > {~
  uinp("Pick a number!") > returne$
~};

func("") > {~
	uinp("Choose a mode! (+, -, *, /, ^, !)") > returne$
~};

k = 3;
z = 1;
while (z){~

  func("") > type$
  asknum("") > n1$
  asknum("") > n2$

  v1 = type == "+"$
  v2 = type == "-"$
  v3 = type == "/"$
  v4 = type == "*"$
  v5 = type == "^"$
  v6 = type == "!"$
  
  n1 = to_int(n1)$
  n2 = to_int(n2)$

  if (v1){%
    res = n1 + n2&
  %}else{%%}$

  if (v2){%
    res = n1 - n2&
  %}else{%%}$

  if (v3){%
    res = n1 / n2&
  %}else{%%}$

  if (v4){%
    res = n1 * n2&
  %}else{%%}$

  if (v5){%
    res = n1 ^ n2&
  %}else{%%}$

  if (v6){%
    res = n1 ! n2&
  %}else{%%}$

  empty = ""$
  sempty = " "$
  se_empty = " = "$
  k = k-1$
  z = k > 0$
  to_print = empty + n1 + sempty + type + sempty + n2 + se_empty + res$
  print to_print$
~};
```

output
```
"Choose a mode! (+, -, *, /, ^, !)": *
"Pick a number!": 3
"Pick a number!": 6
"3 * 6 = 18"
"Choose a mode! (+, -, *, /, ^, !)":
... 
```

os
```
cfile("filename"); // CFILE LPAREN STRING RPAREN;
rfile("filename") > var; // RFILE LPAREN STRING RPAREN > NAME;
xfile("filename"); // XFILE LPAREN STRING RPAREN;
wfile("filename", "data"); // WFILE LPAREN STRING "," STRING RPAREN;
```

imports
```
import file; #> imports file.yx;
```

exec
```
x = exec(~returne=3~); #> x = 3, note execution function will excecute code in python;
```