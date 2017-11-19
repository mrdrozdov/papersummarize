def tip_cell(tip, show_title=False):
    result = dict()
    result['_tip'] = tip
    result['show_title'] = show_title
    result['formatted_date'] = tip.created_at.strftime("%B %d, %Y")
    result['paper_formatted_date'] = tip.paper.published.strftime("%B %d, %Y")
    return result
