# **Technology Stack & Documentation DEGIRO**

- **Programming Language: Python**
    - [Python Documentation](https://docs.python.org/3/)
- **Web Framework: FastAPI**
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - **Role:** Serve API endpoints for data ingestion, rule evaluation, and integration with your dashboard.
- **Market Data Sources:**
    1. **Degiro API**
        - (Refer to Degiro resources and internal documentation as available.)
    1. **MacroPulse**
        - [MacroPulse Documentation](https://www.macropulse.com/) (or your chosen provider)
    1. **Additional Free Source – Alpha Vantage or Finnhub:**
        - **Alpha Vantage:**
            - [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
            - **Free Tier:** Offers up to 500 requests per day; suitable for prototyping and lower-frequency data retrieval.
        - **Alternatively, Finnhub:**
            - [Finnhub Documentation](https://finnhub.io/docs/api)
            - **Free Tier:** Provides real-time data on U.S. equities and more with certain usage limits.
    - **Note:** Choose the provider that best fits your data frequency and coverage needs while keeping costs at zero.
- **Task Queue & Scheduler: Celery**
    - [Celery Documentation](https://docs.celeryq.dev/en/stable/)
    - [Redis Documentation](https://redis.io/documentation)
    - **Role:** Manage asynchronous tasks (e.g., periodic data fetching, rule evaluations, notifications).
- **Data Storage: PostgreSQL**
    - [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- **Secrets Management: HashiCorp Vault**
    - [Vault Documentation](https://www.vaultproject.io/docs)
- **Logging & Monitoring:**
    - **Metrics & Dashboards:**
        - **Prometheus:**
            - [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
            - **Role:** Collect and store metrics.
        - **Grafana:**
            - [Grafana Documentation](https://grafana.com/docs/)
            - **Role:** Visualize metrics and logs.
    - **Log Aggregation:**
        - **Grafana Loki:**
            - [Grafana Loki Documentation](https://grafana.com/docs/loki/latest/)
            - **Role:** Collect, query, and visualize logs in a cost-effective, open-source stack.
- **Containerization: Docker**
    - [Docker Documentation](https://docs.docker.com/)
- **Notification Systems:**
    - **Twilio:**
        - [Twilio API Documentation](https://www.twilio.com/docs/usage/api)
        - **Role:** Send SMS or other notifications reliably.
- **Frontend Dashboard:**
    - **React with Vite:**
        - [React Documentation](https://reactjs.org/docs/getting-started.html)
        - [Vite Documentation](https://vitejs.dev/)
        - **Role:** Build a fast, modern web UI for real-time alerts and system status visualization.
- **Development Environment:**
    - **PyCharm IDE:**
        - [PyCharm Documentation](https://www.jetbrains.com/pycharm/documentation/)
    - **Cursor/Zencoder:**
        - (Verify integration instructions if these tools are part of your media or workflow automation tasks.)

---

## **Revised Project Phases & Action Plan**

### **Phase 1: Define Objectives and Initial Rules**

**Objectives:**

- Identify the list of assets (ETFs, stocks, commodities) to monitor.
- Confirm three data sources: Degiro API, MacroPulse, and a free real-time source (Alpha Vantage or Finnhub).
- Define key alert triggers (e.g., price thresholds, volume spikes, technical indicators).

**Actions:**

1. Create a detailed document or spreadsheet mapping each asset to its associated rules.
2. Finalize and store API credentials securely using HashiCorp Vault.
3. Outline each asset’s performance indicators (price, volume, RSI, moving averages) and define threshold conditions.

---

### **Phase 2: Build a Monolithic MVP Using FastAPI**

**Objectives:**

- Develop a working monolithic application that integrates data ingestion, rule evaluation, and notifications.
- Ensure the architecture is modular enough to extract components later.

**Actions:**

1. **Data Pipeline Setup:**
    - Develop asynchronous FastAPI endpoints to fetch data concurrently from Degiro, MacroPulse, and Alpha Vantage (or Finnhub).
    - Use HashiCorp Vault to load API keys and manage credentials.
    - Store the retrieved data in PostgreSQL.
    - **Reference:**
        - [FastAPI Asynchronous Endpoints](https://fastapi.tiangolo.com/async/)
1. **Rules Engine Development:**
    - Create modular Python classes/functions to encapsulate rule evaluation logic.
    - Implement logging for each rule evaluation using Loki, with metrics stored in Prometheus.
    - Test and validate rule triggers using a simulated (paper trading) mode.
1. **Notification and Dashboard Creation:**
    - Integrate Twilio for sending SMS alerts.
    - Develop a basic dashboard with FastAPI endpoints and build the UI in React using Vite.
    - Connect Grafana to Prometheus and Loki for real-time monitoring and log visualization.
    - **Reference:**
        - [Celery Periodic Tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)

---

### **Phase 3: Modularization & Scalability Enhancements**

**Objectives:**

- Transition from a monolithic application to a modular, microservices-based architecture.
- Isolate core functionalities (data ingestion, rules evaluation, notifications) into separate services.

**Actions:**

1. **Service Extraction:**
    - Extract core components into dedicated services.
    - Containerize each service with Docker for independent deployment.
1. **Event-Driven Communication:**
    - Set up a lightweight message broker (Redis or RabbitMQ) to enable asynchronous inter-service communication.
1. **Scalability & Deployment:**
    - Use Docker Compose (or eventually Kubernetes) to orchestrate the services.
    - Monitor performance with Prometheus and visualize with Grafana.
    - **Documentation References:**
        - [Docker Compose](https://docs.docker.com/compose/)
        - [Kubernetes](https://kubernetes.io/docs/home/)

---

### **Phase 4: Security, Monitoring, and UX Enhancements**

**Objectives:**

- Strengthen overall system security.
- Upgrade the monitoring and logging stack.
- Enhance the dashboard for a smoother user experience.

**Actions:**

1. **Security Enhancements:**
    - Implement HTTPS/TLS, RBAC, and MFA for sensitive endpoints.
    - Ensure secure API communications and safe storage of secrets.
1. **Advanced Monitoring:**
    - Fully integrate Prometheus for metrics collection and Grafana for dashboard visualization.
    - Use Grafana Loki for cost-effective, open-source log aggregation and analysis.
1. **User Interface Upgrades:**
    - Enhance the React dashboard for near real-time updates (e.g., using WebSockets).
    - Iterate on UI based on user feedback.

---

### **Phase 5: Future Enhancements & Continuous Improvement**

**Objectives:**

- Integrate advanced analytics (machine learning, technical indicators) for improved trading insights.
- Expand market data feed options if needed.
- Schedule regular system audits and code refactoring sessions.

**Actions:**

1. **Advanced Analytics:**
    - Evaluate technical analysis libraries such as [TA-Lib](https://mrjbq7.github.io/ta-lib/).
1. **Expand Integrations:**
    - Monitor additional data sources or premium feeds if future requirements demand faster or more comprehensive data.
1. **Continuous Improvements:**
    - Regularly audit system performance, security configurations, and logs.
    - Update dependencies and refine code structure.

[##microsoft / ##qlib](https://github.com/microsoft/qlib)

[##ccxt / ##ccxt](https://github.com/ccxt/ccxt)