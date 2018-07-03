separate_one(A,[],A):-
    \+(member(0,A)),!.
separate_one(A,ZB,C) :-
    append(A,ZB,C),
    \+(member(0,A)),
    append([0],B,ZB).

separate_zero(A,[],A):-
    \+(member(1,A)),!.
separate_zero(A,OB,C) :-
    append(A,OB,C),
    \+(member(1,A)),
    append([1],B,OB).

matcher([], sep).
matcher([1], .).
matcher([1,1], .).
matcher([1,1], -).
matcher([1,1,1], -).
matcher([1,1,1,1|T],-) :-
    \+(member(0,T)).
matcher([0],sep).
matcher([0,0],sep).
matcher([0,0],^).
matcher([0,0,0],^).
matcher([0,0,0,0],^).
matcher([0,0,0,0,0],^).
matcher([0,0,0,0,0|T],#) :-
    \+(member(1,T)).


signal_morse([],[]):- !.
signal_morse(FOFZT,B) :-
    separate_one(FO,FZT,FOFZT),
    matcher(FO,OS),
    separate_zero(FZ,T,FZT),
    matcher(FZ,ZS),
    append([OS],[ZS],OSZS),
    signal_morse(T,TS),
    append(OSZS,TS,BE),
    delete(BE,sep,B).


morse(a, [.,-]).           % A
morse(b, [-,.,.,.]).       % B
morse(c, [-,.,-,.]).       % C
morse(d, [-,.,.]).     % D
morse(e, [.]).         % E
morse('e''', [.,.,-,.,.]). % É (accented E)
morse(f, [.,.,-,.]).       % F
morse(g, [-,-,.]).     % G
morse(h, [.,.,.,.]).       % H
morse(i, [.,.]).       % I
morse(j, [.,-,-,-]).       % J
morse(k, [-,.,-]).     % K or invitation to transmit
morse(l, [.,-,.,.]).       % L
morse(m, [-,-]).       % M
morse(n, [-,.]).       % N
morse(o, [-,-,-]).     % O
morse(p, [.,-,-,.]).       % P
morse(q, [-,-,.,-]).       % Q
morse(r, [.,-,.]).     % R
morse(s, [.,.,.]).     % S
morse(t, [-]).         % T
morse(u, [.,.,-]).     % U
morse(v, [.,.,.,-]).       % V
morse(w, [.,-,-]).     % W
morse(x, [-,.,.,-]).       % X or multiplication sign
morse(y, [-,.,-,-]).       % Y
morse(z, [-,-,.,.]).       % Z
morse(0, [-,-,-,-,-]).     % 0
morse(1, [.,-,-,-,-]).     % 1
morse(2, [.,.,-,-,-]).     % 2
morse(3, [.,.,.,-,-]).     % 3
morse(4, [.,.,.,.,-]).     % 4
morse(5, [.,.,.,.,.]).     % 5
morse(6, [-,.,.,.,.]).     % 6
morse(7, [-,-,.,.,.]).     % 7
morse(8, [-,-,-,.,.]).     % 8
morse(9, [-,-,-,-,.]).     % 9
morse(., [.,-,.,-,.,-]).   % . (period)
morse(',', [-,-,.,.,-,-]). % , (comma)
morse(:, [-,-,-,.,.,.]).   % : (colon or division sign)
morse(?, [.,.,-,-,.,.]).   % ? (question mark)
morse('''',[.,-,-,-,-,.]). % ' (apostrophe)
morse(-, [-,.,.,.,.,-]).   % - (hyphen or dash or subtraction sign)
morse(/, [-,.,.,-,.]).     % / (fraction bar or division sign)
morse('(', [-,.,-,-,.]).   % ( (left-hand bracket or parenthesis)
morse(')', [-,.,-,-,.,-]). % ) (right-hand bracket or parenthesis)
morse('"', [.,-,.,.,-,.]). % " (inverted commas or quotation marks)
morse(=, [-,.,.,.,-]).     % = (double hyphen)
morse(+, [.,-,.,-,.]).     % + (cross or addition sign)
morse(@, [.,-,-,.,-,.]).   % @ (commercial at)

% Error.
morse(error, [.,.,.,.,.,.,.,.]). % error - see below

% Prosigns.
morse(as, [.,-,.,.,.]).          % AS (wait A Second)
morse(ct, [-,.,-,.,-]).          % CT (starting signal, Copy This)
morse(sk, [.,.,.,-,.,-]).        % SK (end of work, Silent Key)
morse(sn, [.,.,.,-,.]).          % SN (understood, Sho' 'Nuff)


separate_word(M,L):-
    \+(member(#,M)),
    separate_letter(M,L).
separate_word(M,L):-
    append(A,[#|B],M),
    \+(member(#,A)),
    separate_letter(A,LA),
    separate_word(B,LT),
    append(LA,[#|LT],L).

separate_letter(M,L):-
    \+(member(^,M)),
    match_letter([M],L).
separate_letter(M,L):-
    append(A,[^|B],M),
    \+(member(^,A)),
    match_letter([A],[AL]),
    separate_letter(B,LT),
    append([AL],LT,L).

match_letter([],[]):-!.
match_letter([HS|TS],L):- 
    morse(HL,HS),
    match_letter(TS,LT),
    append([HL],LT,L).

remove_error(A,A):- \+(member(error,A)).
remove_error(A,B):-
    \+(member(#,A)),
    sub_error(A,B).
remove_error(A,B):-
    append(AH,[#|AT],A),
    sub_error(AH,AHW),
    remove_error(AT,ATW),
    append(AHW,[#|ATW],B).

sub_error(A,A):- \+(member(error,A)).
sub_error(A,LT):-
    append(L,[error|LT],A),
    \+member(error,L).

signal_message(L,M):-
    signal_morse(L,MS),
    separate_word(MS,MSE),
    once(remove_error(MSE,M)).
