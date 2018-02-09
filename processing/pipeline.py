def execute_pipeline(similarity_map, *blocks):
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
			pass
	return similarity_map