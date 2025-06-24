from fastapi import FastAPI, HTTPException

from config import logger, QUESTDB_HOST, QUESTDB_PORT
from models import *
from queries import GET_ACTIONS_QUERY, COUNT_SEX_HUNTING_QUERY
from utils import parse_time, get_db_connection

app = FastAPI(title="Cow Actions API")

@app.post("/actions", response_model=list[EntityResponse])
async def get_actions(request: ActionsRequest):
    try:
        start_time = parse_time(request.start_time)
        end_time = parse_time(request.end_time)

        if start_time > end_time:
            logger.warning(f"invalid time range: start_time {start_time} > end_time {end_time}")
            return []

        all_actions = tuple(request.actions + [f"end_{action}" for action in request.actions if action != "sex_hunting"])
        entity_ids = tuple(request.entity_ids)

        logger.info(f"executing SQL query: {GET_ACTIONS_QUERY} with params {entity_ids}, {all_actions}, {start_time}, {end_time}")

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(GET_ACTIONS_QUERY, (entity_ids, all_actions, start_time, end_time))
                rows = cur.fetchall()

                count_sex_hunting = []
                if "sex_hunting" in request.actions:
                    cur.execute(COUNT_SEX_HUNTING_QUERY, (entity_ids, "sex_hunting", start_time, end_time))
                    count_sex_hunting = cur.fetchall()


        if not rows:
            logger.warning(f"no data found for entity_ids: {request.entity_ids}, actions: {all_actions}")
            return []

        count_sex_hunting_dict = {result["entity_id"]: result["count"] for result in count_sex_hunting}

        response = []
        for entity_id in request.entity_ids:
            entity_rows = [row for row in rows if row['entity_id'] == entity_id]
            actions_data = {action: [] for action in request.actions if action != "sex_hunting"}
            total_duration = {action: 0.0 for action in request.actions if action != "sex_hunting"}
            session_count = {action: 0 for action in request.actions}

            for action in request.actions:
                if action == "sex_hunting":
                    session_count["sex_hunting"] = count_sex_hunting_dict.get(entity_id, 0)
                    continue

                action_times = [row['timestamp'] for row in entity_rows if row['action'] == action]
                end_action_times = [row['timestamp'] for row in entity_rows if row['action'] == f"end_{action}"]

                for i in range(len(action_times)):
                    action_time = action_times[i]
                    end_time = end_action_times[i]
                    duration = (end_time - action_time).total_seconds()
                    if duration >= 0:
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
                    total_duration[action] / session_count[action] if session_count[action] > 0 else 0
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

        logger.info(
            f"processed data for {len(request.entity_ids)} entities, found {sum(sum(r['session_count'].values()) for r in response)} sessions")
        return response

    except Exception as e:
        logger.error(f"error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"error processing request: {str(e)}")


@app.on_event("startup")
async def startup_event():
    try:
        with get_db_connection() as conn:
            logger.info(f"success connect to QuestDB at {QUESTDB_HOST}:{QUESTDB_PORT}")
    except Exception as e:
        logger.error(f"failed to connect to QuestDB: {e}")
        raise Exception("QuestDB connection failed")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("QuestDB connection closed")