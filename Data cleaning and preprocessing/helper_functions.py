collisions_expected_number_of_fields = 29

def inspect_bad_lines(file_path, expected_fields):
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, 1):
            fields = line.strip().split(',')  # Adjust delimiter as needed
            if len(fields) != expected_fields:
                print(f"Line {line_number}: {line.strip()}")  # Print problematic line