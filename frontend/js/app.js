document.addEventListener("DOMContentLoaded", () => {
  const api = new TaskApiService();

  const tasksContainer = document.getElementById("tasks-container");
  const createTaskBtn = document.getElementById("create-task-btn");
  const batchTaskBtn = document.getElementById("batch-task-btn");
  const taskModal = document.getElementById("task-modal");
  const batchModal = document.getElementById("batch-modal");
  const taskForm = document.getElementById("task-form");
  const batchForm = document.getElementById("batch-form");
  const modalTitle = document.getElementById("modal-title");
  const taskIdInput = document.getElementById("task-id");
  const cancelBtn = document.getElementById("cancel-btn");
  const batchCancelBtn = document.getElementById("batch-cancel-btn");
  const addBatchTaskBtn = document.getElementById("add-batch-task-btn");
  const batchTasksContainer = document.getElementById("batch-tasks");
  const selectAllCheckbox = document.getElementById("select-all");
  const bulkCompleteBtn = document.getElementById("bulk-complete-btn");
  const bulkIncompleteBtn = document.getElementById("bulk-incomplete-btn");
  const bulkDeleteBtn = document.getElementById("bulk-delete-btn");
  const statusFilter = document.getElementById("status-filter");
  const priorityFilter = document.getElementById("priority-filter");
  const applyFiltersBtn = document.getElementById("apply-filters-btn");
  const clearFiltersBtn = document.getElementById("clear-filters-btn");

  const closeButtons = document.querySelectorAll(".close");

  let currentTasks = [];
  let selectedTaskIds = [];
  let filters = {
    completed: null,
    priority: null,
  };

  loadTasks();

  async function loadTasks() {
    try {
      while (tasksContainer.firstChild) {
        tasksContainer.removeChild(tasksContainer.firstChild);
      }

      const emptyState = document.createElement("div");
      emptyState.className = "empty-state";
      emptyState.innerHTML = `
                <i class="fas fa-tasks fa-3x"></i>
                <p>No tasks found. Create a new task to get started.</p>
            `;
      tasksContainer.appendChild(emptyState);

      const response = await api.getTasks(filters.completed, filters.priority);
      currentTasks = response.tasks || [];

      currentTasks.forEach((task) => {
        TaskUI.addTaskToContainer(task, tasksContainer);
      });

      TaskUI.toggleEmptyState(tasksContainer);

      selectedTaskIds = [];
      TaskUI.updateSelectionUI(selectedTaskIds);
      selectAllCheckbox.checked = false;
    } catch (error) {
      TaskUI.showToast(error.message, "error");
    }
  }

  async function saveTask(event) {
    event.preventDefault();

    const taskId = taskIdInput.value;
    const isEdit = taskId !== "";

    const taskData = {
      title: document.getElementById("title").value,
      description: document.getElementById("description").value,
      due_date: document.getElementById("due-date").value,
      priority: document.getElementById("priority").value,
      completed: document.getElementById("completed").checked,
    };

    try {
      let savedTask;

      if (isEdit) {
        savedTask = await api.updateTask(parseInt(taskId), taskData);
        TaskUI.updateTaskInContainer(savedTask, tasksContainer);
        TaskUI.showToast("Task updated successfully", "success");
      } else {
        savedTask = await api.createTask(taskData);
        TaskUI.addTaskToContainer(savedTask, tasksContainer);
        TaskUI.showToast("Task created successfully", "success");
      }

      currentTasks = currentTasks.filter((task) => task.id !== savedTask.id);
      currentTasks.push(savedTask);

      TaskUI.hideModal(taskModal);
      TaskUI.resetForm(taskForm);

      TaskUI.toggleEmptyState(tasksContainer);
    } catch (error) {
      TaskUI.showToast(error.message, "error");
    }
  }

  function openCreateTaskModal() {
    TaskUI.resetForm(taskForm);
    taskIdInput.value = "";

    const now = new Date();
    const dueDateInput = document.getElementById("due-date");
    dueDateInput.value = TaskUI.formatDateForInput(now.toISOString());

    modalTitle.textContent = "Create New Task";

    TaskUI.showModal(taskModal);
  }

  async function openEditTaskModal(taskId) {
    try {
      const task = await api.getTask(taskId);

      taskIdInput.value = task.id;
      document.getElementById("title").value = task.title;
      document.getElementById("description").value = task.description;
      document.getElementById("due-date").value = TaskUI.formatDateForInput(
        task.due_date
      );
      document.getElementById("priority").value = task.priority;
      document.getElementById("completed").checked = task.completed;

      modalTitle.textContent = "Edit Task";

      TaskUI.showModal(taskModal);
    } catch (error) {
      TaskUI.showToast(error.message, "error");
    }
  }

  function deleteTask(taskId) {
    TaskUI.showConfirmation(
      "Are you sure you want to delete this task?",
      async () => {
        try {
          await api.deleteTask(taskId);

          TaskUI.removeTaskFromContainer(taskId, tasksContainer);

          currentTasks = currentTasks.filter((task) => task.id !== taskId);

          TaskUI.toggleEmptyState(tasksContainer);

          TaskUI.showToast("Task deleted successfully", "success");
        } catch (error) {
          TaskUI.showToast(error.message, "error");
        }
      }
    );
  }

  async function saveBatchTasks(event) {
    event.preventDefault();

    try {
      const tasksData = TaskUI.getBatchTaskData(batchForm);

      if (tasksData.length === 0) {
        TaskUI.showToast("Please add at least one task", "warning");
        return;
      }

      const createdTasks = await api.createBatchTasks(tasksData);

      createdTasks.forEach((task) => {
        TaskUI.addTaskToContainer(task, tasksContainer);
        currentTasks.push(task);
      });

      TaskUI.hideModal(batchModal);
      TaskUI.resetForm(batchForm);

      while (batchTasksContainer.firstChild) {
        batchTasksContainer.removeChild(batchTasksContainer.firstChild);
      }
      TaskUI.addBatchTaskField(batchTasksContainer);

      TaskUI.toggleEmptyState(tasksContainer);

      TaskUI.showToast(
        `${createdTasks.length} tasks created successfully`,
        "success"
      );
    } catch (error) {
      TaskUI.showToast(error.message, "error");
    }
  }

  async function markSelectedTasksComplete() {
    if (selectedTaskIds.length === 0) return;

    try {
      const updatedTasks = await api.markTasksComplete(selectedTaskIds);

      updatedTasks.forEach((task) => {
        TaskUI.updateTaskInContainer(task, tasksContainer);

        const index = currentTasks.findIndex((t) => t.id === task.id);
        if (index !== -1) {
          currentTasks[index] = task;
        }
      });

      selectedTaskIds = [];
      TaskUI.updateSelectionUI(selectedTaskIds);
      selectAllCheckbox.checked = false;

      TaskUI.showToast(
        `${updatedTasks.length} tasks marked as complete`,
        "success"
      );
    } catch (error) {
      TaskUI.showToast(error.message, "error");
    }
  }

  async function markSelectedTasksIncomplete() {
    if (selectedTaskIds.length === 0) return;

    try {
      const updatedTasks = await api.markTasksIncomplete(selectedTaskIds);

      updatedTasks.forEach((task) => {
        TaskUI.updateTaskInContainer(task, tasksContainer);

        const index = currentTasks.findIndex((t) => t.id === task.id);
        if (index !== -1) {
          currentTasks[index] = task;
        }
      });

      selectedTaskIds = [];
      TaskUI.updateSelectionUI(selectedTaskIds);
      selectAllCheckbox.checked = false;

      TaskUI.showToast(
        `${updatedTasks.length} tasks marked as incomplete`,
        "success"
      );
    } catch (error) {
      TaskUI.showToast(error.message, "error");
    }
  }

  function deleteSelectedTasks() {
    if (selectedTaskIds.length === 0) return;

    TaskUI.showConfirmation(
      `Are you sure you want to delete ${selectedTaskIds.length} tasks?`,
      async () => {
        try {
          const result = await api.deleteTasks(selectedTaskIds);

          selectedTaskIds.forEach((taskId) => {
            TaskUI.removeTaskFromContainer(taskId, tasksContainer);
          });

          currentTasks = currentTasks.filter(
            (task) => !selectedTaskIds.includes(task.id)
          );

          selectedTaskIds = [];
          TaskUI.updateSelectionUI(selectedTaskIds);
          selectAllCheckbox.checked = false;

          TaskUI.toggleEmptyState(tasksContainer);

          TaskUI.showToast(
            result.message || "Tasks deleted successfully",
            "success"
          );
        } catch (error) {
          TaskUI.showToast(error.message, "error");
        }
      }
    );
  }

  function applyFilters() {
    filters.completed =
      statusFilter.value === "" ? null : statusFilter.value === "true";
    filters.priority =
      priorityFilter.value === "" ? null : priorityFilter.value;

    loadTasks();
  }

  function clearFilters() {
    statusFilter.value = "";
    priorityFilter.value = "";

    filters.completed = null;
    filters.priority = null;

    loadTasks();
  }

  createTaskBtn.addEventListener("click", openCreateTaskModal);

  batchTaskBtn.addEventListener("click", () => {
    TaskUI.resetForm(batchForm);

    while (batchTasksContainer.firstChild) {
      batchTasksContainer.removeChild(batchTasksContainer.firstChild);
    }
    TaskUI.addBatchTaskField(batchTasksContainer);

    TaskUI.showModal(batchModal);
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const modal = button.closest(".modal");
      TaskUI.hideModal(modal);
    });
  });

  cancelBtn.addEventListener("click", () => TaskUI.hideModal(taskModal));
  batchCancelBtn.addEventListener("click", () => TaskUI.hideModal(batchModal));

  taskForm.addEventListener("submit", saveTask);

  batchForm.addEventListener("submit", saveBatchTasks);

  addBatchTaskBtn.addEventListener("click", () => {
    TaskUI.addBatchTaskField(batchTasksContainer);
  });

  tasksContainer.addEventListener("click", (event) => {
    if (event.target.closest(".action-btn.edit")) {
      const button = event.target.closest(".action-btn.edit");
      const taskId = parseInt(button.getAttribute("data-id"));
      openEditTaskModal(taskId);
    }

    if (event.target.closest(".action-btn.delete")) {
      const button = event.target.closest(".action-btn.delete");
      const taskId = parseInt(button.getAttribute("data-id"));
      deleteTask(taskId);
    }
  });

  tasksContainer.addEventListener("change", (event) => {
    if (event.target.classList.contains("task-select")) {
      const taskId = parseInt(event.target.getAttribute("data-id"));

      if (event.target.checked) {
        if (!selectedTaskIds.includes(taskId)) {
          selectedTaskIds.push(taskId);
        }
      } else {
        selectedTaskIds = selectedTaskIds.filter((id) => id !== taskId);

        selectAllCheckbox.checked = false;
      }

      TaskUI.updateSelectionUI(selectedTaskIds);
    }
  });

  selectAllCheckbox.addEventListener("change", () => {
    const checkboxes = tasksContainer.querySelectorAll(".task-select");

    checkboxes.forEach((checkbox) => {
      checkbox.checked = selectAllCheckbox.checked;

      const taskId = parseInt(checkbox.getAttribute("data-id"));

      if (selectAllCheckbox.checked) {
        if (!selectedTaskIds.includes(taskId)) {
          selectedTaskIds.push(taskId);
        }
      } else {
        selectedTaskIds = selectedTaskIds.filter((id) => id !== taskId);
      }
    });

    TaskUI.updateSelectionUI(selectedTaskIds);
  });

  bulkCompleteBtn.addEventListener("click", markSelectedTasksComplete);
  bulkIncompleteBtn.addEventListener("click", markSelectedTasksIncomplete);
  bulkDeleteBtn.addEventListener("click", deleteSelectedTasks);

  applyFiltersBtn.addEventListener("click", applyFilters);
  clearFiltersBtn.addEventListener("click", clearFilters);

  window.addEventListener("click", (event) => {
    if (event.target === taskModal) {
      TaskUI.hideModal(taskModal);
    }

    if (event.target === batchModal) {
      TaskUI.hideModal(batchModal);
    }
  });
});
