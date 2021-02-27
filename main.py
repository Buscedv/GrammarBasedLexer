# TODO:
# Read grammar rules.
# Lex grammar rules.
# Merge grammar rules.
# Store in cache (local text file)?

# Loop over source.
# Find matches in the merged grammar rules by "ruling non-matching ones" out, char by char.
# Store the tokens by type and value.

import os
from prettyprinter import pprint


def merge_rules(tokens: list) -> dict:
	rules = {}

	pprint(tokens)

	return rules


def is_part_of_word(char):
	return char.isalpha() or char in ['_'] or char.isdigit()


def lex_rules(raw_rules: list) -> dict:
	rules_tokens = {}

	rule_name_collect = True
	rule_name = ''

	tmp = ''
	collect = False
	collect_end: list = []
	skip_on_end = True
	token_type = ''

	collect_ends = {
		'REGEX': ['}'],
		'WORD': ['\'', '"', '{', '\n', '|', '+', '-', '*', '/', '%', '?', '(', ')', ' ']
	}

	for line in raw_rules:
		line = line.replace("\\'", 'ESC_SINGLE_QUOTE').replace('\\"', 'ESC_QUOTE')
		for char in line:
			if rule_name_collect:
				if char == '=':
					if not rule_name:
						break

					rules_tokens[rule_name] = []
					rule_name_collect = False
				elif is_part_of_word(char):
					rule_name += char
			else:
				if collect:
					if char not in collect_end:
						tmp += char
						continue

					collect = False
					collect_end = []

					rules_tokens[rule_name].append([token_type, tmp])
					token_type = ''
					tmp = ''

					if skip_on_end:
						continue

				if char == '(':
					rules_tokens[rule_name].append(['GROUP_START', '('])
				if char == ')':
					rules_tokens[rule_name].append(['GROUP_END', ')'])
				if char == '|':
					rules_tokens[rule_name].append(['OR', '|'])
				if char == '+':
					rules_tokens[rule_name].append(['1_OR_MORE', '+'])
				if char == '*':
					rules_tokens[rule_name].append(['0_OR_MORE', '*'])
				if char == '?':
					rules_tokens[rule_name].append(['0_OR_1', '?'])

				if char in ['\'', '"']:
					token_type = 'EXACT'

				if char == '{':
					token_type = 'REGEX'

				if is_part_of_word(char):
					token_type = 'WORD'

				# Assigns other values based on the collection token type
				if token_type:
					collect = True
					skip_on_end = True

					if token_type == 'WORD':
						skip_on_end = False
						tmp += char

					try:
						collect_end = collect_ends[token_type]
					except KeyError:
						if token_type == 'EXACT':
							collect_end = [char]
			if char == '\n':
				rule_name = ''
				rule_name_collect = True

	return rules_tokens


def read_rules(file):
	if os.path.isfile(f'{os.getcwd()}/{file}'):
		with open(file, 'r') as f:
			raw_rules = f.readlines()

		rule_tokens = lex_rules(raw_rules)
		rules = merge_rules(rule_tokens)


# cache_rules(rules)


def main():
	read_rules('rules.grammar')


if __name__ == '__main__':
	main()
