# toc
A python package for doing theory-of-computation related stuff. 

This is a work in progress, and far from complete. Comments, requests, suggestions for improvement are all welcome. Feel free to submit an issue.

Note that the terminology used in this package (and many of the test examples) follow the lead of Michael Sipser's excellent *Introduction to the Theory of Computation*.

There are thus far two sub-packages: `fsa` and `cfg`...

##fsa
A package for dealing with finite-state automata, and their ilk. There are three classes you import with the fsa sub-package:

###DFA
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

* `+`: Let A be the language recognised by dfa1, B be the language recognised by dfa2. `dfa1 + dfa2` returns a DFA that recognises the set of all concatenations of strings in A with strings in B. This DFA operator is parasitic on the NFA operator; it converts the input DFAs into NFAs, uses the NFA '+', then converts the result back to a DFA. That makes for a relatively simple but, sadly, computationally expensive algorith. For that reason, I recommend you don't `+` dfas with large numbers of states.

#### Methods

* `accepts`: `my_dfa.accepts("some string")` returns `True` if my_dfa accepts "some string", and `False` otherwise. Will raise a ValueError exception is the string contains symbols that aren't in the DFA's alphabet.

* `encode`: Let A be the language accepted by dfa. `dfa.encode()` returns a regex string that generates A. That regex string is liable to be much more complicated than necessary; maybe I'll figure out how to improve on average simplicity, eventually. Note that the regex language I use is much simpler than the standard python regex language (though it is technically equivalent in expressive power). See here.

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
  1. `transition_function`, the transition function of the nfa specified as a dictionary. Equal to the dictionary you passed in on instantiation, if that's how the nfa instance was created;
  2. `states`, the set of states of the nfa. Inferred from the transition-function parameter on instantiation, if that's how the nfa instance was created;
  3. `alphabet`, the set of symbols that appear in the language of the nfa. Inferred from the transition-function on instantion, if that's how the nfa instance was created;
  4. `start_state`, the start state of the nfa. Equal to the start-start parameter you passed in on instantiation, if that's how the dfa instance was created;
  5. `accept_states`, the set of the nfa's accept-states. Equal to the accept_state parameter you passed in on instantiation, it that's how the dfa instance was created.

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

For reaons related to the above, the characters '(', ')', '|', '*', '•', '€' and 'Ø' cannot be symbols in the alphabet of the NFA. (My apologies to speakers of Scandinavian languages for the last one; I am very against English chauvinism, but your letter is so very close to the empty-set symbol. If, by some miracle, there is someone who cares about this, I will change the symbol for empty-set.)

In the absence of parentheses, the order of operations is: `*`, then `•`, then `|`.

I realise the simplicity of the regex language is lame; some day it might be better.

The method uses a version of Dijkstra's shunting yard algorithm to parse the regex and build the NFA.

The method will raise a ValueError exception if any of the following conditions hold:
  * the alphabet contains any of the verboten characters -- i.e.,`(`, `)`, `|`, `*`, `•`, `€` and `Ø`,
  * the input regex string contains a character not in the alphabet, and not one of the above veboten characters,
  * the input regex contain a binary operator followed by an operator, or
  * the input regex does not have properly matching parentheses.
