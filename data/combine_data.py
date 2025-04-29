def append_files(file1, file2, file3, output_file):
    input_files = [file1, file2, file3]
    with open(output_file, 'w') as outfile:
        for idx, fname in enumerate(input_files):
            with open(fname, 'r') as infile:
                lines = infile.readlines()
                if idx == 0:
                    outfile.write(lines[0].strip() + '\n')  # Write header once
                    data_lines = lines[1:]
                else:
                    data_lines = lines[1:]  # Skip header for subsequent files
                for line in data_lines:
                    fields = line.strip().split(',')
                    if len(fields) > 0:
                        fields[-1] = fields[-1].lower()  # Lowercase Bias column (assume it's the last column)
                    outfile.write(','.join(fields) + '\n')

file1 = 'test_preprocessed.csv'
file2 = 'allsides_additional_test_preprocessed.csv'
file3 = 'newsapi_test_preprocessed.csv'
output_file1 = 'combined_test_preprocessed.csv'

append_files(file1, file2, file3, output_file1)

file4 = 'transformers_test_preprocessed.csv'
file5 = 'allsides_additional_transformers_test_preprocessed.csv'
file6 = 'newsapi_transformers_test_preprocessed.csv'
output_file2 = 'combined_transformers_test_preprocessed.csv'

append_files(file4, file5, file6, output_file2)

file7 = 'train_preprocessed.csv'
file8 = 'allsides_additional_train_preprocessed.csv'
file9 = 'newsapi_train_preprocessed.csv'
output_file3 = 'combined_train_preprocessed.csv'

append_files(file7, file8, file9, output_file3)

file10 = 'transformers_train_preprocessed.csv'
file11 = 'allsides_additional_transformers_train_preprocessed.csv'
file12 = 'newsapi_transformers_train_preprocessed.csv'
output_file4 = 'combined_transformers_train_preprocessed.csv'

append_files(file10, file11, file12, output_file4)