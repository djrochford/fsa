# toc
A python package for doing theory-of-computation related stuff. 

This is a work in progress. Comments, requests, suggestions for improvement are all welcome. Feel free to submit an issue.

Note that the terminology used in this package (and many of the test examples) follow the lead of Michael Sipser's excellent *Introduction to the Theory of Computation*.

There are thus far two sub-packages: [fsa](#fsa) and [cfg](#cfg)...

## fsa
A package for dealing with finite-state automata, and their ilk. There are three classes you import with the fsa sub-package:

### DFA
A deterministic finite automaton class. Takes three parameters: a transition function, a start state and a set of accept states, in that order.

The transition function should be specified as a dictionary with tuple keys. These keys implicitly define the dfa's state-set and alphabet; the first elements of the tuples represent the fsa's states, and the second elements are the symbols in the alphabet.

The dfa expects the symbols of the alphabet to be one character strings. States can be anything hashable. (Note that, for reasons of hashability, you'll need to use frozensets, rather than sets, if you want to have sets as states.)

The class will raise a ValueError exception on instantiation if any of the following are true:
  * the start state is not a member of the set of states inferred from the transition function;
  * the set of accept states is not a subset of the set of states inferred from the transition function;
  * the range of the transition function is not a subset of the set of states inferred from the transition function;
  * a member of the alphabet inferred from the transition function is not a one-character string;
  * the transition function is missing a case -- i.e., it is not the case that every pair of a state and a symbol is in the domain of the transition function.
The exception message will specify which of these above conditions things triggered the exception, and which states/symbols are the source of the problem.

#### Properties
A DFA instance has the following properties:
  1. `transition_function`, the transition function of the dfa specified as a dictionary. Equal to the dictionary you passed in on instantiation, if that's how the dfa instance was created;
  2. `states`, the set of states of the dfa. Inferred from the transition-function parameter on instantiation, if that's how the dfa instance was created;
  3. `alphabet`, the set of symbols that appear in the language of the dfa. Inferred from the transition-function on instantiona, if that's how the dfa instance was created;
  4. `start_state`, the start state of the dfa. Equal to the start-start parameter you passed in on instantiation, if that's how the dfa instance was created;
  5. `accept_states`, the set of the dfa's accept-states. Equal to the accept_state parameter you passed in on instantiation, it that's how the dfa instance was created.

Each of the above are accessible using a `get` method, of the form `get_[PROPERTY]`. For example `my_dfa.get_transition_function()` returns a copy of my_dfa's transition function.

#### Operators

* `|`: Let A be the language recognised by dfa1, and B be the language recognized by dfa2. `dfa1 | dfa2` returns a dfa that recognizes A union B. The states of dfa1 | dfa2 are ordered pairs of states from dfa1 and dfa2. There is no problem with the input DFAs having different alphabets.

* `+`: Let A be the language recognised by dfa1, B be the language recognised by dfa2. `dfa1 + dfa2` returns a DFA that recognises the set of all concatenations of strings in A with strings in B. This DFA operator is parasitic on the [NFA](#NFA) operator; it converts the input DFAs into NFAs, uses the NFA '+', then converts the result back to a DFA. That makes for a relatively simple but, sadly, computationally expensive algorith. For that reason, I recommend you don't `+` dfas with large numbers of states.

#### Methods

* `accepts`: `my_dfa.accepts("some string")` returns `True` if my_dfa accepts "some string", and `False` otherwise. Will raise a ValueError exception is the string contains symbols that aren't in the DFA's alphabet.

* `encode`: Let A be the language accepted by dfa. `dfa.encode()` returns a regex string that generates A. That regex string is liable to be much more complicated than necessary; maybe I'll figure out how to improve on average simplicity, eventually. Note that the regex language I use is much simpler than the standard python regex language (though it is technically equivalent in expressive power). See the `fit` method in the [NFA](#NFA) section for more details.

* `non_determinize`: Convenience method that takes a DFA instance and returns an equivalent NFA instance.

### NFA
A nondeterministic finite automaton class. Takes three parameters: a transition function, a start state and a set of accept states, in that order.

The transition function should be specified as a dictionary with tuple keys. These keys implicitly define the nfa's state-set and alphabet; the first elements of the tuples represent the nfa's states, and the second elements are the symbols in the alphabet.

The nfa expects the symbols of the alphabet to be one character strings. States can be anything hashable. (Note that, for reasons of hashability, you'll need to use frozensets, rather than sets, if you want to have sets as states.)

The domain of the transition function is the power-set of the nfa's state set --- i.e., the values of the transition function dictionary should be sets (or frozensets). The empty set is a valid value; in fact, you are required to specify that the successor set for a given state-symbol pair is the empty set, if it is.

You can define epsilon-moves by using the empty string in place of an alphabet symbol in the transition function. Note that the empty string will not be inferred to be a member of the alphabet (and hence the checks below will work as you would expect).

The class will raise a ValueError exception on instantiation if any of the following are true:
  * the start state is not a member of the set of states inferred from the transition function;
  * the set of accept states is not a subset of the set of states inferred from the transition function;
  * a member of the alphabet inferred from the transition function is not a one-character string;
  * a member of the transition function's range is not a set;
  * the range of the transition function is not a subset of the power set of states inferred from the transition function;
  * the transition function is missing cases -- i.e., it is not the case that every pair of a state and a symbol is in the domain of the transition function.
The exception message will specify which of these six conditions things triggered the exception, and which states/symbols are the source of the problem.

#### Properties
An NFA instance has the following properties:
  1. `transition_function`, the transition function of the NFA specified as a dictionary. Equal to the dictionary you passed in on instantiation, if that's how the NFA instance was created;
  2. `states`, the set of states of the NFA. Inferred from the transition-function parameter on instantiation, if that's how the NFA instance was created;
  3. `alphabet`, the set of symbols that appear in the language of the NFA. Inferred from the transition-function on instantion, if that's how the nfa instance was created;
  4. `start_state`, the start state of the NFA. Equal to the start-start parameter you passed in on instantiation, if that's how the NFA instance was created;
  5. `accept_states`, the set of the nfa's accept-states. Equal to the accept_state parameter you passed in on instantiation, it that's how the NFA instance was created.

Each of the above are accessible using a `get` method, of the form `get_[PROPERTY]`. For example `my_nfa.get_transition_function()` returns a copy of my_nfa's transition function.

#### Operators

* `|`: Let A be the language recognised by nfa1, and B be the language recognized by nfa2. `nfa1 | nfa2` returns an nfa that recognizes A union B. The cardinality of the state-set of nfa1 | nfa2 is the cardinality of the state set of nfa1 plus the cardinality of the state-set of nfa2 plus 1. There is no problem with the input NFAs having different alphabets.

* `+`: Let A be the language recognised by nfa1, and B be the language recognized by nfa2. `nfa1 + nfa2` returns an nfa that recognizes A concat B -- i.e., the language consisten of the set of strins of the form ab, where a is an element of A and b is an element of B. Note that this `+` operation is not commutative.

#### Methods

* `accepts`: `my_nfa.accepts("some string")` returns `True` if my_nfa accepts "some string", and `False` otherwise. Will raise a ValueError exception is the string contains symbols that aren't in the NFA's alphabet.

* `determinize`: Returns a DFA that recognizes the same language as the NFA instance. WARNING: The set of DFA states is the power-set of the set of NFA states. For related reasons, the time complexity of this method is exponential in the number of states of the NFA. Don't determinize big NFAs.

* `star`: Let A be the language recognised by nfa. `nfa.star()` returns an NFA that recognizes A* --i.e., the set of all strings formed by concatenating any number of members of A. You should really think of this as a unary operator, rather than a method; I'd write it as such if I knew how to make the syntax work.

There is also one **static method**:

* `fit`: Takes a regular expression and an alphabet (i.e., a set of one-character strings) as input, in that order; returns an NFA that recognises the language defined by that regular expression and that alphabet.

The alphabet parameter is optional; it's default value is `string.printable` -- i.e., the set of "printable" characters, which includes the standard ASCII letters and digits, and most common punctuation and white space.

Actually, that's not quite right -- the default value is `string.printable` *minus* parentheses, the vertical bar and the star symbol, for reasons that I will explain presently.

As of now, the syntax of the regular expressions that this method takes as input is very simple -- much simpler than the standard python regular expresssions. All characters are intepreted as literals for symbols in the alphabet except for `(`, `)`,`|`, `*`, `•`, `€` and `Ø`. 

The parentheses, vertical bar and star mean what you'd expect them to mean if you are familiar with regular expressions as taught in computer science classes. 

'•' (option-8 on a mac keyboard) means concatenation. You can leave concatentation implicit, as is usual; no need to write '•'' explicitly if you don't want to. But it gets used internally. 

'€' (option-shift-2) is used to match the empty string (because it kind of looks like an epsilon); there's no other way to match, for instance, {'', '0'} with the current syntax. (Quick challenge: it's not totally obvious how to match the empty string in normal python regex either, although it can be done; give it a go.) 

'Ø' (option-shift-o) represents the empty set; you can match to the empty language with it.

For reasons related to the above, the characters '(', ')', '|', '\*', '•', '€' and 'Ø' cannot be symbols in the alphabet of the NFA. (My apologies to speakers of Scandinavian languages for the last one; I am very against English chauvinism, but your letter is so very close to the empty-set symbol. If, by some miracle, there is someone who cares about this, I will change the symbol for empty-set.)

In the absence of parentheses, the order of operations is: `*`, then `•`, then `|`.

I realise the simplicity of the regex language is lame; some day it might be better.

The method uses a version of Dijkstra's shunting yard algorithm to parse the regex and build the NFA.

The method will raise a ValueError exception if any of the following conditions hold:
  * the alphabet contains any of the verboten characters -- i.e.,`(`, `)`, `|`, `*`, `•`, `€` and `Ø`,
  * the input regex string contains a character not in the alphabet, and not one of the above veboten characters,
  * the input regex contain a binary operator followed by an operator, or
  * the input regex does not have properly matching parentheses.

### FST
A finite-state transducer class. Takes two parameters: a transition function, and a start state, in that order.

The transition function should be specified as a dictionary with tuple keys and values. These keys implicitly define the fst's state-set and input alphabet; the first elements of the tuples represent the fst's states, and the second elements are the symbols in the alphabet.

Similarly, the values should be tuples with the first element a state, the second member a symbol in the output alphabet, and the output alphabet (though not the state set) is implicitly defined by these values.

The fst expects the symbols of both alphabets to be one character strings. States can be anything hashable. (Note that, for reasons of hashability, you'll need to use frozensets, rather than sets, if you want to have sets as states.)

The class will raise a ValueError exception on instantiation if any of the following are true:
 * the start state is not a member of the set of states inferred from the transition function;
 * a member of the input alphabet inferred from the transition function is not a one-character string;
 * a member of the output alphabet inferred from the transition function is not a one-character string;
 * the states in the range of the transition function are not members of the state-set inferred from the domain of the transition function;
 * the transition function is missing cases -- i.e., it is not the case that every pair of a state and a symbol in the input alphabet is in the domain of the transition function.
The exception message will specify which of these five conditions things triggered the exception, and which states/symbols are the source of the problem.

#### Properties
An FST instance has the following properties:
 1. `transition_function`: the FST's transition function, specified as a dictionary. Equal to the dictionary you passed in on instantiation.
 2. `states`: the set of the FST's states. Inferred from the FST's transition_function on instantiation.
 3. `start_state`: the FST's start state. Equal to the parameter you passed in on instantiation.
 4. `input_alphabet`: the alphabet of the language the FST accepts as input. Inferred from the transition function on instantiation.
 5. `output_alphabet`: the alphabet of the language the FST outputs. Inferred from the transition function on instantiation.
Each of the above are accessible using a `get` method, of the form `get_[PROPERTY]`. For example `my_fst.get_transition_function()` returns a copy of my_fst's transition function.

#### Mehods

 * `process`: Takes a string as input, and returns a string as output. Specifically, it returns the string that the given FST returns, when given the first string as input.

## cfg

A package for dealing with context-free grammars. Currently contains just the one class:

### CFG
A context-free grammar class. Takes two parameters: the grammar's rules, and the start variable, in that order.

The rules should be specified as a dictionary with string keys and set (or frozenset) values. Each member of the set is a possible substitution for that variable; the substitutions should also be strings.

The variables and terminals of the grammar are inferred from the rule dictionary. All keys are assumed to be variables of the grammar; everything that appears in a substitution that isn't a variable is assumed to be a terminal.

You can specify empty substitutions using '€' (opt-shift-2, on a mac). That symbol the closest thing to an epsilon you can access easily from the keyboard.

The class will raise a ValueError exception on instantiation if any of the following are true:
 * the first (rule) parameter is not a dictionary;
 * the rule dictionary contains a non-string key;
 * the rule dictionary contains a value that is neither a set nor a frozenset;
 * one of the set-values of the rule dictionary has a non-string member;
 * there are no terminals among the possible susbtitutions;
 * the start-variable parameter is not one of the variables inferred from the rule dictionary.
The exception message will specify which of the above conditions triggered the exception, and which variables/terminals were the source of the problem.

#### Properties
 * `rules`: the rules of the CFG, specified as a dictionary. Equal to the rules parameter you passed in on instantiation, if that's how the CFG instance was created.
 * `variables`: the variables of the CFG. These are inferred from the rules parameter on instantiation, if that's how the CFG instance was created.
 * `terminals`: the terminals of the CFG -- i.e., strings in the language that the CFG generates. Inferred from the rules parameter on instantiation, if that's how the CFG instance was created.
 * `start_variable`: the start variable of the CFG. Equal to the start-variable parameter you passed in on instantiation, if thats how the CFG instance was created.
Each of the above are accessible using a `get` method, of the form `get_[PROPERTY]`. For example `my_cfg.get_rules()` returns a copy of my_cfg's rules.

#### Methods

* `chomsky_normalize`: Let cfg be a context-free grammar that generates language L. `cfg.chomky_normalize()` returns a new CFG instance that also generates L, but is in Chomsky Normal Form -- i.e., all possible substitutions of variables are either single terminals or a pair of variables (no empty substitutions). 

The resulting grammar is liable to much more complicated than the minimally-complicated, Chomsky-normalized grammar that generates L. Maybe some day I'll add some stuff to simplify the result.
