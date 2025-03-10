from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from pydantic import BaseModel
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from app.database import db_dependency, WalksOrm, WalkStatus, AnimalStatus
from app.utils import get_volunteer, volunteer_dependency, templates, animal_dependency, session_dependency, \
    walk_dependency


class ReserveWalksRequest(BaseModel):
    slots: List[datetime]
    location: str


volunteer_router = APIRouter(prefix="/volunteer",
                             tags=["volunteer"],
                             dependencies=[Depends(get_volunteer)])


@volunteer_router.get("/dashboard", status_code=HTTP_200_OK)
async def staff_dashboard(request: Request, volunteer: volunteer_dependency, session: session_dependency):
    """
    Render the template with volunteer dashboard
    """
    return templates.TemplateResponse(
        "volunteer/dashboard.html", {
            "request": request,
            "staff": volunteer,
            "user": session.user
        }
    )


@volunteer_router.get("/history", status_code=HTTP_200_OK)
async def volunteer_history(
        request: Request,
        volunteer: volunteer_dependency
):
    """
    Returns the history of the walks for the current volunteer
    """
    walks = volunteer.walks

    walks.sort(key=lambda walk: walk.date, reverse=True)

    return templates.TemplateResponse(
        "volunteer/history.html",
        {
            "request": request,
            "walks": walks,
            "now": datetime.now(),
            "user": volunteer
        },
    )


@volunteer_router.delete("/walks/{walk_id}/cancel", status_code=HTTP_200_OK)
async def cancel_walk(
        walk: walk_dependency,
        db: db_dependency,
        volunteer: volunteer_dependency,
):
    """
    Cancel the walk for the volunteer
    """
    if walk.user_id != volunteer.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You are not authorized to cancel this walk.")

    today = datetime.now()

    if walk.status not in [WalkStatus.pending, WalkStatus.accepted]:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Cannot cancel this walk due to its status.")

    if walk.date.date() <= today.date():
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Cannot cancel past walks.")

    # Update walk status to 'canceled'
    walk.status = WalkStatus.cancelled
    db.commit()

    return {"message": "Walk canceled successfully."}


@volunteer_router.get("/animals/{animal_id}/calendar", status_code=HTTP_200_OK)
async def reserve_calendar(
        request: Request,
        animal: animal_dependency,
        session: session_dependency
):
    """
    Displays the calendar interface for reserving walks for a specific animal.
    """

    if animal.status not in [AnimalStatus.available] or animal.hidden:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Animal is available.")

    return templates.TemplateResponse(
        "volunteer/calendar.html",
        {
            "request": request,
            "animal": animal,
            "user": session.user
        },
    )


@volunteer_router.post("/animals/{animal_id}/reserve", status_code=HTTP_201_CREATED)
async def reserve_walks(
        animal: animal_dependency,
        request: ReserveWalksRequest,
        db: db_dependency,
        volunteer: volunteer_dependency,
):
    """
    The function to reserve a walk slots for specific animal by a volunteer.
    """

    slots = request.slots
    location = request.location

    def group_continuous_slots(max_gap: timedelta = timedelta(hours=1)):
        """
        Helper function to group several slots into the session
        """
        grouped_sessions: List[List[datetime]] = []
        current_session: List[datetime] = [slots[0]]

        for prev, curr in zip(slots, slots[1:]):
            if curr - prev <= max_gap:  # Continuous
                current_session.append(curr)
            else:  # Gap detected
                grouped_sessions.append(current_session)
                current_session = [curr]

        if current_session:
            grouped_sessions.append(current_session)

        return grouped_sessions

    if animal.status not in [AnimalStatus.available] or animal.hidden:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Animal is available.")

    if not slots:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="No slots selected.")

    # Sort slots to ensure chronological order
    slots.sort()

    sessions = group_continuous_slots()

    # Create walk records in the database
    for session in sessions:
        start_time = session[0]
        end_time = session[-1] + timedelta(hours=1)  # Each slot represents one hour
        duration = int((end_time - start_time).total_seconds() / 60)  # Duration in minutes

        # Check for existing walks at the same date

        overlapping_walks = list(filter(
            lambda s_walk:
            s_walk.status not in [WalkStatus.rejected, WalkStatus.cancelled] and
            s_walk.date < end_time and
            (s_walk.date + timedelta(minutes=s_walk.duration)) > start_time,
            animal.scheduled_walks
        ))

        if overlapping_walks:
            overlapping_details = [
                f"Walk on {walk.date.strftime('%Y-%m-%d %H:%M')} for {walk.duration} minutes (status: {walk.status})"
                for walk in overlapping_walks
            ]
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Requested time slots overlap with existing walks: {', '.join(overlapping_details)}"
            )

        new_walk = WalksOrm(
            animal_id=animal.id,
            user_id=volunteer.id,
            date=start_time,
            duration=duration,
            location=location,
        )
        db.add(new_walk)

    db.commit()

    return {"message": "Walks reserved successfully."}


@volunteer_router.get("/animals/{animal_id}/scheduled-walks", status_code=HTTP_200_OK)
async def get_scheduled_walks(
        animal: animal_dependency,
        start_date: datetime = Query(...),
        end_date: datetime = Query(...),
):
    """
    Fetches all scheduled walks for a specific animal within a given date range.
    """

    if animal.status not in [AnimalStatus.available] or animal.hidden:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Animal is not available.")

    scheduled_walks = list(filter(
        lambda s_walk:
        s_walk.status not in [WalkStatus.rejected, WalkStatus.cancelled] and
        start_date <= s_walk.date < end_date, animal.scheduled_walks
    ))
    # Generate scheduled slots
    scheduled_slots = []

    for walk in scheduled_walks:
        start_time = walk.date
        end_time = start_time + timedelta(minutes=walk.duration)

        # Calculate the number of full hours
        num_slots = int((end_time - start_time).total_seconds() // 3600)

        # Generate slots for each hour
        for hour_offset in range(num_slots):
            slot_time = start_time + timedelta(hours=hour_offset)
            scheduled_slots.append({
                "hour": slot_time.strftime("%H:00"),
                "date": slot_time.strftime("%Y-%m-%d"),
            })

    return {"scheduled_slots": scheduled_slots}
