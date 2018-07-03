let rec belongsTo a b = match b with
	| hd :: tl -> if a = hd then true else belongsTo a tl
	| [] -> false


let rec subset a b = match a with
	| hd :: tl -> (belongsTo hd b) && (subset tl b)
	| [] -> true


let equal_sets a b = (subset a b) && (subset b a)


let rec set_union a b = match a with
	| hd :: tl -> if (belongsTo hd b) then (set_union tl b) else (set_union tl (hd::b))
	| [] -> b


let rec set_intersection a b = match a with
	| hd :: tl -> if (belongsTo hd b) then hd::(set_intersection tl b) else (set_intersection tl b)
	| []->[]


let rec set_diff a b = match a with
	| hd :: tl -> if (belongsTo hd b) then (set_diff tl b) else (hd::set_diff tl b)
	| []->[]

let rec computed_fixed_point eq f x = 
	if (eq x (f x)) then x else (computed_fixed_point eq f (f x))


let rec period f p x = if (p = 0) then x else (period f (p-1) (f x))
let rec computed_periodic_point eq f p x =
	if (eq (period f p x) x) then x else computed_periodic_point eq f p (f x)


let rec while_away s p x = if (p x) then x::(while_away s p (s x)) else []


let rec addList (n , x) l = if (n = 0) then l else x::(addList (n-1,x) l)
let rec rle_decode lp = match lp with
	| []-> []
	| hd :: tl -> (addList hd (rle_decode tl))

type ('nonterminal, 'terminal) symbol =
  | N of 'nonterminal
  | T of 'terminal

let getFirst (a,b) = a
let getSecond (a,b) = b

let isTerminal = function 
	| N _ -> false
	| T _ -> true

let rec allTerminal l = match l with
	| [] -> true
	| hd :: tl -> if (isTerminal hd) then (allTerminal tl) else false

let rec findT l = match l with
	| [] -> []
	| (a,b) :: tl -> if (allTerminal b) then a::(findT tl) else findT tl

let rec getRidOfSym l = match l with
	| [] -> []
	| (N a) :: tl -> a :: getRidOfSym tl
	| (T a) :: tl -> getRidOfSym tl

let rec listGoodN l list_of_GoodN =
	match l with
		| [] -> list_of_GoodN
		| (non,list_of_sym) :: tl -> if (subset (getRidOfSym list_of_sym) list_of_GoodN)
					  then (non) :: (listGoodN tl (list_of_GoodN))
					  else listGoodN tl list_of_GoodN


let rec filter_work list_of_Rules list_of_GoodN =
	match list_of_Rules with
		| [] -> []
		| (non,syms_list) :: tl -> if (subset (getRidOfSym syms_list) list_of_GoodN)
					  then (non,syms_list) :: (filter_work tl list_of_GoodN)
					  else filter_work tl list_of_GoodN


let filter_blind_alleys g = 
	let list_of_GoodN = 
	computed_fixed_point equal_sets (listGoodN (getSecond g)) (findT (getSecond g)) in
	(getFirst g , filter_work (getSecond g) list_of_GoodN)




