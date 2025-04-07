class TaskUI {
  static formatDate(dateString) {
    const date = new Date(dateString);
    return (
      date.toLocaleDateString() +
      " " +
      date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    );
  }

  static formatDateForInput(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
  }

  static createTaskElement(task) {
    const taskElement = document.createElement("div");
    taskElement.className = `task-item ${task.completed ? "completed" : ""}`;
    taskElement.setAttribute("data-id", task.id);

    taskElement.innerHTML = `
            <div class="checkbox-col">
                <input type="checkbox" class="task-select" data-id="${task.id}">
            </div>
            <div class="title-col">${task.title}</div>
            <div class="priority-col">
                <span class="priority-badge priority-${task.priority}">${
      task.priority
    }</span>
            </div>
            <div class="due-date-col">${this.formatDate(task.due_date)}</div>
            <div class="status-col">
                <span class="status-badge status-${
                  task.completed ? "complete" : "incomplete"
                }">
                    ${task.completed ? "Completed" : "Incomplete"}
                </span>
            </div>
            <div class="tag-col">
                <span class="tag-badge">${task.tag || "No Tag"}</span>
            </div>
            <div class="actions-col">
                <button class="action-btn edit" data-id="${
                  task.id
                }" title="Edit Task">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete" data-id="${
                  task.id
                }" title="Delete Task">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

    return taskElement;
  }

  static addTaskToContainer(task, container) {
    const taskElement = this.createTaskElement(task);
    container.appendChild(taskElement);
  }

  static updateTaskInContainer(task, container) {
    const taskElement = container.querySelector(
      `.task-item[data-id="${task.id}"]`
    );
    if (taskElement) {
      const newTaskElement = this.createTaskElement(task);
      taskElement.replaceWith(newTaskElement);
    }
  }

  static removeTaskFromContainer(taskId, container) {
    const taskElement = container.querySelector(
      `.task-item[data-id="${taskId}"]`
    );
    if (taskElement) {
      taskElement.remove();
    }
  }

  static getSelectedTaskIds(container) {
    const checkboxes = container.querySelectorAll(".task-select:checked");
    return Array.from(checkboxes).map((checkbox) =>
      parseInt(checkbox.getAttribute("data-id"))
    );
  }

  static showModal(modal) {
    modal.style.display = "block";
  }

  static hideModal(modal) {
    modal.style.display = "none";
  }

  static resetForm(form) {
    form.reset();
  }

  static showToast(message, type = "info", duration = 3000) {
    const toastContainer = document.getElementById("toast-container");

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    let icon;
    switch (type) {
      case "success":
        icon = '<i class="fas fa-check-circle"></i>';
        break;
      case "error":
        icon = '<i class="fas fa-exclamation-circle"></i>';
        break;
      case "warning":
        icon = '<i class="fas fa-exclamation-triangle"></i>';
        break;
      default:
        icon = '<i class="fas fa-info-circle"></i>';
    }

    toast.innerHTML = `${icon} <span>${message}</span>`;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => {
        toast.remove();
      }, 300);
    }, duration);
  }

  static showConfirmation(message, onConfirm, onCancel) {
    const confirmModal = document.getElementById("confirm-modal");
    const confirmMessage = document.getElementById("confirm-message");
    const confirmOkBtn = document.getElementById("confirm-ok-btn");
    const confirmCancelBtn = document.getElementById("confirm-cancel-btn");
    const closeBtn = confirmModal.querySelector(".close");

    confirmMessage.textContent = message;

    const handleConfirm = () => {
      this.hideModal(confirmModal);
      onConfirm();

      confirmOkBtn.removeEventListener("click", handleConfirm);
      confirmCancelBtn.removeEventListener("click", handleCancel);
      closeBtn.removeEventListener("click", handleCancel);
    };

    const handleCancel = () => {
      this.hideModal(confirmModal);
      if (onCancel) onCancel();

      confirmOkBtn.removeEventListener("click", handleConfirm);
      confirmCancelBtn.removeEventListener("click", handleCancel);
      closeBtn.removeEventListener("click", handleCancel);
    };

    confirmOkBtn.addEventListener("click", handleConfirm);
    confirmCancelBtn.addEventListener("click", handleCancel);
    closeBtn.addEventListener("click", handleCancel);

    this.showModal(confirmModal);
  }

  static toggleEmptyState(container) {
    const emptyState = container.querySelector(".empty-state");
    const hasItems = container.querySelector(".task-item") !== null;

    if (emptyState) {
      emptyState.style.display = hasItems ? "none" : "block";
    }
  }

  static addBatchTaskField(container) {
    const taskIndex = container.querySelectorAll(".batch-task").length + 1;

    const taskElement = document.createElement("div");
    taskElement.className = "batch-task";

    taskElement.innerHTML = `
            <h3>Task ${taskIndex}</h3>
            <button type="button" class="remove-task-btn" title="Remove Task">
                <i class="fas fa-times"></i>
            </button>
            <div class="form-group">
                <label>Title</label>
                <input type="text" class="batch-title" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea class="batch-description" required></textarea>
            </div>
            <div class="form-group">
                <label>Due Date</label>
                <input type="datetime-local" class="batch-due-date" required>
            </div>
            <div class="form-group">
                <label>Priority</label>
                <select class="batch-priority" required>
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                </select>
            </div>
            <div class="form-group checkbox">
                <input type="checkbox" class="batch-completed" id="batch-completed-${taskIndex}">
                <label for="batch-completed-${taskIndex}">Completed</label>
            </div>
        `;

    const removeBtn = taskElement.querySelector(".remove-task-btn");
    removeBtn.addEventListener("click", () => {
      taskElement.remove();

      this.updateBatchTaskNumbers(container);
    });

    container.appendChild(taskElement);
  }

  static updateBatchTaskNumbers(container) {
    const tasks = container.querySelectorAll(".batch-task");
    tasks.forEach((task, index) => {
      const headingEl = task.querySelector("h3");
      const checkboxId = `batch-completed-${index + 1}`;

      if (headingEl) {
        headingEl.textContent = `Task ${index + 1}`;
      }

      const checkbox = task.querySelector(".batch-completed");
      const label = task.querySelector(".checkbox label");

      if (checkbox && label) {
        checkbox.id = checkboxId;
        label.setAttribute("for", checkboxId);
      }
    });
  }

  static getBatchTaskData(form) {
    const tasks = [];
    const taskElements = form.querySelectorAll(".batch-task");

    taskElements.forEach((taskEl) => {
      const title = taskEl.querySelector(".batch-title").value;
      const description = taskEl.querySelector(".batch-description").value;
      const dueDate = taskEl.querySelector(".batch-due-date").value;
      const priority = taskEl.querySelector(".batch-priority").value;
      const completed = taskEl.querySelector(".batch-completed").checked;

      tasks.push({
        title,
        description,
        due_date: dueDate,
        priority,
        completed,
      });
    });

    return tasks;
  }

  static updateSelectionUI(selectedIds) {
    const bulkCompleteBtn = document.getElementById("bulk-complete-btn");
    const bulkIncompleteBtn = document.getElementById("bulk-incomplete-btn");
    const bulkDeleteBtn = document.getElementById("bulk-delete-btn");

    const hasSelection = selectedIds.length > 0;

    bulkCompleteBtn.disabled = !hasSelection;
    bulkIncompleteBtn.disabled = !hasSelection;
    bulkDeleteBtn.disabled = !hasSelection;
  }
}
