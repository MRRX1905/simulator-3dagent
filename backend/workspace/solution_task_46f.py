def solve_task(data: dict) -> dict:
    # Implementation with error handling
    if not isinstance(data, dict):
        raise ValueError('Invalid input format')
    return {'status': 'success', 'processed': data}
