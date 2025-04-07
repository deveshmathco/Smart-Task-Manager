class TaskApiService {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async makeRequest(endpoint, method = "GET", data = null, params = null) {
    const url = new URL(`${this.baseUrl}${endpoint}`);

    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] !== null && params[key] !== undefined) {
          url.searchParams.append(key, params[key]);
        }
      });
    }

    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    };

    if (data && (method === "POST" || method === "PUT")) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);

      if (!response.ok) {
        const errorData = await response.json().catch(() => {
          return { detail: `HTTP error ${response.status}` };
        });

        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }

      if (response.status === 204) {
        return { success: true };
      }

      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  }

  async getTasks(completed = null, priority = null) {
    const params = { completed, priority };
    const response = await this.makeRequest("/tasks", "GET", null, params);
    return response;
  }

  async getTask(taskId) {
    return await this.makeRequest(`/tasks/${taskId}`);
  }

  async createTask(taskData) {
    return await this.makeRequest("/tasks", "POST", taskData);
  }

  async createBatchTasks(tasksData) {
    return await this.makeRequest("/tasks/batch", "POST", { tasks: tasksData });
  }

  async updateTask(taskId, taskData) {
    return await this.makeRequest(`/tasks/${taskId}`, "PUT", taskData);
  }

  async deleteTask(taskId) {
    return await this.makeRequest(`/tasks/${taskId}`, "DELETE");
  }

  async markTasksComplete(taskIds) {
    return await this.makeRequest("/tasks/complete", "POST", {
      task_ids: taskIds,
    });
  }

  async markTasksIncomplete(taskIds) {
    return await this.makeRequest("/tasks/incomplete", "POST", {
      task_ids: taskIds,
    });
  }

  async deleteTasks(taskIds) {
    return await this.makeRequest("/tasks/delete", "POST", {
      task_ids: taskIds,
    });
  }

  async updateTaskTag(taskId) {
    return await this.makeRequest("/tagger", "POST", { task_id: taskId });
  }
}
