from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Request, HTTPException, Depends, Query
from starlette.status import HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.database import db_dependency, WalksOrm, AnimalsOrm
from app.utils import get_volunteer, volunteer_dependency, templates
from pydantic import BaseModel



class Slot(BaseModel):
    datetime: datetime


class ReserveWalksRequest(BaseModel):
    slots: List[Slot]


volunteer_router = APIRouter(prefix="/volunteer",
                             tags=["volunteer"],
                             dependencies=[Depends(get_volunteer)])


@volunteer_router.get("/dashboard", status_code=HTTP_200_OK)
async def staff_dashboard(request: Request, volunteer: volunteer_dependency):
    """
    Render the template with volunteer dashboard
    """
    return templates.TemplateResponse("volunteer/dashboard.html", {"request": request, "staff": volunteer})


@volunteer_router.get("/history", status_code=HTTP_200_OK)
async def volunteer_history(
    request: Request,
    volunteer: volunteer_dependency,
    db: db_dependency,
):
    """
    Returns the history of the walks for the current volunteer
    """
    # Query walks associated with the volunteer
    walks = db.query(WalksOrm).filter(WalksOrm.user_id == volunteer.id).all()

    walk_data = [
        {
            "animal_name": walk.animal.name,
            "date": walk.date,
            "duration": walk.duration,
            "location": walk.location,
        }
        for walk in walks
    ]

    return templates.TemplateResponse(
        "volunteer/history.html",
        {"request": request, "walks": walk_data},
    )


@volunteer_router.get("/animals/{animal_id}/calendar", status_code=HTTP_200_OK)
async def reserve_calendar(
    request: Request,
    animal_id: int,
    db: db_dependency,
):
    """
    Displays the calendar interface for reserving walks for a specific animal.
    """
    animal = db.query(AnimalsOrm).filter(AnimalsOrm.id == animal_id).first()
    if not animal:
        return {"error": "Animal not found"}  # TODO: replace with 404

    return templates.TemplateResponse(
        "volunteer/calendar.html",
        {
            "request": request,
            "animal": animal,
        },
    )


@volunteer_router.post("/animals/{animal_id}/reserve", status_code=HTTP_201_CREATED)
async def reserve_walks(
    animal_id: int,
    slots: List[datetime],
    db: db_dependency,
    volunteer: volunteer_dependency,
):
    """
    The function to reserve a walk slots for specific animal by a volunteer.
    """

    def group_continuous_slots(max_gap: timedelta = timedelta(hours=1)):
        """
        Helper function to group several slots into the session
        """
        grouped_sessions = []
        current_session = [slots[0]]

        for prev, curr in zip(slots, slots[1:]):
            if curr - prev <= max_gap:  # Continuous
                current_session.append(curr)
            else:  # Gap detected
                grouped_sessions.append(current_session)
                current_session = [curr]

        if current_session:
            grouped_sessions.append(current_session)

        return grouped_sessions

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

        new_walk = WalksOrm(
            animal_id=animal_id,
            user_id=volunteer.id,
            date=start_time,
            duration=duration,
            location="Shelter grounds",
        )
        db.add(new_walk)

    db.commit()

    return {"message": "Walks reserved successfully."}


@volunteer_router.get("/animals/{animal_id}/scheduled-walks", status_code=HTTP_200_OK)
async def get_scheduled_walks(
    animal_id: int,
    db: db_dependency,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
):
    """
    Fetches all scheduled walks for a specific animal within a given date range.
    """

    # Fetch scheduled walks within the given date range
    scheduled_walks = (
        db.query(WalksOrm)
        .filter(
            WalksOrm.animal_id == animal_id,
            WalksOrm.date >= start_date,
            WalksOrm.date < end_date
        )
        .all()
    )

    # Generate scheduled slots
    scheduled_slots = []

    for walk in scheduled_walks:
        start_time = walk.date
        end_time = start_time + timedelta(minutes=walk.duration)

        # Calculate the number of full hours
        total_hours = int((end_time - start_time).total_seconds() // 3600)
        remaining_minutes = int((end_time - start_time).total_seconds() % 3600)

        # If there are remaining minutes, add an extra slot
        num_slots = total_hours + (1 if remaining_minutes > 0 else 0)

        # Generate slots for each hour
        for hour_offset in range(num_slots):
            slot_time = start_time + timedelta(hours=hour_offset)
            scheduled_slots.append({
                "hour": slot_time.strftime("%H:00"),
                "date": slot_time.strftime("%Y-%m-%d"),
            })

    return {"scheduled_slots": scheduled_slots}

