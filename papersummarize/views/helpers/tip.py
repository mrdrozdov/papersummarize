def tip_cell(tip):
    result = dict()
    result['_tip'] = tip
    result['formatted_date'] = tip.created_at.strftime("%B %d, %Y")
    return result
