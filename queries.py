GET_ACTIONS_QUERY = """
SELECT timestamp, entity_id, action, value
FROM activity
WHERE entity_id IN %s
AND action IN %s
AND timestamp >= %s AND timestamp <= %s
ORDER BY timestamp ASC;
"""

