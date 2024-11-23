let currentStartDate = new Date();
const selectedSlots = new Set();
const statusDiv = document.getElementById('response-status');

/** Helper function to format date as 'YYYY-MM-DD' */
const formatDate = (date) => {
    const year = date.getFullYear();
    const month = (`0${date.getMonth() + 1}`).slice(-2);
    const day = (`0${date.getDate()}`).slice(-2);
    return `${year}-${month}-${day}`;
};

/** Helper function to format datetime as 'YYYY-MM-DDTHH:MM:SS' */
const formatDateTime = (date) => {
    const year = date.getFullYear();
    const month = (`0${date.getMonth() + 1}`).slice(-2);
    const day = (`0${date.getDate()}`).slice(-2);
    const hour = (`0${date.getHours()}`).slice(-2);
    const minute = (`0${date.getMinutes()}`).slice(-2);
    const second = (`0${date.getSeconds()}`).slice(-2);
    return `${year}-${month}-${day}T${hour}:${minute}:${second}`;
};

/** Helper function to get the start of the week (Monday) */
const getMonday = (date) => {
    const day = date.getDay();
    const diff = (day + 6) % 7;
    return new Date(date.getFullYear(), date.getMonth(), date.getDate() - diff);
};

const updateWeekDates = (startDate) => {
    const options = { month: "short", day: "numeric" };
    const weekDates = Array.from({ length: 7 }, (_, i) => new Date(startDate.getTime() + i * 86400000));

    // Update week date range display
    const displayStartDate = weekDates[0].toLocaleDateString(undefined, options);
    const displayEndDate = weekDates[6].toLocaleDateString(undefined, options);
    document.getElementById("week-dates").textContent = `${displayStartDate} - ${displayEndDate}`;

    // Update date headers
    document.querySelectorAll('.date-header').forEach((header, index) => {
        header.textContent = weekDates[index].toLocaleDateString(undefined, options);
    });

    // Get current date and time
    const now = new Date();

    // Attach the `data-date` attributes to the slots and disable past slots
    document.querySelectorAll(".time-slot, .disabled").forEach((slot, index) => {
        const columnIndex = index % 7;
        const rowIndex = Math.floor(index / 7);
        const slotDate = weekDates[columnIndex];
        const slotHour = 8 + rowIndex; // Assuming hours from 8:00

        const slotDateTime = new Date(`${formatDate(slotDate)}T${(`0${slotHour}`).slice(-2)}:00`);

        // Update data attributes
        slot.dataset.date = formatDate(slotDate);
        slot.dataset.hour = (`0${slotHour}`).slice(-2) + ':00';

        // Disable past slots
        if (slotDateTime <= now) {
            slot.classList.add('disabled');
            slot.classList.remove('time-slot', 'selected');
        } else {
            slot.classList.remove('disabled');
            slot.classList.add('time-slot');
        }
    });

    // Fetch and render booked slots
    fetchScheduledWalks(startDate);
};


/** Function to fetch and render scheduled walks for a given week */
const fetchScheduledWalks = (startDate) => {
    const endDate = new Date(startDate.getTime() + 7 * 86400000);

    fetch(`/volunteer/animals/${animalId}/scheduled-walks?start_date=${formatDateTime(startDate)}&end_date=${formatDateTime(endDate)}`)
        .then(response => response.json())
        .then(data => {
            const occupiedSlots = new Set(data.scheduled_slots.map(s => `${s.hour}|${s.date}`));

            // Update calendar with booked slots
            document.querySelectorAll(".time-slot").forEach(slot => {
                const slotKey = `${slot.dataset.hour}|${slot.dataset.date}`;
                slot.classList.remove("occupied", "selected");
                if (occupiedSlots.has(slotKey)) {
                    slot.classList.add("occupied");
                }
            });
        })
        .catch(error => {
            console.error('Error fetching scheduled walks:', error);
        });
};

/** Event handler for time slot clicks */
const handleSlotClick = (event) => {
    const slot = event.target;
    if (slot.classList.contains('time-slot') && !slot.classList.contains('occupied')) {
        const key = `${slot.dataset.hour}|${slot.dataset.date}`;
        if (selectedSlots.has(key)) {
            selectedSlots.delete(key);
            slot.classList.remove('selected');
        } else {
            selectedSlots.add(key);
            slot.classList.add('selected');
        }
    }
};

/** Event handler for confirming reservation */
const confirmReservation = () => {
    if (selectedSlots.size === 0) {
        statusDiv.textContent = 'Please select at least one slot';
        return;
    }

    const slots = Array.from(selectedSlots).map(slotKey => {
        const [hour, date] = slotKey.split('|');
        return `${date}T${hour}:00`;
    });

    // Get the selected location
    const locationSelect = document.getElementById('location');
    const selectedLocation = locationSelect.value;

    // Include the location in the request body
    fetch(`/volunteer/animals/${animalId}/reserve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            slots: slots,
            location: selectedLocation,
        }),
    }).then(response => {
        if (response.ok) {
            statusDiv.textContent = 'Walks reserved successfully';
            // Timeout to allow the user to see the success message
            setTimeout(() => {
                window.location.href = `/volunteer/history`;
            });
        } else {
            response.json().then(data => {
                statusDiv.textContent = data.detail;
            });
        }
    });
};


/** Initialize the calendar */
const initializeCalendar = () => {
    currentStartDate = getMonday(new Date());
    updateWeekDates(currentStartDate);
};

/** Event listeners */
document.getElementById("prev-week").addEventListener("click", () => {
    currentStartDate.setDate(currentStartDate.getDate() - 7);
    updateWeekDates(currentStartDate);
});

document.getElementById("next-week").addEventListener("click", () => {
    currentStartDate.setDate(currentStartDate.getDate() + 7);
    updateWeekDates(currentStartDate);
});

document.addEventListener('click', handleSlotClick);
document.getElementById('confirm').addEventListener('click', confirmReservation);

// Start the calendar on page load
initializeCalendar();
