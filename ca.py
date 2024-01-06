import math

# rule = 30
width = 150
iterations = 100
alive_char = "\u2593"
dead_char = " "

def init_field(width):
    # Initialize a list of all zeroes
    field = [0] * width

    # Set the middle element to a 1
    field[int(width / 2)] = "1"

    return field

def field_to_string(field, width, alive_char, dead_char):
    # Convert the field list to a printable string
    field_string = ""

    for i in range(width):
        if field[i] == "1":
            field_string += alive_char
        else:
            field_string += dead_char
        # field_string += str(field[i])

    return field_string

def rule_to_binary_string(rule):
    # Takes a rule as a number and converts it to a string of eight characters
    # that represent the number in binary.
    # For example rule 7 would be represented as "00000111"

    binary_string = ""
    check_value = rule

    # Yeah this is not very efficient but it follows
    # how to convert decimal to binary by hand
    while check_value / 2 >= 1:
        binary_string = str(check_value % 2) + binary_string
        check_value = math.floor(check_value / 2)

    # The loop will stop before adding the final digit, so we do it here
    binary_string = str(check_value %2) + binary_string

    # Pad the string with leading zeroes if necessary
    binary_string_length = len(binary_string)
    if binary_string_length < 8:
        binary_string = "0" * (8 - binary_string_length) + binary_string

    return binary_string

def get_neighborhood(field, index, width):
    # Return a string that represents the cell and the neighbors to the left and right.
    # In the case where the cell is on the end of the list, wrap.

    left_neighbor = field[(index - 1) % width]
    right_neighbor = field[(index + 1) % width]

    neighborhood = str(left_neighbor) + str(field[index]) + str(right_neighbor)

    # print(f'neighborhood at index {index:5}: {neighborhood}')

    return neighborhood

def get_cell_value_by_rule(neighborhood, rule):
    # The rule is representing a binary value as a string,
    # for example rule 5 would be "00000101".
    # So when matching, match from the right
    match neighborhood:
        case "000":
            cell_status = rule[7]
        case "001":
            cell_status = rule[6]
        case "010":
            cell_status = rule[5]
        case "011":
            cell_status = rule[4]
        case "100":
            cell_status = rule[3]
        case "101":
            cell_status = rule[2]
        case "110":
            cell_status = rule[1]
        case "111":
            cell_status = rule[0]
        case _:
            print("Something went very wrong.")
            exit(1)

    # print(f'neighborhood {neighborhood} with rule {rule} has cell status of {cell_status}')

    return cell_status

def next_round(field, rule_as_string, width):

    new_field = []

    for i in range(width):
        # Get a string representing the value of the cell and the values of those
        # to the left and the right
        neighborhood_string = get_neighborhood(field, i, width)
        new_field.append(get_cell_value_by_rule(neighborhood_string, rule_as_string))

    return new_field

def main():
    for rule in range(256):
        print(f'RULE {rule}')
        field = init_field(width)

        # print(f'field is:')
        # print(field)
        rule_as_string = rule_to_binary_string(rule)

        for r in range(iterations):
            # Display the current list of cells that are alive or dead
            print(f'{r:5}: {field_to_string(field, width, alive_char, dead_char)}')

            # Determine the next round
            field = next_round(field, rule_as_string, width)

if __name__ == '__main__':
    main()
