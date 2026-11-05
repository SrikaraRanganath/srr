from flask import request

def paginate_query(query):
    page = int(request.args.get('page', default=1))
    page_size = int(request.args.get('page_size', default=25))

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return {
        "items": pagination.items,
        "current_page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": pagination.pages,
        "total_items": pagination.total
    }