#lang racket

(define (null-ld? obj) (if (pair? obj) (eq? (car obj) (cdr obj)) #f))

(define (listdiff? obj) (if (pair? obj) (cond [(eq? (cdr obj) empty) #t]
											  [(eq? (car obj) (cdr obj)) #t]
											  [(eq? (car obj) empty) #f]
											  [else (if (pair? (car obj)) 
											  			(listdiff? (cons (cdr (car obj)) (cdr obj))) #f)])#f))

(define (cons-ld obj listdiff) (cons (cons obj (car listdiff)) (cdr listdiff)))

(define (car-ld listdiff) (car (car listdiff)))

(define (cdr-ld listdiff) (cons (cdr (car listdiff)) (cdr listdiff)))

(define (listdiff obj . args) (cons (cons obj args) '()))

(define (length-ld listdiff) (cond [(null-ld? listdiff) 0]
								   [else (+ (length-ld (cdr-ld listdiff)) 1)] ))

(define (listdiff->list listdiff) (cond [(null-ld? listdiff) '()]
									  [else (cons (car-ld listdiff) (listdiff->list (cdr-ld listdiff)))]))

(define (append-ld-helper listdiff listlistdiff) (cond [(equal? listlistdiff '()) listdiff]
													   [else (let ((tail (append-ld-helper (car listlistdiff) (cdr listlistdiff))))
													   				(cons (append (listdiff->list listdiff) (car tail)) (cdr tail)))]))

(define (append-ld listdiff . args) (append-ld-helper listdiff args))

(define (list-tail-ld listdiff k) (cond [(equal? k 0) listdiff]
										[else (list-tail-ld (cdr-ld listdiff) (- k 1))]))

(define (list->listdiff list) (cons list '()))

(define (expr-returning listdiff) `(cons ', (listdiff->list listdiff) '() ))



