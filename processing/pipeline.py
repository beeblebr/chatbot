from __future__ import print_function


def execute_pipeline(similarity_map, *blocks):
	print('execing', file=sys.stderr)
	for block in blocks:
		print(block)
		try:
			if len(block) > 1:
				fn, params = block
				similarity_map  = fn(similarity_map, *params)
			else:
				fn = block[0]
				similarity_map = fn(similarity_map)
		except Exception as e:
			print(e)
	return similarity_map