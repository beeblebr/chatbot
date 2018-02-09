def augment_return(func):
	def return_tuple(*args, **kwargs):
		result = func(*args, **kwargs)
		if type(result) != tuple:
			result = (result, None)
		return result
	return return_tuple


def execute_pipeline(similarity_map, *blocks):
	for block in blocks:
		print(block)
		try:
			if len(block) > 1:
				fn, params = block
				similarity_map, return_values = fn(similarity_map, return_values, *params)
			else:
				fn = block[0]
				similarity_map, return_values = fn(similarity_map, return_values)
		except Exception as e:
			pass
	return similarity_map