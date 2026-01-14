const planningTableHead = document.querySelector("#planning-table thead");
const planningTableBody = document.querySelector("#planning-table tbody");
const statsGrid = document.querySelector("#stats-grid");
const prevWeekButton = document.querySelector("#prev-week");
const nextWeekButton = document.querySelector("#next-week");
const calendarRangeLabel = document.querySelector("#calendar-range");

const STATUS_LABELS = {
  office: "",
  smart: "S",
  away: "A",
};

const STATUS_CLASSES = {
  office: "status-office",
  smart: "status-smart",
  away: "status-away",
};

const STATUS_ORDER = ["office", "smart", "away"];

const WEEKS_VISIBLE = 2;

const formatDate = (date) => date.toISOString().split("T")[0];

const getWeekStart = (date) => {
  const dayIndex = date.getDay() === 0 ? 6 : date.getDay() - 1;
  const start = new Date(date);
  start.setDate(date.getDate() - dayIndex);
  start.setHours(0, 0, 0, 0);
  return start;
};

const addDays = (date, days) => {
  const newDate = new Date(date);
  newDate.setDate(date.getDate() + days);
  return newDate;
};

const getEndOfNextMonth = (date) => {
  const endOfNextMonth = new Date(date.getFullYear(), date.getMonth() + 2, 0);
  endOfNextMonth.setHours(0, 0, 0, 0);
  return endOfNextMonth;
};

const buildDateRange = (startDate) => {
  const start = getWeekStart(startDate);
  const dates = [];
  for (let i = 0; i < WEEKS_VISIBLE * 7; i += 1) {
    dates.push(addDays(start, i));
  }
  return { start, dates };
};

const fetchUsers = async () => {
  const response = await fetch("/api/users");
  return response.json();
};

const fetchSchedule = async (start, end) => {
  const response = await fetch(`/api/schedule?start=${start}&end=${end}`);
  return response.json();
};

const createHeader = (dates) => {
  planningTableHead.innerHTML = "";
  const headerRow = document.createElement("tr");
  headerRow.innerHTML = `<th>Team member</th>`;
  dates.forEach((date) => {
    const weekday = date.toLocaleDateString(undefined, {
      weekday: "short",
    });
    const label = date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    });
    headerRow.innerHTML += `<th><span class="day-label">${weekday}</span><span class="date-label">${label}</span></th>`;
  });
  planningTableHead.appendChild(headerRow);
};

const buildScheduleMap = (entries) => {
  const map = new Map();
  entries.forEach((entry) => {
    map.set(`${entry.user_id}-${entry.day}`, entry.status);
  });
  return map;
};

const updateCellDisplay = (cell, status) => {
  cell.textContent = STATUS_LABELS[status];
  cell.className = `status-cell ${STATUS_CLASSES[status]}`;
};

const updateStats = (users, dates, scheduleMap) => {
  const weekDates = dates.slice(0, 7);
  const totals = {
    office: 0,
    smart: 0,
    away: 0,
  };

  weekDates.forEach((date) => {
    users.forEach((user) => {
      const key = `${user.id}-${formatDate(date)}`;
      const status = scheduleMap.get(key) ?? "office";
      totals[status] += 1;
    });
  });

  statsGrid.innerHTML = "";
  const totalSlots = users.length * weekDates.length;
  const buildStat = (label, value) => {
    const percentage = totalSlots
      ? Math.round((value / totalSlots) * 100)
      : 0;
    const stat = document.createElement("div");
    stat.className = "stat";
    stat.innerHTML = `<h3>${label}</h3><p>${value} (${percentage}%)</p>`;
    statsGrid.appendChild(stat);
  };

  buildStat("Office days", totals.office);
  buildStat("Smart-working days", totals.smart);
  buildStat("Away days", totals.away);
};

const formatRangeLabel = (startDate, endDate) => {
  const formatOptions = {
    month: "short",
    day: "numeric",
    year: "numeric",
  };
  const startLabel = startDate.toLocaleDateString(undefined, formatOptions);
  const endLabel = endDate.toLocaleDateString(undefined, formatOptions);
  return `${startLabel} – ${endLabel}`;
};

const updateNavigationState = (rangeStart, minStart, maxStart) => {
  prevWeekButton.disabled = rangeStart.getTime() <= minStart.getTime();
  nextWeekButton.disabled = rangeStart.getTime() >= maxStart.getTime();
};

const createScheduleTable = async (rangeStart) => {
  const { dates } = buildDateRange(rangeStart);
  const start = formatDate(dates[0]);
  const end = formatDate(dates[dates.length - 1]);

  const [users, scheduleEntries] = await Promise.all([
    fetchUsers(),
    fetchSchedule(start, end),
  ]);

  const scheduleMap = buildScheduleMap(scheduleEntries);
  createHeader(dates);
  planningTableBody.innerHTML = "";

  users.forEach((user) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${user.name}</td>`;

    dates.forEach((date) => {
      const key = `${user.id}-${formatDate(date)}`;
      const status = scheduleMap.get(key) ?? "office";
      const cell = document.createElement("td");
      updateCellDisplay(cell, status);
      cell.addEventListener("click", async () => {
        const currentStatus = scheduleMap.get(key) ?? "office";
        const nextIndex =
          (STATUS_ORDER.indexOf(currentStatus) + 1) % STATUS_ORDER.length;
        const nextStatus = STATUS_ORDER[nextIndex];

        updateCellDisplay(cell, nextStatus);
        if (nextStatus === "office") {
          scheduleMap.delete(key);
        } else {
          scheduleMap.set(key, nextStatus);
        }

        await fetch("/api/schedule", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: user.id,
            day: formatDate(date),
            status: nextStatus,
          }),
        });

        updateStats(users, dates, scheduleMap);
      });
      row.appendChild(cell);
    });

    planningTableBody.appendChild(row);
  });

  updateStats(users, dates, scheduleMap);
};

const today = new Date();
const minRangeStart = getWeekStart(today);
const maxRangeStart = addDays(
  getWeekStart(getEndOfNextMonth(today)),
  -(WEEKS_VISIBLE - 1) * 7,
);
let currentRangeStart = new Date(minRangeStart);

const refreshCalendar = async () => {
  const { dates } = buildDateRange(currentRangeStart);
  calendarRangeLabel.textContent = formatRangeLabel(
    dates[0],
    dates[dates.length - 1],
  );
  updateNavigationState(currentRangeStart, minRangeStart, maxRangeStart);
  await createScheduleTable(currentRangeStart);
};

prevWeekButton.addEventListener("click", () => {
  if (currentRangeStart.getTime() <= minRangeStart.getTime()) {
    return;
  }
  currentRangeStart = addDays(currentRangeStart, -7);
  refreshCalendar();
});

nextWeekButton.addEventListener("click", () => {
  if (currentRangeStart.getTime() >= maxRangeStart.getTime()) {
    return;
  }
  currentRangeStart = addDays(currentRangeStart, 7);
  refreshCalendar();
});

refreshCalendar();
