# Automated MLOps Pipeline: Image Captioning & Object Detection

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Optional: [![Build Status](YOUR_JENKINS_BADGE_URL)](YOUR_JENKINS_JOB_URL) -->

Final project for **CSE 816: Software Production Engineering**, demonstrating an automated DevOps framework for an MLOps application suite (Image Caption Generator & YOLOv3 Object Detection). The focus is on the **DevOps pipeline and MLOps practices**.

---

## :rocket: Core Idea

Automate the entire SDLC from code commit to deployment, scaling, and monitoring of ML applications using a modern DevOps toolchain.

**Key DevOps Features:**
*   **CI/CD:** Jenkins (`Jenkinsfile`) for automated build, test, containerization, deployment.
*   **Containerization:** Docker (`Dockerfile`) & Docker Compose for local dev.
*   **Config Management:** Ansible (`ansible/`) for local environment setup (Docker, Minikube).
*   **Orchestration:** Kubernetes (`kubernetes/`) for deployment, scaling (HPA), service discovery.
*   **Monitoring:** ELK Stack for centralized logging (Filebeat for log shipping).

---

## :hammer_and_wrench: Tech Stack

*   **Apps:** Python, Flask, TensorFlow/Keras, OpenCV
*   **DevOps Tools:** Git/GitHub, Jenkins, Docker, Ansible, Kubernetes (Minikube), ELK Stack.

---

## :compass: System Architecture

*(Strongly recommend replacing this with an IMAGE of your architecture diagram: `![System Architecture](path/to/diagram.png)`)*
```mermaid
graph LR
    Developer -- Git Push --> GitHub;
    GitHub -- Trigger --> Jenkins;
    Jenkins -- Pipeline --> DockerHub;
    Jenkins -- Deploy --> Kubernetes_Cluster(Minikube);
    Kubernetes_Cluster -- Runs --> App_Pods;
    App_Pods -- Logs --> Filebeat;
    Filebeat --> ELK_Stack;
    User -- Accesses --> App_Pods;
    ELK_Stack -- Monitoring --> Developer;
    Ansible -- Sets_Up --> Minikube & Docker;
