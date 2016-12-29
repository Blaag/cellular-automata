# life.tcl
#
# john conway's life simulator in tcl
# created to be run on a cisco router
#
# chris schock 11/11/09
#

proc randomInit {seed} {
	global randomSeed
	set randomSeed $seed
}

proc random {} {
	global randomSeed
	set randomSeed [expr ($randomSeed*9301 + 49297) % 233280]
	return [expr $randomSeed/double(233280)]
}

proc randomRange {range} {
	expr int([random] * $range)
}

proc genMatrix {rows columns} {
#
# populate the matrix with cells
#
	global matrix

	randomInit [clock seconds]
	for {set y  1} {$y <= $rows} {incr y} {
		for {set x 1} {$x <= $columns} { incr x} {
			set index $x,$y
			set matrix($index) [randomRange 2]
		}
	}
}

proc showMatrix {rows columns} {
#
# dump the matrix to stdout
#
	global matrix

	for {set y  1} {$y <= $rows} {incr y} {
		for {set x 1} {$x <= $columns} { incr x} {
			set index $x,$y
			if ($matrix($index)) {
				puts -nonewline stdout "*"
			} else {
				puts -nonewline "."
			}
		}
		puts stdout ""
	}
}

proc countNeighbors {rows columns xcoord ycoord} {
#
# count the number of neighbors
# a given cell has, needed to
# determine whether it lives, dies,
# or a new cell is born
#
	global matrix
	set neighbors 0
		
	if {$ycoord > 1} {
		set ystart -1
	} else {
		set ystart 0
	}
		
	if {$ycoord < $rows} {
		set yend 1
	} else {
		set yend 0
	}
		
	if {$xcoord > 1} {
		set xstart -1
	} else {
		set xstart 0
	}
		
	if {$xcoord < $columns} {
			set xend 1
	} else {
		set xend 0
	}
		
	for {set y $ystart} {$y <= $yend} {incr y} {
		for {set x $xstart} {$x <= $xend} {incr x} {
			set xfinal [expr $xcoord + $x]
			set yfinal [expr $ycoord + $y]
			set index $xfinal,$yfinal
			if {$matrix($index) && (($y != 0) || ($x != 0))} {
				incr neighbors
			}
		}
	}
	return $neighbors
}

proc runIteration {rows columns} {
#
# run through a single round
# of the simulation
#
	global matrix

	for {set y 1} {$y <= $rows} {incr y} {
		for {set x 1} {$x <= $columns} {incr x} {
			set neighbors [countNeighbors $rows $columns $x $y]
			set index $x,$y
			# by default, assume a cell died
			set newmatrix($index) 0
			# a birth
			if {($neighbors == 3) && ($matrix($index) == 0)} {
				set newmatrix($index) 1
			}
			# sustained 
			if {(($neighbors == 2) || ($neighbors == 3)) && $matrix($index)} {
				set newmatrix($index) 1
			}
		}
	}
	for {set y 1} {$y <= $rows} {incr y} {
		for {set x 1} {$x <= $columns} {incr x} {
			set index $x,$y
			set matrix($index) $newmatrix($index)
		}
	}
}

proc runSim {rows columns rounds} {
#
# controls overall running of the program
# use ctrl-shift-6 to break out before the
# number of iterations complete
#
	genMatrix $rows $columns
	showMatrix $rows $columns
	for {set i 1} {$i <= $rounds} {incr i} {
		puts stdout "iteration: $i"
		runIteration $rows $columns
		showMatrix $rows $columns
	}
}

runSim 20 60 200
