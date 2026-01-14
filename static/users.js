const userTableBody = document.querySelector("#user-table tbody");
const userForm = document.querySelector("#user-form");
const nameInput = document.querySelector("#user-name");
const emailInput = document.querySelector("#user-email");

const fetchUsers = async () => {
  const response = await fetch("/api/users");
  const users = await response.json();
  userTableBody.innerHTML = "";
  users.forEach((user) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${user.id}</td>
      <td>${user.name}</td>
      <td>${user.email}</td>
    `;
    userTableBody.appendChild(row);
  });
};

userForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    name: nameInput.value.trim(),
    email: emailInput.value.trim(),
  };
  if (!payload.name || !payload.email) {
    return;
  }
  await fetch("/api/users", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  nameInput.value = "";
  emailInput.value = "";
  await fetchUsers();
});

fetchUsers();
