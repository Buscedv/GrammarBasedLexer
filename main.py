# TODO:
# Read grammar rules. X
# Lex grammar rules. X
# Merge grammar rules. X
# Store in cache (local text file)?

# Loop over source.
# Find matches in the merged grammar rules by "ruling non-matching ones" out, char by char.
# Store the tokens by type and value.

import os
import re
from prettyprinter import pprint


def get_tokens_by_word(word):
	global rule_tokens

	for rule, value in rule_tokens.items():
		if rule != word:
			continue
		return value


def recursive_rule_parser(tokens) -> str:
	global rule_tokens

	if not tokens:
		return ''

	regex = r''
	for token in tokens:
		token_type = token[0]
		token_val = token[1]

		if token_type == 'EXACT':
			regex += re.escape(token_val)
		elif token_type == 'WORD':
			regex += recursive_rule_parser(get_tokens_by_word(token_val))
		elif token_type == 'REGEX':
			regex += f'({token_val})'
		else:
			regex += token_val

	return regex


def merge_rules(rules: dict) -> dict:
	pprint(rules)

	merged = {rule: recursive_rule_parser(value) for rule, value in rules.items()}

	pprint(merged)
	return merged


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
		line = line.replace("\\'", 'ESC_SINGLE_QUOTE')
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
	global rule_tokens

	if os.path.isfile(f'{os.getcwd()}/{file}'):
		with open(file, 'r') as f:
			raw_rules = f.readlines()

		rule_tokens = lex_rules(raw_rules)
		return merge_rules(rule_tokens)

	return {}


def lex(file: str, rules: dict) -> list:
	tokens = []

	if os.path.isfile(f'{os.getcwd()}/{file}'):
		with open(file, 'r') as f:
			raw_source = f.readlines()

		for line in raw_source:
			possible = [rule for rule, pattern in rules.items() if re.match(pattern, line)]
			if possible:
				tokens.append([possible[-1], line])

	return tokens


def main():
	rules = read_rules('rules.grammar')
	pprint(lex('source.lang', rules))


rule_tokens = {}

if __name__ == '__main__':
	main()
