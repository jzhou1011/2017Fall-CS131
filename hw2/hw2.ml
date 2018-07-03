type ('nonterminal, 'terminal) symbol =
  | N of 'nonterminal
  | T of 'terminal


let rec convert_parse rules = function non_ter -> match rules with
								| hd::tl -> if fst hd = non_ter 
											then snd hd::(convert_parse tl non_ter) 
											else convert_parse tl non_ter
								| [] -> []

let convert_grammar gram1 = (fst gram1, convert_parse (snd gram1))

let rec match_rule start_sym rules_fun rules_list accept deriv frag =
	match rules_list with
	| [] -> None (*If no rule for the start_sym*)
	| hd::tl -> match match_ter rules_fun hd accept (deriv@[(start_sym,hd)]) frag with
				|Some path -> Some path
				|None -> match_rule start_sym rules_fun tl accept deriv frag
and match_ter rules_fun rule accept deriv frag = 
	if rule = [] then accept deriv frag
	(*back track to the prev acceptor function*)
	else match frag with
			| []-> None
			(*No fragment left to match the rule*)
			| hdfrag::tlfrag -> match rule with
						| [] -> None
						| (N non_ter)::rest_rule -> 
							match_rule non_ter rules_fun (rules_fun non_ter) (match_ter rules_fun rest_rule accept) deriv frag
						| (T ter)::rest_rule -> if ter = hdfrag 
												then match_ter rules_fun rest_rule accept deriv tlfrag
												else None


let parse_prefix gram = fun accept -> fun frag ->
	let start_sym = fst gram in
	let rules_fun = snd gram in
	let rules_list = rules_fun start_sym in
	match_rule start_sym rules_fun rules_list accept [] frag