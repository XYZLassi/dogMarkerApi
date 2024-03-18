from dog_marker.dtypes.pagination import SkipInt, LimitInt, Pagination


def query_pagination(skip: SkipInt = 0, limit: LimitInt = 100) -> Pagination:
    return Pagination(skip=skip, limit=limit)
