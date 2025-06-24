GET_ACTIONS_QUERY = """
SELECT timestamp, entity_id, action, value
FROM activity
WHERE entity_id IN %s
AND action IN %s
AND timestamp >= %s AND timestamp <= %s
ORDER BY timestamp ASC;
"""


COUNT_SEX_HUNTING_QUERY = """
SELECT COUNT("value") as count, entity_id
FROM activity
WHERE entity_id IN %s
AND action = %s
AND timestamp >= %s AND timestamp <= %s;
"""