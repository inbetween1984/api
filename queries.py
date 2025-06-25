GET_ACTIONS_QUERY = """
SELECT timestamp, entity_id, action, value
FROM activity
WHERE entity_id IN %s
AND action IN %s
AND timestamp >= %s AND timestamp <= %s
ORDER BY timestamp ASC;
"""


COUNT_NON_PAIRED_ACTIONS_QUERY = """
SELECT COUNT(*) as count, entity_id, action
FROM activity
WHERE entity_id IN %s
AND action IN %s
AND timestamp >= %s AND timestamp <= %s
GROUP BY entity_id, action;
"""