import psycopg2
from fastapi import HTTPException

from config import logger, QUESTDB_HOST, QUESTDB_PORT
from models import ActionsRequest
from queries import GET_ACTIONS_QUERY, COUNT_NON_PAIRED_ACTIONS_QUERY
from utils import parse_time, get_db_connection

NON_PAIRED_ACTIONS = {"sex_hunting"}

async def get_actions(request: ActionsRequest):
    try:
        start_time = parse_time(request.start_time)
        end_time = parse_time(request.end_time)

        if start_time > end_time:
            logger.warning(f"invalid time range: start_time {start_time} > end_time {end_time}")
            return []

        all_actions = tuple(request.actions + [f"end_{action}" for action in request.actions if action not in NON_PAIRED_ACTIONS])
        entity_ids = tuple(request.entity_ids)

        logger.info(f"executing SQL query: {GET_ACTIONS_QUERY} with params {entity_ids}, {all_actions}, {start_time}, {end_time}")

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(GET_ACTIONS_QUERY, (entity_ids, all_actions, start_time, end_time))
                rows = cur.fetchall()

                non_paired_counts = {}
                non_paired_requested = NON_PAIRED_ACTIONS & set(request.actions)
                if non_paired_requested:
                    cur.execute(COUNT_NON_PAIRED_ACTIONS_QUERY, (entity_ids, tuple(non_paired_requested), start_time, end_time))
                    count_results = cur.fetchall()
                    logger.info(f"non-paired actions count result: {count_results}")
                    non_paired_counts = {(result["entity_id"], result["action"]): result["count"] for result in count_results}

        if not rows:
            logger.warning(f"No data found for entity_ids: {request.entity_ids}, actions: {all_actions}")
            return []

        response = []
        for entity_id in request.entity_ids:
            entity_rows = [row for row in rows if row['entity_id'] == entity_id]
            if not entity_rows:
                logger.info(f"No data found for entity_id: {entity_id}")

            actions_data = {action: [] for action in request.actions if action not in NON_PAIRED_ACTIONS}
            total_duration = {action: 0.0 for action in request.actions if action not in NON_PAIRED_ACTIONS}
            session_count = {action: 0 for action in request.actions}

            action_timestamps = {}
            for row in entity_rows:
                action = row['action']
                action_timestamps.setdefault(action, []).append(row['timestamp'])

            for action in request.actions:
                if action in NON_PAIRED_ACTIONS:
                    session_count[action] = non_paired_counts.get((entity_id, action), 0)
                    continue
                action_times = sorted(action_timestamps.get(action, []))
                end_action_times = sorted(action_timestamps.get(f"end_{action}", []))

                for i in range(min(len(action_times), len(end_action_times))):
                    action_time = action_times[i]
                    end_time = end_action_times[i]
                    duration = (end_time - action_time).total_seconds()

                    actions_data[action].append({
                        "action": action,
                        "action_start": action_time.isoformat(),
                        "action_end": end_time.isoformat(),
                        "duration_seconds": duration
                    })
                    total_duration[action] += duration
                    session_count[action] += 1

            average_duration = {
                action: (
                    total_duration[action] / session_count[action] if session_count[action] > 0 else 0.0
                )
                for action in total_duration
            }

            response.append({
                "entity_id": entity_id,
                "actions": actions_data,
                "total_duration": total_duration,
                "average_duration": average_duration,
                "session_count": session_count
            })

        return response

    except psycopg2.Error as e:
        logger.error(f"database error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="database error occurred")
    except Exception as e:
        logger.error(f"unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"unexpected error: {str(e)}")


async def startup_event():
    try:
        with get_db_connection() as conn:
            logger.info(f"success connect to QuestDB at {QUESTDB_HOST}:{QUESTDB_PORT}")
    except Exception as e:
        logger.error(f"failed to connect to QuestDB: {e}")
        raise Exception("QuestDB connection failed")


async def shutdown_event():
    logger.info("QuestDB connection closed")