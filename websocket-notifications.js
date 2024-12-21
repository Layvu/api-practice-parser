const MAX_NOTIFICATIONS = 5;

const socket = new WebSocket("ws://localhost:8000/ws");

// При подключении WebSocket
socket.onopen = function () {
  console.log("WebSocket соединение установлено");
  loadNotifications(); // Загрузка уведомлений из localStorage
};

// При получении нового уведомления
socket.onmessage = function (event) {
  const newNotification = "Новое уведомление: " + event.data;

  // Сохранение и отображение уведомления
  saveNotification(newNotification);
  loadNotifications();
};

// При отключении WebSocket
socket.onclose = function () {
  console.log("WebSocket соединение потеряно");
};

// Загрузка уведомлений из localStorage при загрузке страницы
const loadNotifications = () => {
  const storedNotifications = JSON.parse(localStorage.getItem("notifications")) || [];
  const notificationsContainer = document.getElementById("notifications");
  notificationsContainer.innerHTML = ""; // Очистить контейнер
  storedNotifications.forEach((notification) => {
    const notificationDiv = document.createElement("div");
    notificationDiv.className = "notification";
    notificationDiv.textContent = notification;
    notificationsContainer.appendChild(notificationDiv);
  });
};

// Сохранение уведомлений в localStorage
const saveNotification = (newNotification) => {
  const storedNotifications = JSON.parse(localStorage.getItem("notifications")) || [];
  storedNotifications.unshift(newNotification);
  if (storedNotifications.length > MAX_NOTIFICATIONS) {
    storedNotifications.pop();
  }
  localStorage.setItem("notifications", JSON.stringify(storedNotifications));
};
