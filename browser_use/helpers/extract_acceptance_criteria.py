from typing import List


def extract_acceptance_criteria(description: dict) -> List[str]:
	criteria = []
	if not description:
		return criteria

	for item in description.get('content', []):
		if item['type'] == 'bulletList':
			if item['type'] == 'bulletList':
				for list_item in item['content']:
					for block in list_item['content']:
						for text_block in block.get('content', []):
							criteria.append(text_block['text'])

	return criteria
