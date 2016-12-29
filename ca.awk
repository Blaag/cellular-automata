function setseed () {
	cmd = "date +%s"
	cmd | getline seed
	close(cmd)
	#print "seed is " seed
	srand(seed)
}

function setfield(width) {
	for (loop = 1; loop <= width; loop++) {
		field[loop] = int(rand() * 2)
	}
}

function setfield2(width) {
	for (loop = 1; loop <= width; loop++) {
		field[loop] = 0
	}
	field[int(width/2)] = 1
}

function displayfield() {
	for (loop = fieldwidth; loop >= 1; loop--) {
		if (field[loop] < 1) {
			printf(" ")
		}
		if ((field[loop] > 0) && (field[loop] < 2)) {
			printf(".")
		}
		if ((field[loop] >= 2) && (field[loop] < 4)) {
			printf("o")
		}
		if ((field[loop] >= 4) && (field[loop] < 6)) {
			printf("O")
		}
		if ((field[loop] >= 6) && (field[loop] < 8)) {
			printf("0")
		}
		if ((field[loop] >= 8) && (field[loop] < 10)) {
			printf("*")
		}
		if (field[loop] >= 10) {
			printf("#")
		}
	}
	printf("\n")
}

function ruletobits(ruleBase10, ruleWidth) {
	numerator = ruleBase10
	ruleBase2 = ""

	# convert the decimal value to a binary string
	while (numerator > 1) {
		remainder = numerator % 2
		ruleBase2 = remainder "" ruleBase2
		numerator = int(numerator / 2)
	}

	# deal with the case where the numerator did not divide cleanly the last time
	if (numerator > 0) {
		ruleBase2 = "1" ruleBase2
	}

	# if necessary, pad the binary string so its the required width
	if (length(ruleBase2) < ruleWidth) {
		padbits = ruleWidth - length(ruleBase2)
		for (padloop = 0; padloop < padbits; padloop++) {
			ruleBase2 = "0" ruleBase2
		}
	}

	#print "ruleBase2 is " ruleBase2

	return ruleBase2
}

function getneighbors(fieldposition) {
	if (fieldposition == 1) {
		rightneighbor = field[fieldwidth]
	} else {
		rightneighbor = field[fieldposition - 1]
	}
	if (fieldposition == fieldwidth) {
		leftneighbor = field[1]
	} else {
		leftneighbor = field[fieldposition + 1]
	}

	# return three bits indicating whether the neighbor spots are occupied
	# a bitwise and on the result ensures that if a number greater than one is in the array
	# the bit will only be one
	neighbors = (leftneighbor && 1) "" (field[fieldposition] && 1) "" (rightneighbor && 1)

	return neighbors
}

function mapbintodec(bitvector) {
	if (bitvector == "000") {
		return 0
	}

	if (bitvector == "001") {
		return 1
	}

	if (bitvector == "010") {
		return 2
	}

	if (bitvector == "011") {
		return 3
	}

	if (bitvector == "100") {
		return 4
	}

	if (bitvector == "101") {
		return 5
	}

	if (bitvector == "110") {
		return 6
	}

	if (bitvector == "111") {
		return 7
	}

}

function reverse(origstring) {
	origlength = length(origstring)
	newstring = ""
	for (revloop = 1; revloop <= origlength; revloop++) {
		newstring = newstring "" substr(origstring,origlength - revloop + 1,1)
	}
	return newstring
}

function newgeneration() {
	# look at each cell in the field - remember field goes from right to left!
	for (cellindex = 1; cellindex <= fieldwidth; cellindex++) {
		# first find the neighbors for the cell
		neighbors = getneighbors(cellindex)
		#print "index " cellindex " neighbors found to be " neighbors

		# next convert those three bits into a decimal value
		# string arrays are indexed at 1 instead of 0, so we
		# must add 1
		ruleindex = mapbintodec(neighbors) + 1
		#print "conversion to decimal is " ruleindex - 1

		# now use that value as the index to the rule to determine whether
		# cell lives or dies
		rulevalue = substr(reverse(rulebits), ruleindex, 1)
		#print rulebits " - index " ruleindex " for neighbors value of " neighbors " is " rulevalue

		# map the result into the new field
		if (rulevalue == "0") {
			newfield[cellindex] = 0
		} else {
			newfield[cellindex] = field[cellindex]
			newfield[cellindex]++
		}
	}

	# now copy the new field to the current field
	for (cellindex = 1; cellindex <= fieldwidth; cellindex++) {
		field[cellindex] = newfield[cellindex]
	}
}

BEGIN {
	generations = 0
	fieldwidth = 200
	numruns = 100
}
{
	# seed the random number generator
	setseed()

	for (ruleloop = 1; ruleloop <= 100; ruleloop++) {
		# seed the starting field
		setfield(fieldwidth)
		#setfield2(fieldwidth)

		# display the starting field
		displayfield()

		# convert the rule to bits and ensure that leading zeroes are there
		rulebits = ruletobits(ruleloop, 8)
		print "+++ RULE " ruleloop " +++"

		for (iteration = 0; iteration < numruns; iteration++) {
			newgeneration()
			displayfield()
		}
	}
}
END {
}
